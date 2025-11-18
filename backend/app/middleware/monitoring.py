# ============================================
# IOB MAIIS - Prometheus Monitoring Middleware
# FastAPI Metrics Collection & Export
# Updated: 2025-01-17
# ============================================

import logging
import time
from collections import defaultdict
from typing import Callable, Dict, Optional

import psutil
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


# ============================================
# PROMETHEUS METRICS DEFINITIONS
# ============================================

# Application Info
app_info = Info(
    "iob_maiis_application",
    "Application information",
)

# HTTP Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    ),
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000),
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
)

# Error Metrics
http_exceptions_total = Counter(
    "http_exceptions_total",
    "Total HTTP exceptions",
    ["method", "endpoint", "exception_type"],
)

# Authentication Metrics
auth_attempts_total = Counter(
    "auth_attempts_total",
    "Total authentication attempts",
    ["status", "method"],
)

auth_failures_total = Counter(
    "auth_failures_total",
    "Total authentication failures",
    ["reason"],
)

# Database Metrics
db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"],
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

db_connections_active = Gauge(
    "db_connections_active",
    "Number of active database connections",
)

db_connections_idle = Gauge(
    "db_connections_idle",
    "Number of idle database connections",
)

# Cache Metrics
cache_operations_total = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["operation", "status"],
)

cache_hit_ratio = Gauge(
    "cache_hit_ratio",
    "Cache hit ratio",
)

# Storage Metrics
storage_operations_total = Counter(
    "storage_operations_total",
    "Total storage operations",
    ["operation", "provider", "status"],
)

