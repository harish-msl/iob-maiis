"""
Document model
"""
import enum
from datetime import datetime
from typing import Optional

from app.db.session import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    WORD = "word"
    EXCEL = "excel"

class Document(Base):
    """Document model"""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_indexed: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
