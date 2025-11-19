"""
Chat API Router
Handles AI chat interactions with RAG (Retrieval-Augmented Generation)
"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.services.rag_service import get_rag_service

router = APIRouter(prefix="/chat", tags=["chat"])

# ============================================================================
# Schemas
# ============================================================================


class ChatMessage(BaseModel):
    """Chat message schema"""

    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")

    model_config = {
        "json_schema_extra": {
            "examples": [{"role": "user", "content": "How do I apply for a loan?"}]
        }
    }


class IngestRequest(BaseModel):
    """Request schema for document ingestion"""

    text: str = Field(..., description="Document text to ingest")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata (type, category, etc.)"
    )
    chunk_size: int = Field(500, description="Chunk size in characters")
    chunk_overlap: int = Field(50, description="Overlap between chunks")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Long policy document about loans...",
                    "metadata": {"type": "policy", "category": "loans"},
                    "chunk_size": 500,
                    "chunk_overlap": 50,
                }
            ]
        }
    }


class ChatRequest(BaseModel):
    """Chat request with message and optional context"""

    message: str = Field(..., min_length=1, description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        None, description="Previous conversation history"
    )
    use_context: bool = Field(True, description="Whether to use RAG context retrieval")
    stream: bool = Field(False, description="Whether to stream the response")
    temperature: float = Field(
        0.7, ge=0.0, le=1.0, description="LLM temperature (0.0 to 1.0)"
    )
    top_k: int = Field(
        5, ge=1, le=20, description="Number of context documents to retrieve"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata filters for context retrieval"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "What are the interest rates for savings accounts?",
                    "use_context": True,
                    "temperature": 0.7,
                    "top_k": 5,
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Chat response with AI message and metadata"""

    response: str = Field(..., description="AI assistant response")
    context_used: bool = Field(..., description="Whether context was used")
    num_context_docs: int = Field(0, description="Number of context documents used")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "Our savings accounts offer competitive interest rates...",
                    "context_used": True,
                    "num_context_docs": 3,
                }
            ]
        }
    }


class ChatHistoryResponse(BaseModel):
    """Chat history response"""

    conversations: List[Dict[str, Any]] = Field(
        ..., description="List of conversations"
    )
    total: int = Field(..., description="Total number of conversations")


