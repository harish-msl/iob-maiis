"""
IOB MAIIS - Logging Configuration Module
Structured logging with Loguru and JSON formatting
Supports file rotation, multi-level logging, and integration with monitoring

Created: 2025-01-17
Python: 3.12
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger

# Remove default handler
logger.remove()


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect them to Loguru.
    This allows third-party libraries using standard logging to be captured by Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def serialize_record(record: Dict[str, Any]) -> str:
    """
    Serialize log record to JSON format
    """
    import json
    from datetime import datetime

    # Extract the record data
    subset = {
        "timestamp": record["time"].timestamp(),
        "time": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add extra fields if present
    if record.get("extra"):
        subset["extra"] = record["extra"]

    # Add exception info if present
    if record.get("exception"):
        subset["exception"] = str(record["exception"])

    return json.dumps(subset, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: str = "logs/application.log",
    rotation: str = "500 MB",
    retention: str = "30 days",
    compression: str = "zip",
) -> None:
    """
    Setup logging configuration with Loguru

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type (json or text)
        log_file: Path to log file
        rotation: When to rotate log file
        retention: How long to keep old logs
        compression: Compression format for rotated logs
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Define formats
    if log_format == "json":
        # JSON format for production
        format_string = serialize_record
    else:
        # Human-readable format for development
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add stdout handler with colors (for development)
    logger.add(
        sys.stdout,
        format=format_string,
        level=log_level,
        colorize=True if log_format != "json" else False,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe
    )

    # Add file handler with rotation
    logger.add(
        log_file,
        format=format_string,
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression=compression,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe
        encoding="utf-8",
    )

    # Add error file handler (errors only)
    error_log_file = log_path.parent / "error.log"
    logger.add(
        str(error_log_file),
        format=format_string,
        level="ERROR",
        rotation=rotation,
        retention=retention,
        compression=compression,
        backtrace=True,
        diagnose=True,
        enqueue=True,
        encoding="utf-8",
    )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept specific libraries
    for logger_name in [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
        "aiohttp",
    ]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info("✅ Logging configured successfully")
    logger.info(f"📝 Log level: {log_level}")
    logger.info(f"📄 Log format: {log_format}")
    logger.info(f"📁 Log file: {log_file}")


# Initialize logging on module import
try:
    from app.core.config import settings

    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        log_file=settings.LOG_FILE_PATH,
        rotation=settings.LOG_ROTATION,
        retention=f"{settings.LOG_RETENTION_DAYS} days",
    )
except Exception as e:
    # Fallback to default configuration if settings are not available
    setup_logging()
    logger.warning(f"⚠️  Using default logging configuration: {e}")


# Export logger
__all__ = ["logger", "setup_logging"]