storage_upload_duration_seconds = Histogram(
    "storage_upload_duration_seconds",
    "Storage upload duration in seconds",
    ["provider"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)

storage_upload_size_bytes = Histogram(
    "storage_upload_size_bytes",
    "Storage upload size in bytes",
    ["provider"],
    buckets=(1000, 10000, 100000, 1000000, 10000000, 50000000),
)

storage_upload_errors_total = Counter(
    "storage_upload_errors_total",
    "Total storage upload errors",
    ["provider", "error_type"],
)

# Speech Provider Metrics
speech_provider_requests_total = Counter(
    "speech_provider_requests_total",
    "Total speech provider requests",
    ["provider", "operation", "status"],
)

speech_provider_duration_seconds = Histogram(
    "speech_provider_duration_seconds",
    "Speech provider request duration in seconds",
    ["provider", "operation"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

speech_provider_fallback_total = Counter(
    "speech_provider_fallback_total",
    "Total speech provider fallback usage",
    ["primary_provider", "fallback_provider"],
)

speech_audio_duration_seconds = Histogram(
    "speech_audio_duration_seconds",
    "Processed audio duration in seconds",
    ["operation"],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)

# LLM & RAG Metrics
llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["model", "status"],
)

llm_request_duration_seconds = Histogram(
    "llm_request_duration_seconds",
    "LLM request duration in seconds",
    ["model"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total LLM tokens processed",
    ["model", "type"],  # type: prompt, completion
)

rag_pipeline_duration_seconds = Histogram(
    "rag_pipeline_duration_seconds",
    "RAG pipeline duration in seconds",
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

rag_pipeline_errors_total = Counter(
    "rag_pipeline_errors_total",
    "Total RAG pipeline errors",
    ["stage", "error_type"],
)

embedding_duration_seconds = Histogram(
    "embedding_duration_seconds",
    "Embedding generation duration in seconds",
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0),
)

vector_search_duration_seconds = Histogram(
    "vector_search_duration_seconds",
    "Vector search duration in seconds",
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5),
)

# Document Processing Metrics
document_processing_total = Counter(
    "document_processing_total",
    "Total documents processed",
    ["document_type", "status"],
)

document_processing_duration_seconds = Histogram(
    "document_processing_duration_seconds",
    "Document processing duration in seconds",
    ["document_type"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0),
)

ocr_processing_duration_seconds = Histogram(
    "ocr_processing_duration_seconds",
    "OCR processing duration in seconds",
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

# File Upload Metrics
file_upload_total = Counter(
    "file_upload_total",
    "Total file uploads",
    ["file_type", "status"],
)

file_upload_size_bytes = Histogram(
    "file_upload_size_bytes",
    "File upload size in bytes",
    ["file_type"],
    buckets=(1000, 10000, 100000, 1000000, 10000000, 50000000),
)

# External API Metrics
external_api_requests_total = Counter(
    "external_api_requests_total",
    "Total external API requests",
    ["provider", "endpoint", "status"],
)

external_api_duration_seconds = Histogram(
    "external_api_duration_seconds",
    "External API request duration in seconds",
    ["provider", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

# System Metrics
system_cpu_usage_percent = Gauge(
    "system_cpu_usage_percent",
    "System CPU usage percentage",
)

system_memory_usage_bytes = Gauge(
    "system_memory_usage_bytes",
    "System memory usage in bytes",
)

system_memory_available_bytes = Gauge(
    "system_memory_available_bytes",
    "System available memory in bytes",
)

system_disk_usage_percent = Gauge(
    "system_disk_usage_percent",
    "System disk usage percentage",
    ["path"],
)

# WebSocket Metrics
websocket_connections_active = Gauge(
    "websocket_connections_active",
    "Number of active WebSocket connections",
)

websocket_messages_total = Counter(
    "websocket_messages_total",
    "Total WebSocket messages",
    ["direction", "message_type"],
)


# ============================================
# PROMETHEUS MIDDLEWARE
# ============================================


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all HTTP requests.
    """

    def __init__(self, app: FastAPI, app_name: str = "iob-maiis"):
        super().__init__(app)
        self.app_name = app_name

        # Set application info
        app_info.info(
            {
                "app_name": app_name,
                "version": "1.0.0",
                "environment": "production",
            }
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and collect metrics.
        """
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Extract request info
        method = request.method
        endpoint = request.url.path

        # Sanitize endpoint for metrics (remove IDs)
        endpoint_label = self._sanitize_endpoint(endpoint)

        # Track request in progress
        http_requests_in_progress.labels(method=method, endpoint=endpoint_label).inc()

        # Measure request size
        request_size = int(request.headers.get("content-length", 0))
        http_request_size_bytes.labels(method=method, endpoint=endpoint_label).observe(
            request_size
        )

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            status_code = response.status_code
            http_requests_total.labels(
                method=method,
                endpoint=endpoint_label,
                status=status_code,
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint_label,
            ).observe(duration)

            # Measure response size
            response_size = int(response.headers.get("content-length", 0))
            http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint_label,
            ).observe(response_size)

            return response

        except Exception as exc:
            # Record exception
            duration = time.time() - start_time

            http_exceptions_total.labels(
                method=method,
                endpoint=endpoint_label,
                exception_type=type(exc).__name__,
            ).inc()

            http_requests_total.labels(
                method=method,
                endpoint=endpoint_label,
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint_label,
            ).observe(duration)

            logger.error(f"Exception in request: {exc}", exc_info=True)
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(
                method=method, endpoint=endpoint_label
            ).dec()

    @staticmethod
    def _sanitize_endpoint(endpoint: str) -> str:
        """
        Sanitize endpoint path for metric labels.
        Replace UUID/ID patterns with placeholders.
        """
        import re

        # Replace UUIDs
        endpoint = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{uuid}",
            endpoint,
            flags=re.IGNORECASE,
        )

        # Replace numeric IDs
        endpoint = re.sub(r"/\d+", "/{id}", endpoint)

        return endpoint


# ============================================
# METRICS ENDPOINT
# ============================================


async def metrics_endpoint(request: Request) -> Response:
    """
    Expose Prometheus metrics endpoint.
    """
    # Update system metrics before serving
    update_system_metrics()

    # Generate metrics
    metrics_output = generate_latest(REGISTRY)

    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST,
    )


# ============================================
# SYSTEM METRICS COLLECTOR
# ============================================


def update_system_metrics():
    """
    Update system-level metrics (CPU, memory, disk).
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        system_cpu_usage_percent.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage_bytes.set(memory.used)
        system_memory_available_bytes.set(memory.available)

        # Disk usage (root partition)
        disk = psutil.disk_usage("/")
        system_disk_usage_percent.labels(path="/").set(disk.percent)

    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")


# ============================================
# MONITORING SETUP
# ============================================


def setup_monitoring(app: FastAPI, app_name: str = "iob-maiis"):
    """
    Setup monitoring for the FastAPI application.

    Args:
        app: FastAPI application instance
        app_name: Name of the application
    """
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware, app_name=app_name)

    # Add metrics endpoint
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])

    logger.info(f"Prometheus monitoring setup completed for {app_name}")
    logger.info("Metrics available at /metrics endpoint")


# ============================================
# HELPER FUNCTIONS FOR CUSTOM METRICS
# ============================================


def track_auth_attempt(status: str, method: str = "password"):
    """Track authentication attempt."""
    auth_attempts_total.labels(status=status, method=method).inc()
    if status == "failure":
        auth_failures_total.labels(reason="invalid_credentials").inc()


def track_db_query(operation: str, table: str, duration: float):
    """Track database query."""
    db_queries_total.labels(operation=operation, table=table).inc()
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)


def track_cache_operation(operation: str, status: str):
    """Track cache operation."""
    cache_operations_total.labels(operation=operation, status=status).inc()


def track_storage_operation(
    operation: str,
    provider: str,
    status: str,
    duration: Optional[float] = None,
    size: Optional[int] = None,
):
    """Track storage operation."""
    storage_operations_total.labels(
        operation=operation, provider=provider, status=status
    ).inc()
    if duration is not None:
        storage_upload_duration_seconds.labels(provider=provider).observe(duration)
    if size is not None:
        storage_upload_size_bytes.labels(provider=provider).observe(size)


def track_storage_error(provider: str, error_type: str):
    """Track storage error."""
    storage_upload_errors_total.labels(provider=provider, error_type=error_type).inc()


def track_speech_request(provider: str, operation: str, status: str, duration: float):
    """Track speech provider request."""
    speech_provider_requests_total.labels(
        provider=provider, operation=operation, status=status
    ).inc()
    speech_provider_duration_seconds.labels(
        provider=provider, operation=operation
    ).observe(duration)


def track_speech_fallback(primary_provider: str, fallback_provider: str):
    """Track speech provider fallback."""
    speech_provider_fallback_total.labels(
        primary_provider=primary_provider,
        fallback_provider=fallback_provider,
    ).inc()


def track_llm_request(
    model: str, status: str, duration: float, tokens: Optional[Dict[str, int]] = None
):
    """Track LLM request."""
    llm_requests_total.labels(model=model, status=status).inc()
    llm_request_duration_seconds.labels(model=model).observe(duration)
    if tokens:
        for token_type, count in tokens.items():
            llm_tokens_total.labels(model=model, type=token_type).inc(count)


def track_rag_pipeline(duration: float, error: Optional[str] = None):
    """Track RAG pipeline execution."""
    rag_pipeline_duration_seconds.observe(duration)
    if error:
        rag_pipeline_errors_total.labels(stage="pipeline", error_type=error).inc()


def track_document_processing(doc_type: str, status: str, duration: float):
    """Track document processing."""
    document_processing_total.labels(document_type=doc_type, status=status).inc()
    document_processing_duration_seconds.labels(document_type=doc_type).observe(
        duration
    )


def track_file_upload(file_type: str, status: str, size: int):
    """Track file upload."""
    file_upload_total.labels(file_type=file_type, status=status).inc()
    file_upload_size_bytes.labels(file_type=file_type).observe(size)


def track_external_api(provider: str, endpoint: str, status: str, duration: float):
    """Track external API request."""
    external_api_requests_total.labels(
        provider=provider, endpoint=endpoint, status=status
    ).inc()
    external_api_duration_seconds.labels(provider=provider, endpoint=endpoint).observe(
        duration
    )


def track_websocket_connection(active: int):
    """Track WebSocket connection count."""
    websocket_connections_active.set(active)


def track_websocket_message(direction: str, message_type: str):
    """Track WebSocket message."""
    websocket_messages_total.labels(
        direction=direction, message_type=message_type
    ).inc()
