"""
IOB MAIIS - Main Application Entry Point
Multimodal AI-Enabled Information System
FastAPI Backend Application

Created: 2025-01-17
Python: 3.12
FastAPI: 0.115.0
"""

import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.api.banking import router as banking_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.voice import router as voice_router
from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.logging import logger
from app.db.session import Base, engine, init_db

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTIVE_REQUESTS = Counter("http_requests_active", "Active HTTP requests")

ERROR_COUNT = Counter(
    "http_errors_total", "Total HTTP errors", ["method", "endpoint", "error_type"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 Starting IOB MAIIS - Multimodal AI-Enabled Information System")
    logger.info("=" * 80)
    logger.info(f"📦 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🐍 Python: 3.12")
    logger.info(f"⚡ FastAPI: 0.115.0")
    logger.info(f"🗄️  Database: PostgreSQL 16")
    logger.info(f"🔍 Vector DB: Qdrant")
    logger.info(f"💾 Cache: Redis 7.2")
    logger.info(f"🤖 LLM: {settings.LLM_MODEL}")
    logger.info("=" * 80)

    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")

        # Initialize database with default data
        await init_db()
        logger.info("✅ Database initialized with default data")

        # Test Redis connection
        logger.info("🔗 Testing Redis connection...")
        from app.core.cache import redis_client

        await redis_client.ping()
        logger.info("✅ Redis connection established")

        # Test Qdrant connection
        logger.info("🔗 Testing Qdrant connection...")
        from app.services.embedding_service import embedding_service

        await embedding_service.initialize()
        logger.info("✅ Qdrant connection established")

        logger.info("=" * 80)
        logger.info("✅ IOB MAIIS started successfully!")
        logger.info(f"📚 API Docs: http://localhost:8000/api/docs")
        logger.info(f"🔍 Health Check: http://localhost:8000/health")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("=" * 80)
    logger.info("👋 Shutting down IOB MAIIS...")
    logger.info("=" * 80)

    try:
        # Close database connections
        await engine.dispose()
        logger.info("✅ Database connections closed")

        # Close Redis connections
        from app.core.cache import redis_client

        await redis_client.close()
        logger.info("✅ Redis connections closed")

        logger.info("=" * 80)
        logger.info("✅ Cleanup completed successfully")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Shutdown error: {str(e)}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title="IOB MAIIS API",
    description="""
    **Multimodal AI-Enabled Information System**

    Enterprise-grade banking AI assistant with:
    - 🤖 RAG-powered conversational AI
    - 💬 Multimodal interactions (text, voice, images)
    - 🏦 Complete banking operations
    - 🔒 Enterprise security
    - 📊 Real-time analytics

    Built with FastAPI, PostgreSQL, Qdrant, and Ollama.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "IOB MAIIS Team",
        "email": "support@iobmaiis.local",
        "url": "https://github.com/yourusername/iob-maiis",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"],
)

# GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host Middleware (Production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.yourdomain.com", "yourdomain.com", "localhost"],
    )


# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable):
    """Add unique request ID to each request"""
    import uuid

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Logging and Metrics Middleware
@app.middleware("http")
async def log_requests_and_metrics(request: Request, call_next: Callable):
    """Log all requests and collect metrics"""
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    # Log incoming request
    logger.info(
        f"📥 [{request_id[:8]}] {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    try:
        # Process request
        response = await call_next(request)
        process_time = time.time() - start_time

        # Update metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method, endpoint=request.url.path
        ).observe(process_time)

        # Add process time header
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Log response
        log_level = "info" if response.status_code < 400 else "warning"
        getattr(logger, log_level)(
            f"📤 [{request_id[:8]}] {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.4f}s",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time

        # Update error metrics
        ERROR_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            error_type=type(e).__name__,
        ).inc()

        # Log error
        logger.error(
            f"❌ [{request_id[:8]}] {request.method} {request.url.path} "
            f"Error: {str(e)} Time: {process_time:.4f}s",
            exc_info=True,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "process_time": process_time,
            },
        )
        raise


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"⚠️  [{request_id[:8]}] Validation error: {exc.errors()}",
        extra={"request_id": request_id, "errors": exc.errors(), "body": str(exc.body)},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body, "request_id": request_id},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"⚠️  [{request_id[:8]}] HTTP {exc.status_code}: {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"❌ [{request_id[:8]}] Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
            "error_type": type(exc).__name__ if settings.DEBUG else None,
        },
    )


# Include API routers
app.include_router(auth_router, prefix="/api", tags=["🔐 Authentication"])
app.include_router(chat_router, prefix="/api", tags=["💬 AI Chat"])
app.include_router(banking_router, prefix="/api", tags=["🏦 Banking"])
app.include_router(documents_router, prefix="/api", tags=["📄 Documents"])
app.include_router(voice_router, prefix="/api", tags=["🎤 Voice"])


# Root endpoints
@app.get("/", tags=["🏠 Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "message": "IOB MAIIS - Multimodal AI-Enabled Information System",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc",
            "openapi": "/api/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "auth": "/api/auth",
            "chat": "/api/chat",
            "banking": "/api/banking",
            "documents": "/api/documents",
            "voice": "/api/voice",
        },
    }


@app.get("/health", tags=["🏥 Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        from app.db.session import async_session

        async with async_session() as session:
            await session.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    try:
        # Check Redis
        from app.core.cache import redis_client

        await redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"

    try:
        # Check Qdrant
        from app.services.embedding_service import embedding_service

        await embedding_service.health_check()
        qdrant_status = "healthy"
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        qdrant_status = "unhealthy"

    overall_healthy = all(
        [db_status == "healthy", redis_status == "healthy", qdrant_status == "healthy"]
    )

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": time.time(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "qdrant": qdrant_status,
        },
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/metrics", tags=["📊 Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/info", tags=["ℹ️  Information"])
async def api_info():
    """API information and capabilities"""
    return {
        "name": "IOB MAIIS API",
        "version": "1.0.0",
        "description": "Multimodal AI-Enabled Information System",
        "capabilities": {
            "multimodal": {
                "text": True,
                "voice": settings.NEXT_PUBLIC_ENABLE_VOICE
                if hasattr(settings, "NEXT_PUBLIC_ENABLE_VOICE")
                else True,
                "images": settings.NEXT_PUBLIC_ENABLE_OCR
                if hasattr(settings, "NEXT_PUBLIC_ENABLE_OCR")
                else True,
                "documents": True,
            },
            "ai_features": {
                "rag": True,
                "chat": True,
                "semantic_search": True,
                "document_analysis": True,
                "ocr": True,
                "speech_to_text": True,
            },
            "banking_features": {
                "accounts": True,
                "transactions": True,
                "transfers": True,
                "balance_inquiry": True,
                "transaction_history": True,
                "fraud_detection": settings.ENABLE_FRAUD_DETECTION
                if hasattr(settings, "ENABLE_FRAUD_DETECTION")
                else True,
            },
        },
        "models": {
            "llm": settings.LLM_MODEL,
            "embedding": settings.EMBEDDING_MODEL,
            "vision": settings.VISION_MODEL
            if hasattr(settings, "VISION_MODEL")
            else "llava:13b",
        },
        "rate_limits": {
            "per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "auth": settings.AUTH_RATE_LIMIT
            if hasattr(settings, "AUTH_RATE_LIMIT")
            else 5,
            "chat": settings.CHAT_RATE_LIMIT
            if hasattr(settings, "CHAT_RATE_LIMIT")
            else 30,
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting IOB MAIIS in development mode...")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        workers=1 if settings.DEBUG else 4,
    )