class StreamChunk(BaseModel):
    """Streaming response chunk"""

    content: str = Field(..., description="Text chunk")
    done: bool = Field(False, description="Whether streaming is complete")


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Send a message to the AI assistant and get a response

    This endpoint uses RAG (Retrieval-Augmented Generation) to provide
    context-aware responses based on the banking knowledge base.

    Args:
        request: Chat request with message and optional settings
        current_user: Authenticated user
        db: Database session

    Returns:
        ChatResponse with AI response and metadata

    Example:
        ```
        POST /api/chat/message
        {
            "message": "How do I open a checking account?",
            "use_context": true,
            "temperature": 0.7
        }
        ```
    """
    try:
        logger.info(f"User {current_user.id} sent message: {request.message[:100]}...")

        # Get RAG service
        rag_service = get_rag_service()

        # Convert conversation history to proper format
        messages = []
        if request.conversation_history:
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]

        # Add current user message
        messages.append({"role": "user", "content": request.message})

        # Generate response with RAG
        if request.use_context:
            result = await rag_service.generate_response(
                query=request.message,
                top_k=request.top_k,
                filters=request.filters,
                conversation_history=messages[:-1],  # Exclude current message
                temperature=request.temperature,
            )

            response = ChatResponse(
                response=result["response"],
                context_used=True,
                num_context_docs=result["num_context_docs"],
            )
        else:
            # Use chat without context retrieval
            from app.services.llm_service import get_llm_service

            llm_service = get_llm_service()
            response_text = await llm_service.chat(
                messages=messages, temperature=request.temperature
            )

            response = ChatResponse(
                response=response_text,
                context_used=False,
                num_context_docs=0,
            )

        logger.info(f"Generated response for user {current_user.id}")
        return response

    except Exception as e:
        logger.error(f"Chat message failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}",
        )


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Stream AI response in real-time

    This endpoint streams the response chunk by chunk using Server-Sent Events (SSE).

    Args:
        request: Chat request
        current_user: Authenticated user

    Returns:
        StreamingResponse with text chunks

    Example:
        ```
        POST /api/chat/stream
        {
            "message": "Explain different types of bank accounts",
            "use_context": true
        }
        ```
    """
    from fastapi.responses import StreamingResponse

    async def generate():
        try:
            logger.info(
                f"User {current_user.id} requested streaming response: {request.message[:100]}..."
            )

            # Get RAG service
            rag_service = get_rag_service()

            # Convert conversation history
            messages = []
            if request.conversation_history:
                messages = [
                    {"role": msg.role, "content": msg.content}
                    for msg in request.conversation_history
                ]

            # Add current message
            messages.append({"role": "user", "content": request.message})

            # Stream response
            if request.use_context:
                async for chunk in rag_service.generate_response_stream(
                    query=request.message,
                    top_k=request.top_k,
                    filters=request.filters,
                    conversation_history=messages[:-1],
                    temperature=request.temperature,
                ):
                    yield f"data: {chunk}\n\n"
            else:
                from app.services.llm_service import get_llm_service

                llm_service = get_llm_service()
                async for chunk in llm_service.chat_stream(
                    messages=messages, temperature=request.temperature
                ):
                    yield f"data: {chunk}\n\n"

            # Send completion signal
            yield "data: [DONE]\n\n"

            logger.info(f"Completed streaming response for user {current_user.id}")

        except Exception as e:
            logger.error(f"Streaming failed: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time bidirectional chat

    This allows for persistent connections and real-time messaging.

    Connection format:
        - Send: {"message": "your message", "use_context": true}
        - Receive: {"response": "AI response", "done": true}

    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/chat/ws?token=YOUR_JWT_TOKEN');
        ws.send(JSON.stringify({
            message: "What is a mortgage?",
            use_context: true
        }));
        ```
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        # Get RAG service
        rag_service = get_rag_service()

        while True:
            # Receive message
            data = await websocket.receive_json()

            message = data.get("message", "")
            use_context = data.get("use_context", True)
            temperature = data.get("temperature", 0.7)
            top_k = data.get("top_k", 5)

            if not message:
                await websocket.send_json({"error": "Message cannot be empty"})
                continue

            logger.info(f"WebSocket received: {message[:100]}...")

            try:
                # Stream response back through WebSocket
                if use_context:
                    async for chunk in rag_service.generate_response_stream(
                        query=message, temperature=temperature, top_k=top_k
                    ):
                        await websocket.send_json({"response": chunk, "done": False})
                else:
                    from app.services.llm_service import get_llm_service

                    llm_service = get_llm_service()
                    async for chunk in llm_service.stream(
                        prompt=message, temperature=temperature
                    ):
                        await websocket.send_json({"response": chunk, "done": False})

                # Send completion signal
                await websocket.send_json({"response": "", "done": True})

            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.close()
        except:
            pass


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ChatHistoryResponse:
    """
    Get chat conversation history for current user

    Args:
        limit: Maximum number of conversations to return
        offset: Offset for pagination
        current_user: Authenticated user
        db: Database session

    Returns:
        ChatHistoryResponse with conversations

    Note:
        This is a placeholder. Implement actual conversation storage
        in a ChatConversation model if needed.
    """
    try:
        # TODO: Implement conversation storage in database
        # For now, return empty history
        logger.info(f"Fetching chat history for user {current_user.id}")

        return ChatHistoryResponse(conversations=[], total=0)

    except Exception as e:
        logger.error(f"Failed to fetch chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history",
        )


@router.delete("/clear")
async def clear_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Clear chat history for current user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    try:
        # TODO: Implement conversation clearing when storage is implemented
        logger.info(f"Clearing chat history for user {current_user.id}")

        return {"message": "Chat history cleared successfully"}

    except Exception as e:
        logger.error(f"Failed to clear chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history",
        )


@router.get("/health")
async def check_health() -> Dict[str, Any]:
    """
    Check health of chat service components

    Returns:
        Health status of RAG pipeline, LLM, and vector database
    """
    try:
        rag_service = get_rag_service()
        health_status = await rag_service.check_health()

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


@router.post("/ingest")
async def ingest_document(
    request: IngestRequest,
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Ingest a document into the RAG knowledge base

    This endpoint is restricted to admin users for adding documents
    to the vector database.

    Args:
        request: Document ingestion request
        current_user: Authenticated user (must be admin)

    Returns:
        Document IDs and ingestion status

    Example:
        ```
        POST /api/chat/ingest
        {
            "text": "Long policy document about loans...",
            "metadata": {"type": "policy", "category": "loans"},
            "chunk_size": 500,
            "chunk_overlap": 50
        }
        ```
    """
    try:
        # Check if user is admin
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can ingest documents",
            )

        logger.info(f"Admin {current_user.id} ingesting document (length: {len(text)})")

        # Get RAG service
        rag_service = get_rag_service()

        # Ingest document
        result = await rag_service.ingest_document(
            text=request.text,
            metadata=request.metadata or {},
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        return {
            "message": "Document ingested successfully",
            "document_ids": doc_ids,
            "num_chunks": len(doc_ids),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document ingestion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        )
