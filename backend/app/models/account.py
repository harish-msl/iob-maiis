"""
Account model
"""
import enum
from datetime import datetime
from decimal import Decimal
from typing import List

from app.db.session import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class AccountType(str, enum.Enum):
    """Account type enumeration"""
    SAVINGS = "savings"
    CHECKING = "checking"
    FIXED_DEPOSIT = "fixed_deposit"

class Account(Base):
    """Bank account model"""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0.00, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions_from: Mapped[List["Transaction"]] = relationship("Transaction", foreign_keys="Transaction.from_account_id", back_populates="from_account")
    transactions_to: Mapped[List["Transaction"]] = relationship("Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account")
