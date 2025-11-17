#!/usr/bin/env python3
"""
IOB MAIIS - File Generation Script
Generates all remaining project files automatically
Created: 2025-01-17
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent


def create_file(path: str, content: str):
    """Create a file with given content"""
    file_path = BASE_DIR / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    print(f"✅ Created: {path}")


def generate_files():
    """Generate all project files"""

    # ============================================
    # BACKEND FILES
    # ============================================

    # backend/app/core/__init__.py
    create_file(
        "backend/app/core/__init__.py",
        '''"""Core configuration and utilities"""
from app.core.config import settings
from app.core.logging import logger

__all__ = ["settings", "logger"]
''',
    )

    # backend/app/core/security.py
    create_file(
        "backend/app/core/security.py",
        '''"""
Security utilities for password hashing, JWT tokens, etc.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.core.config import settings
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements"""
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters"

    if settings.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if settings.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if settings.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    if settings.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"
''',
    )

    # backend/app/core/cache.py
    create_file(
        "backend/app/core/cache.py",
        '''"""
Redis cache management
"""
import json
from typing import Any, Optional

import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
    socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
)

async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

async def set_cache(key: str, value: Any, expire: int = None) -> bool:
    """Set value in cache"""
    try:
        serialized = json.dumps(value)
        if expire:
            await redis_client.setex(key, expire, serialized)
        else:
            await redis_client.set(key, serialized)
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False

async def delete_cache(key: str) -> bool:
    """Delete key from cache"""
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False

async def clear_cache_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            return await redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Cache clear pattern error: {e}")
        return 0
''',
    )

    # backend/app/db/__init__.py
    create_file(
        "backend/app/db/__init__.py",
        '''"""Database package"""
from app.db.session import Base, async_session, engine, get_db

__all__ = ["Base", "engine", "async_session", "get_db"]
''',
    )

    # backend/app/db/base.py
    create_file(
        "backend/app/db/base.py",
        '''"""
Import all models here for Alembic migrations
"""
from app.db.session import Base
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.document import Document

__all__ = ["Base", "User", "Account", "Transaction", "Document"]
''',
    )

    # backend/app/models/__init__.py
    create_file(
        "backend/app/models/__init__.py",
        '''"""Database models"""
from app.models.user import User, UserRole
from app.models.account import Account, AccountType
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.document import Document, DocumentType

__all__ = [
    "User", "UserRole",
    "Account", "AccountType",
    "Transaction", "TransactionType", "TransactionStatus",
    "Document", "DocumentType"
]
''',
    )

    # backend/app/models/user.py
    create_file(
        "backend/app/models/user.py",
        '''"""
User model
"""
import enum
from datetime import datetime
from typing import List

from app.db.session import Base
from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"

class User(Base):
    """User model"""

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
''',
    )

    # backend/app/models/account.py
    create_file(
        "backend/app/models/account.py",
        '''"""
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
''',
    )

    # backend/app/models/transaction.py
    create_file(
        "backend/app/models/transaction.py",
        '''"""
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
''',
    )

    # backend/app/models/document.py
    create_file(
        "backend/app/models/document.py",
        '''"""
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
''',
    )

    print("\n✅ All files generated successfully!")
    print("\nNext steps:")
    print("1. Run: chmod +x setup.sh")
    print("2. Run: ./setup.sh")
    print("3. Or manually: docker-compose up -d")


if __name__ == "__main__":
    print("🚀 IOB MAIIS - File Generation Script")
    print("=" * 60)
    generate_files()
