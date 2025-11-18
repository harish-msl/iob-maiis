# ============================================
# IOB MAIIS - Sentry Integration
# Error Tracking & Performance Monitoring
# Updated: 2025-01-17
# ============================================

import logging
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

logger = logging.getLogger(__name__)


# ============================================
# SENTRY CONFIGURATION
# ============================================


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "production",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    enable_tracing: bool = True,
    debug: bool = False,
) -> None:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.

    Args:
        dsn: Sentry DSN (Data Source Name)
        environment: Environment name (development, staging, production)
        release: Release version/tag
        traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)
        profiles_sample_rate: Percentage of transactions to profile (0.0 to 1.0)
        enable_tracing: Enable performance monitoring
        debug: Enable Sentry debug mode
    """
    if not dsn:
        logger.warning("Sentry DSN not provided. Sentry integration disabled.")
        return

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release or "iob-maiis@1.0.0",
            # ============================================
            # INTEGRATIONS
            # ============================================
            integrations=[
                # FastAPI integration
                FastApiIntegration(
                    transaction_style="url",  # or "endpoint"
                    failed_request_status_codes=[403, range(500, 599)],
                ),
                # SQLAlchemy integration
                SqlalchemyIntegration(),
                # Redis integration
                RedisIntegration(),
                # Asyncio integration
                AsyncioIntegration(),
                # Logging integration
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR,  # Send errors and above as events
                ),
            ],
            # ============================================
            # PERFORMANCE MONITORING
            # ============================================
            traces_sample_rate=traces_sample_rate if enable_tracing else 0.0,
            profiles_sample_rate=profiles_sample_rate if enable_tracing else 0.0,
            enable_tracing=enable_tracing,
            # ============================================
            # FILTERING & SAMPLING
            # ============================================
            before_send=before_send_filter,
            before_send_transaction=before_send_transaction_filter,
            # ============================================
            # REQUEST DATA
            # ============================================
            send_default_pii=False,  # Don't send PII by default
            max_breadcrumbs=50,
            attach_stacktrace=True,
            # ============================================
            # TRANSPORT & NETWORK
            # ============================================
            shutdown_timeout=2,
            request_bodies="medium",  # 'never', 'small', 'medium', 'always'
            max_request_body_size="medium",  # 'never', 'small', 'medium', 'always'
            # ============================================
            # DEBUG
            # ============================================
            debug=debug,
            # ============================================
            # ADDITIONAL OPTIONS
            # ============================================
            sample_rate=1.0,  # Error sampling rate
            ignore_errors=[
                KeyboardInterrupt,
                # Add other exceptions to ignore
            ],
            in_app_include=["app"],  # Mark app modules as in-app
            in_app_exclude=[
                "site-packages",
                "dist-packages",
            ],
        )

        logger.info(f"Sentry initialized successfully for environment: {environment}")
        logger.info(f"Traces sample rate: {traces_sample_rate * 100}%")
        logger.info(f"Profiles sample rate: {profiles_sample_rate * 100}%")

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}", exc_info=True)


# ============================================
# EVENT FILTERING
# ============================================


def before_send_filter(
    event: Dict[str, Any], hint: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Filter events before sending to Sentry.
    Remove sensitive data and filter out unwanted events.

    Args:
        event: The event dictionary
        hint: Additional information about the event

    Returns:
        Modified event or None to drop the event
    """
    try:
        # Get exception info
        if "exc_info" in hint:
            exc_type, exc_value, tb = hint["exc_info"]

            # Filter out specific exceptions
            ignored_exceptions = [
                "asyncio.CancelledError",
                "starlette.exceptions.HTTPException",
            ]

            if exc_type.__name__ in ignored_exceptions:
                return None

        # Remove sensitive data from request
        if "request" in event:
            request = event["request"]

            # Remove sensitive headers
            if "headers" in request:
                headers = request["headers"]
                sensitive_headers = [
                    "authorization",
                    "cookie",
                    "x-api-key",
                    "x-auth-token",
                ]
                for header in sensitive_headers:
                    if header in headers:
                        headers[header] = "[Filtered]"

            # Remove sensitive data from body
            if "data" in request:
                data = request["data"]
                if isinstance(data, dict):
                    sensitive_keys = [
                        "password",
                        "token",
                        "secret",
                        "api_key",
                        "access_token",
                        "refresh_token",
                    ]
                    for key in sensitive_keys:
                        if key in data:
                            data[key] = "[Filtered]"

        # Add custom tags
        if "tags" not in event:
            event["tags"] = {}

        event["tags"]["app"] = "iob-maiis"
        event["tags"]["component"] = "backend"

        # Add user context (without PII)
        if "user" in event and event["user"]:
            user = event["user"]
            # Remove sensitive user data
            user.pop("email", None)
            user.pop("username", None)
            # Keep only user ID for tracking
            event["user"] = {"id": user.get("id", "anonymous")}

        return event

    except Exception as e:
        logger.error(f"Error in before_send filter: {e}")
        return event


