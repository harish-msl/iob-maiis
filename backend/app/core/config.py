"""
IOB MAIIS - Core Configuration Module
Environment-based settings management using Pydantic
Supports development, staging, and production environments

Created: 2025-01-17
Python: 3.12
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    APP_NAME: str = Field(default="IOB MAIIS", description="Application name")
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, production",
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ============================================
    # SECURITY & AUTHENTICATION
    # ============================================
    SECRET_KEY: str = Field(
        ..., min_length=32, description="Secret key for session encryption"
    )
    JWT_SECRET_KEY: str = Field(
        ..., min_length=32, description="JWT signing secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # Password Policy
    MIN_PASSWORD_LENGTH: int = Field(default=8, description="Minimum password length")
    REQUIRE_UPPERCASE: bool = Field(
        default=True, description="Require uppercase letters"
    )
    REQUIRE_LOWERCASE: bool = Field(
        default=True, description="Require lowercase letters"
    )
    REQUIRE_NUMBERS: bool = Field(default=True, description="Require numbers")
    REQUIRE_SPECIAL_CHARS: bool = Field(
        default=True, description="Require special characters"
    )

    # ============================================
    # DATABASE - PostgreSQL
    # ============================================
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database URL (asyncpg)",
    )
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(
        default="postgres", description="PostgreSQL password"
    )
    POSTGRES_DB: str = Field(
        default="iob_maiis_db", description="PostgreSQL database name"
    )
    POSTGRES_HOST: str = Field(default="postgres", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")

    # Connection Pool Settings
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Maximum overflow connections")
    DB_POOL_TIMEOUT: int = Field(
        default=30, description="Connection pool timeout in seconds"
    )
    DB_POOL_RECYCLE: int = Field(
        default=3600, description="Connection recycle time in seconds"
    )

    # ============================================
    # REDIS - Cache & Session Store
    # ============================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_HOST: str = Field(default="redis", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_MAX_CONNECTIONS: int = Field(
        default=50, description="Maximum Redis connections"
    )
    REDIS_SOCKET_TIMEOUT: int = Field(
        default=5, description="Redis socket timeout in seconds"
    )
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(
        default=5, description="Redis connection timeout in seconds"
    )

    # ============================================
    # QDRANT - Vector Database
    # ============================================
    QDRANT_URL: str = Field(
        default="http://qdrant:6333", description="Qdrant server URL"
    )
    QDRANT_GRPC_PORT: int = Field(default=6334, description="Qdrant gRPC port")
    QDRANT_COLLECTION_NAME: str = Field(
        default="iob_maiis_documents", description="Qdrant collection name"
    )
    QDRANT_API_KEY: Optional[str] = Field(
        default=None, description="Qdrant API key (optional)"
    )
    EMBEDDING_DIM: int = Field(default=768, description="Embedding dimension size")
    VECTOR_SEARCH_LIMIT: int = Field(
        default=10, description="Vector search result limit"
    )
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7, description="Similarity threshold for vector search"
    )

    # ============================================
    # OLLAMA - Local LLM Service
    # ============================================
    OLLAMA_URL: str = Field(
        default="http://ollama:11434", description="Ollama server URL"
    )
    OLLAMA_HOST: str = Field(
        default="0.0.0.0:11434", description="Ollama host and port"
    )
    LLM_MODEL: str = Field(default="llama3.1:8b", description="Main LLM model")
    EMBEDDING_MODEL: str = Field(
        default="nomic-embed-text", description="Embedding model"
    )
    VISION_MODEL: str = Field(default="llava:13b", description="Vision model")
    OLLAMA_TIMEOUT: int = Field(default=120, description="Ollama request timeout")
    OLLAMA_MAX_RETRIES: int = Field(default=3, description="Ollama max retries")

    # LLM Generation Settings
    LLM_TEMPERATURE: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature"
    )
    LLM_TOP_P: float = Field(default=0.9, ge=0.0, le=1.0, description="LLM top_p")
    LLM_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens to generate")
    LLM_CONTEXT_WINDOW: int = Field(default=4096, description="Context window size")

    # ============================================
    # EXTERNAL API KEYS (Optional)
    # ============================================
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_ORG_ID: Optional[str] = Field(
        default=None, description="OpenAI organization ID"
    )
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model")

    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-sonnet-20240229", description="Anthropic model"
    )

    GOOGLE_CLOUD_API_KEY: Optional[str] = Field(
        default=None, description="Google Cloud API key"
    )
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(
        default=None, description="Google Application credentials path"
    )

    AZURE_OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="Azure OpenAI API key"
    )
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(
        default=None, description="Azure OpenAI endpoint"
    )

    # ============================================
    # CORS & SECURITY
    # ============================================
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost",
            "http://127.0.0.1:3000",
        ],
        description="Allowed CORS origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True, description="Allow CORS credentials"
    )
    CORS_MAX_AGE: int = Field(default=3600, description="CORS preflight cache time")

    # Security Headers
    ENABLE_HTTPS_REDIRECT: bool = Field(
        default=False, description="Redirect HTTP to HTTPS"
    )
    SECURE_COOKIES: bool = Field(default=False, description="Use secure cookies")
    HSTS_MAX_AGE: int = Field(default=31536000, description="HSTS max age")

    # ============================================
    # RATE LIMITING
    # ============================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    RATE_LIMIT_PER_DAY: int = Field(default=10000, description="Rate limit per day")

    # API Specific Limits
    AUTH_RATE_LIMIT: int = Field(
        default=5, description="Auth endpoint rate limit per minute"
    )
    CHAT_RATE_LIMIT: int = Field(
        default=30, description="Chat endpoint rate limit per minute"
    )
    UPLOAD_RATE_LIMIT: int = Field(
        default=10, description="Upload endpoint rate limit per minute"
    )

    # ============================================
    # FILE UPLOAD SETTINGS
    # ============================================
    MAX_UPLOAD_SIZE: int = Field(
        default=10485760, description="Max upload size in bytes (10MB)"
    )
    MAX_FILE_SIZE_MB: int = Field(default=10, description="Max file size in MB")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/jpg",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
        description="Allowed file MIME types",
    )
    UPLOAD_DIRECTORY: str = Field(
        default="/data/documents", description="Upload directory path"
    )
    TEMP_DIRECTORY: str = Field(
        default="/tmp/uploads", description="Temporary directory path"
    )

    # ============================================
    # STORAGE SETTINGS (MinIO / S3)
    # ============================================
    # Storage provider selection
    STORAGE_PROVIDER: str = Field(
        default="minio",
        description="Storage provider: minio, s3, local",
    )

    # MinIO Settings (S3-compatible object storage)
    MINIO_ENDPOINT: str = Field(
        default="minio:9000", description="MinIO server endpoint"
    )
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO secret key")
    MINIO_SECURE: bool = Field(
        default=False, description="Use HTTPS for MinIO connections"
    )
    MINIO_BUCKET_DOCUMENTS: str = Field(
        default="documents", description="MinIO bucket for documents"
    )
    MINIO_BUCKET_AUDIO: str = Field(
        default="audio", description="MinIO bucket for audio files"
    )
    MINIO_BUCKET_IMAGES: str = Field(
        default="images", description="MinIO bucket for images"
    )
    MINIO_REGION: str = Field(
        default="us-east-1", description="MinIO region (for compatibility)"
    )

    # AWS S3 Settings (for production)
    S3_ENDPOINT: Optional[str] = Field(
        default=None, description="S3 endpoint URL (leave empty for AWS S3)"
    )
    S3_ACCESS_KEY: Optional[str] = Field(
        default=None, description="AWS S3 access key ID"
    )
    S3_SECRET_KEY: Optional[str] = Field(
        default=None, description="AWS S3 secret access key"
    )
    S3_REGION: str = Field(default="us-east-1", description="AWS S3 region")
    S3_BUCKET: str = Field(default="iob-maiis", description="S3 bucket name")
    S3_BUCKET_DOCUMENTS: str = Field(
        default="documents", description="S3 prefix/folder for documents"
    )
    S3_BUCKET_AUDIO: str = Field(
        default="audio", description="S3 prefix/folder for audio files"
    )
    S3_BUCKET_IMAGES: str = Field(
        default="images", description="S3 prefix/folder for images"
    )
    S3_USE_SSL: bool = Field(default=True, description="Use SSL for S3 connections")
    S3_SIGNATURE_VERSION: str = Field(
        default="s3v4", description="S3 signature version"
    )

    # Storage optimization
    STORAGE_PRESIGNED_URL_EXPIRY: int = Field(
        default=3600, description="Presigned URL expiration in seconds (1 hour)"
    )
    STORAGE_MAX_MULTIPART_SIZE: int = Field(
        default=104857600, description="Max size for multipart upload (100MB)"
    )
    ENABLE_STORAGE_ENCRYPTION: bool = Field(
        default=True, description="Enable server-side encryption for stored files"
    )
    STORAGE_RETENTION_DAYS: int = Field(
        default=365, description="File retention period in days (0 = forever)"
    )

    # ============================================
    # BANKING SETTINGS
    # ============================================
    MAX_TRANSACTION_AMOUNT: float = Field(
        default=100000.00, description="Maximum transaction amount"
    )
    MIN_ACCOUNT_BALANCE: float = Field(
        default=0.00, description="Minimum account balance"
    )
    DAILY_TRANSACTION_LIMIT: float = Field(
        default=500000.00, description="Daily transaction limit"
    )
    TRANSACTION_FEE_PERCENTAGE: float = Field(
        default=0.01, description="Transaction fee percentage"
    )
    ENABLE_FRAUD_DETECTION: bool = Field(
        default=True, description="Enable fraud detection"
    )

    # Currency Settings
    DEFAULT_CURRENCY: str = Field(default="USD", description="Default currency")
    SUPPORTED_CURRENCIES: List[str] = Field(
        default=["USD", "EUR", "GBP", "INR", "JPY"],
        description="Supported currencies",
    )

    # ============================================
    # AI MODEL SETTINGS
    # ============================================
    # Document Processing
    CHUNK_SIZE: int = Field(default=1000, description="Document chunk size")
    CHUNK_OVERLAP: int = Field(default=200, description="Chunk overlap size")
    MAX_CHUNKS_PER_DOCUMENT: int = Field(
        default=100, description="Maximum chunks per document"
    )

    # Embedding Settings
    EMBEDDING_BATCH_SIZE: int = Field(default=32, description="Embedding batch size")
    EMBEDDING_CACHE_ENABLED: bool = Field(
        default=True, description="Enable embedding cache"
    )
    EMBEDDING_CACHE_TTL: int = Field(
        default=3600, description="Embedding cache TTL in seconds"
    )

    # RAG Settings
    RAG_TOP_K: int = Field(default=5, description="RAG top K results")
    RAG_SCORE_THRESHOLD: float = Field(default=0.7, description="RAG score threshold")
    RAG_MAX_CONTEXT_LENGTH: int = Field(
        default=4000, description="RAG max context length"
    )
    RAG_ENABLE_RERANKING: bool = Field(default=True, description="Enable reranking")

    # OCR Settings
    OCR_ENGINE: str = Field(default="tesseract", description="OCR engine")
    OCR_LANGUAGE: str = Field(default="eng", description="OCR language")
    OCR_DPI: int = Field(default=300, description="OCR DPI")
    OCR_TIMEOUT: int = Field(default=30, description="OCR timeout in seconds")

    # Speech Recognition
    SPEECH_MODEL: str = Field(default="whisper-1", description="Speech model")
    SPEECH_LANGUAGE: str = Field(default="en", description="Speech language")
    SPEECH_SAMPLE_RATE: int = Field(
        default=16000, description="Speech sample rate in Hz"
    )
    SPEECH_MAX_DURATION: int = Field(
        default=300, description="Max speech duration in seconds"
    )

    # ============================================
    # SPEECH/TTS PROVIDER SETTINGS
    # ============================================
    # Provider Selection
    STT_PROVIDER: str = Field(
        default="openai",
        description="Speech-to-Text provider: openai, google, azure, local, placeholder",
    )
    TTS_PROVIDER: str = Field(
        default="elevenlabs",
        description="Text-to-Speech provider: elevenlabs, openai, google, azure, local, placeholder",
    )

    # OpenAI Whisper Settings
    OPENAI_WHISPER_MODEL: str = Field(
        default="whisper-1", description="OpenAI Whisper model version"
    )
    OPENAI_WHISPER_TIMEOUT: int = Field(
        default=30, description="OpenAI Whisper API timeout in seconds"
    )
    OPENAI_WHISPER_MAX_RETRIES: int = Field(
        default=3, description="OpenAI Whisper API max retries"
    )

    # ElevenLabs Settings
    ELEVENLABS_API_KEY: Optional[str] = Field(
        default=None, description="ElevenLabs API key for TTS"
    )
    ELEVENLABS_VOICE_ID: str = Field(
        default="21m00Tcm4TlvDq8ikWAM",
        description="ElevenLabs default voice ID (Rachel)",
    )
    ELEVENLABS_MODEL_ID: str = Field(
        default="eleven_monolingual_v1", description="ElevenLabs TTS model ID"
    )
    ELEVENLABS_STABILITY: float = Field(
        default=0.5, ge=0.0, le=1.0, description="ElevenLabs voice stability (0.0-1.0)"
    )
    ELEVENLABS_SIMILARITY_BOOST: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="ElevenLabs similarity boost (0.0-1.0)",
    )
    ELEVENLABS_TIMEOUT: int = Field(
        default=30, description="ElevenLabs API timeout in seconds"
    )

    # Google Cloud Speech Settings
    GOOGLE_CLOUD_STT_MODEL: str = Field(
        default="latest_long", description="Google Cloud STT model"
    )
    GOOGLE_CLOUD_TTS_VOICE: str = Field(
        default="en-US-Neural2-C", description="Google Cloud TTS voice name"
    )

    # Azure Speech Settings
    AZURE_SPEECH_KEY: Optional[str] = Field(
        default=None, description="Azure Speech API key"
    )
    AZURE_SPEECH_REGION: str = Field(
        default="eastus", description="Azure Speech service region"
    )
    AZURE_TTS_VOICE: str = Field(
        default="en-US-AriaNeural", description="Azure TTS voice name"
    )

    # Local/Fallback Settings
    ENABLE_STT_FALLBACK: bool = Field(
        default=True, description="Enable fallback to local STT if API fails"
    )
    ENABLE_TTS_FALLBACK: bool = Field(
        default=True, description="Enable fallback to local TTS if API fails"
    )

    # ============================================
    # MONITORING & OBSERVABILITY
    # ============================================
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")
    PROMETHEUS_RETENTION_DAYS: int = Field(
        default=30, description="Prometheus retention days"
    )

    GRAFANA_ADMIN_USER: str = Field(default="admin", description="Grafana admin user")
    GRAFANA_ADMIN_PASSWORD: str = Field(
        default="admin", description="Grafana admin password"
    )
    GRAFANA_PORT: int = Field(default=3001, description="Grafana port")

    # ============================================
    # LOGGING & DEBUGGING
    # ============================================
    LOG_FORMAT: str = Field(default="json", description="Log format: json or text")
    LOG_ROTATION: str = Field(default="daily", description="Log rotation")
    LOG_RETENTION_DAYS: int = Field(default=30, description="Log retention days")
    LOG_FILE_PATH: str = Field(
        default="/app/logs/application.log", description="Log file path"
    )
    ENABLE_SQL_LOGGING: bool = Field(default=False, description="Enable SQL logging")
    ENABLE_REQUEST_LOGGING: bool = Field(
        default=True, description="Enable request logging"
    )

    # Sentry (Error Tracking)
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    SENTRY_ENVIRONMENT: str = Field(
        default="development", description="Sentry environment"
    )
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=0.1, description="Sentry traces sample rate"
    )

    # ============================================
    # PERFORMANCE TUNING
    # ============================================
    # Worker Settings
    UVICORN_WORKERS: int = Field(default=4, description="Uvicorn worker count")
    UVICORN_TIMEOUT: int = Field(default=60, description="Uvicorn timeout")
    UVICORN_KEEPALIVE: int = Field(default=5, description="Uvicorn keepalive")

    # Cache Settings
    CACHE_DEFAULT_TIMEOUT: int = Field(
        default=300, description="Default cache timeout in seconds"
    )
    CACHE_KEY_PREFIX: str = Field(default="iob_maiis", description="Cache key prefix")
    ENABLE_QUERY_CACHE: bool = Field(default=True, description="Enable query cache")
    QUERY_CACHE_TTL: int = Field(default=600, description="Query cache TTL in seconds")

    # ============================================
    # FEATURE FLAGS
    # ============================================
    ENABLE_REGISTRATION: bool = Field(default=True, description="Enable registration")
    ENABLE_PASSWORD_RESET: bool = Field(
        default=True, description="Enable password reset"
    )
    ENABLE_EMAIL_VERIFICATION: bool = Field(
        default=False, description="Enable email verification"
    )
    ENABLE_2FA: bool = Field(default=False, description="Enable 2FA")
    ENABLE_API_VERSIONING: bool = Field(
        default=True, description="Enable API versioning"
    )
    ENABLE_WEBSOCKETS: bool = Field(default=True, description="Enable WebSockets")
    ENABLE_BACKGROUND_TASKS: bool = Field(
        default=True, description="Enable background tasks"
    )

    # Public Feature Flags (for frontend)
    NEXT_PUBLIC_ENABLE_VOICE: bool = Field(
        default=True, description="Enable voice features"
    )
    NEXT_PUBLIC_ENABLE_OCR: bool = Field(default=True, description="Enable OCR")
    NEXT_PUBLIC_ENABLE_MULTIMODAL: bool = Field(
        default=True, description="Enable multimodal"
    )

    # ============================================
    # VALIDATORS
    # ============================================
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v_upper

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins"""
        if not v:
            return ["*"]
        return v

    # ============================================
    # COMPUTED PROPERTIES
    # ============================================
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.ENVIRONMENT == "staging"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to ensure settings are loaded only once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
