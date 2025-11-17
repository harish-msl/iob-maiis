"""
IOB MAIIS - Authentication Router
Complete authentication endpoints including signup, login, refresh, logout
JWT-based authentication with comprehensive security features

Created: 2025-01-17
Python: 3.12
FastAPI: 0.115.0
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, get_current_user
from app.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SignupRequest,
    UserResponse,
)
from app.core.cache import delete_cache, get_cache, set_cache
from app.core.config import settings
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User, UserRole

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user

    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, numbers, special chars)
    - **full_name**: User's full name
    - **phone**: Optional phone number

    Returns the created user information (without password)
    """
    try:
        # Validate password strength
        is_valid, message = validate_password_strength(signup_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == signup_data.email.lower())
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"Signup attempt with existing email: {signup_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = get_password_hash(signup_data.password)
        new_user = User(
            email=signup_data.email.lower(),
            hashed_password=hashed_password,
            full_name=signup_data.full_name,
            phone=signup_data.phone,
            role=UserRole.USER,
            is_active=True,
            is_verified=False,  # Email verification can be implemented
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"✅ New user registered: {new_user.email} (ID: {new_user.id})")

        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            phone=new_user.phone,
            avatar_url=new_user.avatar_url,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account",
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return access and refresh tokens

    - **email**: User's email address
    - **password**: User's password

    Returns:
    - **access_token**: JWT access token (expires in 30 minutes)
    - **refresh_token**: JWT refresh token (expires in 7 days)
    - **token_type**: Bearer
    - **user**: User information
    """
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email.lower())
        )
        user = result.scalar_one_or_none()

        # Check if user exists and password is correct
        if not user or not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Create tokens
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Store refresh token in cache
        await set_cache(
            f"refresh_token:{user.id}",
            refresh_token,
            expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        logger.info(f"✅ User logged in: {user.email} (ID: {user.id})")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                phone=user.phone,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens
    """
    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Verify refresh token in cache
        cached_token = await get_cache(f"refresh_token:{user_id}")
        if not cached_token or cached_token != refresh_data.refresh_token:
            logger.warning(f"Invalid refresh token for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        # Get user
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new tokens
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        # Update refresh token in cache
        await delete_cache(f"refresh_token:{user.id}")
        await set_cache(
            f"refresh_token:{user.id}",
            new_refresh_token,
            expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        logger.info(f"✅ Token refreshed for user: {user.email} (ID: {user.id})")

        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """
    Logout current user

    Revokes refresh token and invalidates session
    Requires valid access token
    """
    try:
        # Delete refresh token from cache
        await delete_cache(f"refresh_token:{current_user.id}")

        # Optionally: Add access token to blacklist
        # This would require maintaining a blacklist of tokens until they expire

        logger.info(f"✅ User logged out: {current_user.email} (ID: {current_user.id})")

        return {
            "message": "Successfully logged out",
            "user_id": current_user.id,
        }

    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user information

    Requires valid access token
    Returns complete user profile
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    bio: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile

    - **full_name**: Updated full name (optional)
    - **phone**: Updated phone number (optional)
    - **bio**: Updated bio/description (optional)
    - **avatar_url**: Updated avatar URL (optional)

    Returns updated user information
    """
    try:
        # Update fields if provided
        if full_name is not None:
            current_user.full_name = full_name
        if phone is not None:
            current_user.phone = phone
        if bio is not None:
            current_user.bio = bio
        if avatar_url is not None:
            current_user.avatar_url = avatar_url

        current_user.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(current_user)

        logger.info(
            f"✅ User profile updated: {current_user.email} (ID: {current_user.id})"
        )

        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            phone=current_user.phone,
            avatar_url=current_user.avatar_url,
            bio=current_user.bio,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            last_login=current_user.last_login,
        )

    except Exception as e:
        logger.error(f"❌ Profile update error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password

    - **current_password**: Current password for verification
    - **new_password**: New password (must meet security requirements)

    Returns success message
    """
    try:
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Validate new password
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # Update password
        current_user.hashed_password = get_password_hash(new_password)
        current_user.updated_at = datetime.utcnow()

        await db.commit()

        # Revoke all refresh tokens
        await delete_cache(f"refresh_token:{current_user.id}")

        logger.info(
            f"✅ Password changed for user: {current_user.email} (ID: {current_user.id})"
        )

        return {
            "message": "Password changed successfully",
            "user_id": current_user.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Password change error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )
