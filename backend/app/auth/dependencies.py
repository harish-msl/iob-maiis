"""
Authentication Dependencies
Provides JWT token validation and user authentication dependencies
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User

settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate JWT token and return current user

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode and verify token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Extract user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Verify token type
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if current user is active

    Args:
        current_user: Current authenticated user

    Returns:
        User: Active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Check if current user is a superuser

    Args:
        current_user: Current active user

    Returns:
        User: Superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based access control

    Args:
        *allowed_roles: Roles that are allowed to access the endpoint

    Returns:
        Dependency function that checks user role

    Example:
        @router.get("/admin", dependencies=[Depends(require_role("admin", "manager"))])
        async def admin_endpoint():
            ...
    """

    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' not authorized. Required: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work with or without authentication

    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session

    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        token_type: str = payload.get("type")
        if token_type != "access":
            return None

        user = db.query(User).filter(User.id == int(user_id)).first()
        return user

    except JWTError:
        return None


class RoleChecker:
    """
    Class-based role checker for dependency injection
    Provides a reusable way to check user roles

    Example:
        admin_required = RoleChecker(["admin"])

        @router.get("/admin", dependencies=[Depends(admin_required)])
        async def admin_endpoint():
            ...
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' not authorized. Required: {', '.join(self.allowed_roles)}",
            )
        return current_user


# Common role dependencies (ready to use)
admin_required = RoleChecker(["admin"])
manager_required = RoleChecker(["admin", "manager"])
staff_required = RoleChecker(["admin", "manager", "agent"])
customer_only = RoleChecker(["customer"])


async def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate refresh token and return user

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User: User from refresh token

    Raises:
        HTTPException: If refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user