def before_send_transaction_filter(
    event: Dict[str, Any], hint: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Filter transactions before sending to Sentry.

    Args:
        event: The transaction event dictionary
        hint: Additional information about the event

    Returns:
        Modified event or None to drop the transaction
    """
    try:
        # Get transaction name
        transaction_name = event.get("transaction", "")

        # Filter out health check and metrics endpoints
        ignored_transactions = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/_next/",
        ]

        for ignored in ignored_transactions:
            if transaction_name.startswith(ignored):
                return None

        # Sample high-volume endpoints more aggressively
        high_volume_endpoints = [
            "/api/chat",
            "/api/voice",
        ]

        for endpoint in high_volume_endpoints:
            if transaction_name.startswith(endpoint):
                # Only send 10% of these transactions
                import random

                if random.random() > 0.1:
                    return None

        return event

    except Exception as e:
        logger.error(f"Error in before_send_transaction filter: {e}")
        return event


# ============================================
# HELPER FUNCTIONS
# ============================================


def capture_exception(
    error: Exception,
    level: str = "error",
    tags: Optional[Dict[str, str]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Manually capture an exception and send to Sentry.

    Args:
        error: The exception to capture
        level: Severity level ('fatal', 'error', 'warning', 'info', 'debug')
        tags: Additional tags to attach
        extra: Additional context data

    Returns:
        Event ID if sent, None otherwise
    """
    try:
        with sentry_sdk.push_scope() as scope:
            # Set level
            scope.level = level

            # Add tags
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)

            # Add extra context
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)

            # Capture exception
            event_id = sentry_sdk.capture_exception(error)
            logger.debug(f"Exception captured in Sentry: {event_id}")
            return event_id

    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")
        return None


def capture_message(
    message: str,
    level: str = "info",
    tags: Optional[Dict[str, str]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Capture a message and send to Sentry.

    Args:
        message: The message to capture
        level: Severity level ('fatal', 'error', 'warning', 'info', 'debug')
        tags: Additional tags to attach
        extra: Additional context data

    Returns:
        Event ID if sent, None otherwise
    """
    try:
        with sentry_sdk.push_scope() as scope:
            # Set level
            scope.level = level

            # Add tags
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)

            # Add extra context
            if extra:
                for key, value in extra.items():
                    scope.set_extra(key, value)

            # Capture message
            event_id = sentry_sdk.capture_message(message, level=level)
            logger.debug(f"Message captured in Sentry: {event_id}")
            return event_id

    except Exception as e:
        logger.error(f"Failed to capture message in Sentry: {e}")
        return None


def set_user_context(
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Set user context for Sentry events.

    Args:
        user_id: User ID
        email: User email (will be filtered if PII disabled)
        username: Username (will be filtered if PII disabled)
        **kwargs: Additional user attributes
    """
    try:
        user_data = {}

        if user_id:
            user_data["id"] = user_id

        # Only include PII if explicitly enabled
        # By default, we only send user ID
        # if email:
        #     user_data["email"] = email
        # if username:
        #     user_data["username"] = username

        # Add custom attributes
        for key, value in kwargs.items():
            user_data[key] = value

        sentry_sdk.set_user(user_data)

    except Exception as e:
        logger.error(f"Failed to set user context in Sentry: {e}")


def set_context(name: str, data: Dict[str, Any]) -> None:
    """
    Set custom context for Sentry events.

    Args:
        name: Context name
        data: Context data dictionary
    """
    try:
        sentry_sdk.set_context(name, data)
    except Exception as e:
        logger.error(f"Failed to set context in Sentry: {e}")


def add_breadcrumb(
    message: str,
    category: str = "default",
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Add a breadcrumb for debugging context.

    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Severity level
        data: Additional data
    """
    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {},
        )
    except Exception as e:
        logger.error(f"Failed to add breadcrumb in Sentry: {e}")


def start_transaction(name: str, op: str = "http.server") -> Any:
    """
    Start a Sentry transaction for performance monitoring.

    Args:
        name: Transaction name
        op: Operation type

    Returns:
        Transaction object
    """
    try:
        return sentry_sdk.start_transaction(name=name, op=op)
    except Exception as e:
        logger.error(f"Failed to start transaction in Sentry: {e}")
        return None


# ============================================
# PERFORMANCE MONITORING DECORATORS
# ============================================


def trace_function(op: str = "function"):
    """
    Decorator to trace function execution in Sentry.

    Args:
        op: Operation type

    Usage:
        @trace_function(op="database.query")
        async def fetch_user(user_id: str):
            ...
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=op, description=func.__name__):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=op, description=func.__name__):
                return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
