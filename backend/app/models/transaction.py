"""
Transaction model
"""
import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.db.session import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(Base):
    """Transaction model"""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)

    from_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("account.id"), nullable=True)
    to_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("account.id"), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=True)
    reference_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    from_account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[from_account_id], back_populates="transactions_from")
    to_account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[to_account_id], back_populates="transactions_to")
