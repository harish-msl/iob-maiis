"""
Authentication Schemas
Pydantic models for request/response validation in auth endpoints
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# ============================================================================
# Request Schemas
# ============================================================================


class SignupRequest(BaseModel):
    """User registration request"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=100, description="User password (min 8 chars)"
    )
    full_name: str = Field(
        ..., min_length=2, max_length=100, description="User full name"
    )
    phone: Optional[str] = Field(
        None, max_length=20, description="Phone number (optional)"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate full name"""
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v is None:
            return v
        # Remove common separators
        cleaned = v.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Phone number must contain only digits and '+' sign")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "password": "SecurePass123!",
                    "full_name": "John Doe",
                    "phone": "+1234567890",
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    """User login request"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "john.doe@example.com", "password": "SecurePass123!"}
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str = Field(..., description="Valid refresh token")

    model_config = {
        "json_schema_extra": {
            "examples": [{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]
        }
    }


class ChangePasswordRequest(BaseModel):
    """Change password request"""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password (min 8 chars)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "OldPass123!",
                    "new_password": "NewSecurePass456!",
                }
            ]
        }
    }


class UpdateProfileRequest(BaseModel):
    """Update user profile request"""

    full_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="User full name"
    )
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name"""
        if v is not None:
            if not v.strip():
                raise ValueError("Full name cannot be empty")
            if len(v.strip()) < 2:
                raise ValueError("Full name must be at least 2 characters")
            return v.strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v is not None:
            cleaned = (
                v.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            )
            if not cleaned.replace("+", "").isdigit():
                raise ValueError("Phone number must contain only digits and '+' sign")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{"full_name": "John Smith", "phone": "+1234567890"}]
        }
    }


# ============================================================================
# Response Schemas
# ============================================================================


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """User response"""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Account active status")
    is_superuser: bool = Field(..., description="Superuser status")
    email_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "john.doe@example.com",
                    "full_name": "John Doe",
                    "phone": "+1234567890",
                    "role": "customer",
                    "is_active": True,
                    "is_superuser": False,
                    "email_verified": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    }


class LoginResponse(BaseModel):
    """Login response with user and tokens"""

    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": {
                        "id": 1,
                        "email": "john.doe@example.com",
                        "full_name": "John Doe",
                        "phone": "+1234567890",
                        "role": "customer",
                        "is_active": True,
                        "is_superuser": False,
                        "email_verified": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                    },
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                }
            ]
        }
    }


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "Operation completed successfully", "success": True}
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response"""

    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Error code")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Invalid credentials",
                    "error_code": "AUTH_INVALID_CREDENTIALS",
                }
            ]
        }
    }


# ============================================================================
# Internal Schemas (for service layer)
# ============================================================================


class TokenPayload(BaseModel):
    """JWT token payload"""

    sub: str = Field(..., description="Subject (user ID)")
    type: str = Field(..., description="Token type (access/refresh)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")


class UserCreate(BaseModel):
    """Internal schema for creating users"""

    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "customer"
    is_active: bool = True
    is_superuser: bool = False
    email_verified: bool = False


class UserUpdate(BaseModel):
    """Internal schema for updating users"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserInDB(UserResponse):
    """User schema including hashed password (for internal use only)"""

    hashed_password: str = Field(..., description="Hashed password")

    model_config = {"from_attributes": True}
