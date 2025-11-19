"""
Document Management API
Handles document upload, OCR processing, and knowledge base ingestion
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.services.ocr_service import get_ocr_service
from app.services.rag_service import get_rag_service
from app.services.storage_service import get_storage_service

router = APIRouter(prefix="/documents", tags=["documents"])

# ============================================================================
# Schemas
# ============================================================================


class DocumentUploadResponse(BaseModel):
    """Document upload response"""

    id: int
    filename: str
    file_type: str
    file_size: int
    uploaded_at: str
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "filename": "policy_document.pdf",
                    "file_type": "application/pdf",
                    "file_size": 524288,
                    "uploaded_at": "2024-01-15T10:30:00Z",
                    "message": "Document uploaded successfully",
                }
            ]
        }
    }


class OCRRequest(BaseModel):
    """OCR processing request"""

    document_id: Optional[int] = Field(None, description="Document ID from database")
    base64_data: Optional[str] = Field(None, description="Base64 encoded image data")
    language: str = Field("eng", description="OCR language code")
    preprocess: bool = Field(True, description="Apply image preprocessing")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_id": 1,
                    "language": "eng",
                    "preprocess": True,
                }
            ]
        }
    }


class OCRResponse(BaseModel):
    """OCR processing response"""

    text: str = Field(..., description="Extracted text")
    confidence: float = Field(..., description="Average confidence score")
    word_count: int = Field(..., description="Number of words extracted")
    language: str = Field(..., description="Language used for OCR")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "This is the extracted text from the document...",
                    "confidence": 95.5,
                    "word_count": 423,
                    "language": "eng",
                    "processing_time": 2.34,
                }
            ]
        }
    }


class DocumentResponse(BaseModel):
    """Document response"""

    id: int
    user_id: int
    filename: str
    file_type: str
    file_size: int
    file_path: str
    extracted_text: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "filename": "contract.pdf",
                    "file_type": "application/pdf",
                    "file_size": 524288,
                    "file_path": "/uploads/user_1/contract.pdf",
                    "extracted_text": "Contract text...",
                    "metadata": {"pages": 5, "ocr_processed": True},
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    }


class IngestDocumentRequest(BaseModel):
    """Request to ingest document into knowledge base"""

    document_id: int = Field(..., description="Document ID")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for knowledge base"
    )
    chunk_size: int = Field(500, description="Chunk size for text splitting")
    chunk_overlap: int = Field(50, description="Overlap between chunks")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_id": 1,
                    "metadata": {"type": "policy", "category": "loans"},
                    "chunk_size": 500,
                }
            ]
        }
    }


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    process_ocr: bool = Query(False, description="Automatically process with OCR"),
    ingest_to_kb: bool = Query(False, description="Ingest to knowledge base"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Upload a document (PDF, image, etc.)

    Args:
        file: File to upload
        process_ocr: If true, automatically extract text with OCR
        ingest_to_kb: If true, add to RAG knowledge base (requires admin)
        current_user: Authenticated user
        db: Database session

    Returns:
        Document upload response with ID

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/documents/upload" \
          -H "Authorization: Bearer YOUR_TOKEN" \
          -F "file=@document.pdf" \
          -F "process_ocr=true"
        ```
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided",
            )

        # Check file size (max 10MB for now)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        file_size = len(content)

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {max_size / 1024 / 1024}MB",
            )

        logger.info(
            f"User {current_user.id} uploading document: {file.filename} ({file_size} bytes)"
        )

        # Upload to storage (MinIO/S3)
        try:
            storage_service = get_storage_service()
            upload_result = await storage_service.upload_document(
                file_data=content,
                filename=file.filename,
                user_id=current_user.id,
                content_type=file.content_type,
                metadata={"uploaded_at": datetime.utcnow().isoformat()},
            )

            file_path = upload_result["object_name"]
            storage_url = upload_result["url"]

            logger.info(f"File uploaded to storage: {storage_url}")

        except Exception as e:
            logger.error(f"Storage upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Storage upload failed: {str(e)}",
            )

        # Create document record
        document = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            file_path=file_path,
        )

        # Process OCR if requested
        if process_ocr:
            try:
                ocr_service = get_ocr_service()

                # Determine file type and process accordingly
                if file.content_type == "application/pdf":
                    result = await ocr_service.process_pdf(content)
                    document.extracted_text = result["full_text"]
                    document.metadata = {
                        "pages": result["page_count"],
                        "avg_confidence": result["avg_confidence"],
                        "ocr_processed": True,
                    }
                elif file.content_type and file.content_type.startswith("image/"):
                    result = await ocr_service.process_image(content)
                    document.extracted_text = result["text"]
                    document.metadata = {
                        "confidence": result["confidence"],
                        "ocr_processed": True,
                    }

                logger.info(f"OCR processed document: {file.filename}")
            except Exception as e:
                logger.warning(f"OCR processing failed: {str(e)}")
                # Continue with upload even if OCR fails

        db.add(document)
        db.commit()
        db.refresh(document)

        # Ingest to knowledge base if requested and user is admin
        if ingest_to_kb and document.extracted_text:
            if not current_user.is_superuser:
                logger.warning(
                    f"User {current_user.id} attempted to ingest without admin rights"
                )
            else:
                try:
                    rag_service = get_rag_service()
                    await rag_service.ingest_document(
                        text=document.extracted_text,
                        metadata={
                            "document_id": document.id,
                            "filename": document.filename,
                            "user_id": current_user.id,
                        },
                    )
                    logger.info(f"Document {document.id} ingested to knowledge base")
                except Exception as e:
                    logger.error(f"Failed to ingest to knowledge base: {str(e)}")

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            uploaded_at=document.created_at.isoformat(),
            message="Document uploaded successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    request: OCRRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> OCRResponse:
    """
    Process document with OCR to extract text

    Args:
        request: OCR request with document ID or base64 data
        current_user: Authenticated user
        db: Database session

    Returns:
        Extracted text and metadata

    Example:
        ```
        POST /api/documents/ocr
        {
            "document_id": 1,
            "language": "eng",
            "preprocess": true
        }
        ```
    """
    import time

    try:
        start_time = time.time()

        ocr_service = get_ocr_service()

        # Get document data
        if request.document_id:
            # Load from database
            document = (
                db.query(Document)
                .filter(
                    Document.id == request.document_id,
                    Document.user_id == current_user.id,
                )
                .first()
            )

            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found",
                )

            # TODO: Load actual file content from storage
            # For now, return error if no base64 data
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document storage not yet implemented. Use base64_data instead.",
            )

        elif request.base64_data:
            # Use provided base64 data
            try:
                image_data = base64.b64decode(request.base64_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid base64 data: {str(e)}",
                )

            # Preprocess if requested
            if request.preprocess:
                image_data = await ocr_service.preprocess_image(image_data)

            # Process with OCR
            result = await ocr_service.process_image(
                image_data=image_data,
                language=request.language,
            )

            processing_time = time.time() - start_time

            return OCRResponse(
                text=result["text"],
                confidence=result["confidence"],
                word_count=result["word_count"],
                language=result["language"],
                processing_time=round(processing_time, 2),
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either document_id or base64_data must be provided",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        )


@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Document]:
    """
    Get list of documents for current user

    Args:
        limit: Maximum number of documents to return
        offset: Offset for pagination
        current_user: Authenticated user
        db: Database session

    Returns:
        List of documents
    """
    try:
        documents = (
            db.query(Document)
            .filter(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return documents

    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents",
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Document:
    """
    Get document details by ID

    Args:
        document_id: Document ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Document details
    """
    try:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id,
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch document",
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Delete a document

    Args:
        document_id: Document ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    try:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id,
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        logger.info(
            f"User {current_user.id} deleting document {document_id}: {document.filename}"
        )

        # TODO: Delete actual file from storage
        # For now, just delete database record
        db.delete(document)
        db.commit()

        return {"message": f"Document {document.filename} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )


@router.post("/ingest")
async def ingest_to_knowledge_base(
    request: IngestDocumentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ingest document text into RAG knowledge base (Admin only)

    Args:
        request: Ingest request
        current_user: Authenticated user (must be admin)
        db: Database session

    Returns:
        Ingestion result with document IDs

    Raises:
        403: If user is not an admin
        404: If document not found
    """
    try:
        # Check admin permission
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can ingest documents to knowledge base",
            )

        # Get document
        document = db.query(Document).filter(Document.id == request.document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if not document.extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no extracted text. Process with OCR first.",
            )

        logger.info(
            f"Admin {current_user.id} ingesting document {request.document_id} to knowledge base"
        )

        # Prepare metadata
        metadata = request.metadata or {}
        metadata.update(
            {
                "document_id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
            }
        )

        # Ingest to RAG
        rag_service = get_rag_service()
        doc_ids = await rag_service.ingest_document(
            text=document.extracted_text,
            metadata=metadata,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        # Update document metadata
        if not document.metadata:
            document.metadata = {}
        document.metadata["ingested_to_kb"] = True
        document.metadata["vector_ids"] = doc_ids
        db.commit()

        return {
            "message": "Document ingested to knowledge base successfully",
            "document_id": document.id,
            "vector_ids": doc_ids,
            "num_chunks": len(doc_ids),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        )
