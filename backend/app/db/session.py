"""
IOB MAIIS - Database Session Management
SQLAlchemy async session configuration for PostgreSQL
Handles database connections, session lifecycle, and initialization

Created: 2025-01-17
Python: 3.12
SQLAlchemy: 2.0
"""

from typing import AsyncGenerator

from app.core.config import settings
from app.core.logging import logger
from sqlalchemy import MetaData, event, pool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr

# ============================================
# DATABASE ENGINE CONFIGURATION
# ============================================

# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENABLE_SQL_LOGGING,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using
    poolclass=pool.AsyncAdaptedQueuePool,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ============================================
# BASE MODEL
# ============================================

# Naming convention for constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models
    Provides common functionality and naming conventions
    """

    metadata = metadata

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name automatically from class name
        Converts CamelCase to snake_case
        """
        import re

        name = cls.__name__
        # Insert underscore before uppercase letters
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()

    def __repr__(self) -> str:
        """String representation of model instance"""
        columns = ", ".join(
            [
                f"{k}={repr(v)}"
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )
        return f"<{self.__class__.__name__}({columns})>"


# ============================================
# DATABASE EVENTS
# ============================================


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set database connection parameters"""
    if settings.ENVIRONMENT == "development":
        logger.debug("Database connection established")


@event.listens_for(engine.sync_engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when connection is returned to pool"""
    if settings.DEBUG and settings.ENABLE_SQL_LOGGING:
        logger.debug("Connection returned to pool")


@event.listens_for(engine.sync_engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when connection is checked out from pool"""
    if settings.DEBUG and settings.ENABLE_SQL_LOGGING:
        logger.debug("Connection checked out from pool")


# ============================================
# SESSION MANAGEMENT
# ============================================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    Automatically handles session lifecycle and rollback on errors

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


async def get_db_context():
    """
    Context manager for database session
    Use when dependency injection is not available

    Example:
        async with get_db_context() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database context error: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


# ============================================
# DATABASE INITIALIZATION
# ============================================


async def init_db() -> None:
    """
    Initialize database with default data
    Creates default users, roles, and sample data
    """
    from app.models.user import User, UserRole

    try:
        async with async_session() as session:
            # Check if admin user exists
            from sqlalchemy import select

            result = await session.execute(
                select(User).where(User.email == "admin@iobmaiis.local")
            )
            admin_user = result.scalar_one_or_none()

            if not admin_user:
                # Create admin user
                from app.core.security import get_password_hash

                admin_user = User(
                    email="admin@iobmaiis.local",
                    hashed_password=get_password_hash("Admin@123456"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True,
                )
                session.add(admin_user)
                logger.info("Created admin user")

            # Create demo user
            result = await session.execute(
                select(User).where(User.email == "demo@iobmaiis.local")
            )
            demo_user = result.scalar_one_or_none()

            if not demo_user:
                from app.core.security import get_password_hash

                demo_user = User(
                    email="demo@iobmaiis.local",
                    hashed_password=get_password_hash("Demo@123456"),
                    full_name="Demo User",
                    role=UserRole.USER,
                    is_active=True,
                    is_verified=True,
                )
                session.add(demo_user)
                logger.info("Created demo user")

            await session.commit()
            logger.info("✅ Database initialization completed")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}", exc_info=True)
        raise


async def check_db_connection() -> bool:
    """
    Check if database connection is working

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}", exc_info=True)
        return False


async def create_tables() -> None:
    """
    Create all database tables
    Only used in development/testing
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}", exc_info=True)
        raise


async def drop_tables() -> None:
    """
    Drop all database tables
    WARNING: This will delete all data!
    Only used in development/testing
    """
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop tables in production!")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("⚠️  All database tables dropped")
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {str(e)}", exc_info=True)
        raise


# ============================================
# DATABASE UTILITIES
# ============================================


async def get_db_session() -> AsyncSession:
    """
    Get a new database session
    Caller is responsible for closing the session

    Returns:
        AsyncSession: New database session
    """
    return async_session()


async def execute_raw_sql(sql: str, params: dict = None) -> None:
    """
    Execute raw SQL query
    Use with caution - prefer ORM queries when possible

    Args:
        sql: SQL query string
        params: Optional query parameters

    Example:
        await execute_raw_sql(
            "UPDATE users SET is_active = :active WHERE id = :id",
            {"active": True, "id": 1}
        )
    """
    async with async_session() as session:
        try:
            await session.execute(sql, params or {})
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Raw SQL execution failed: {str(e)}", exc_info=True)
            raise


# ============================================
# EXPORTS
# ============================================

__all__ = [
    "Base",
    "engine",
    "async_session",
    "get_db",
    "get_db_context",
    "init_db",
    "check_db_connection",
    "create_tables",
    "drop_tables",
    "get_db_session",
    "execute_raw_sql",
]
