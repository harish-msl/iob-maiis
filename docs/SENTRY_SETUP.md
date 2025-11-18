# Sentry Setup and Configuration Guide

## Overview

This guide covers the setup and configuration of Sentry for error tracking and performance monitoring in the IOB MAIIS application.

## Table of Contents

1. [What is Sentry?](#what-is-sentry)
2. [Getting Started](#getting-started)
3. [Configuration](#configuration)
4. [Environment Variables](#environment-variables)
5. [Features Enabled](#features-enabled)
6. [Testing Sentry Integration](#testing-sentry-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## What is Sentry?

Sentry provides:
- **Error Tracking**: Automatic capture and aggregation of errors
- **Performance Monitoring**: Transaction tracing and performance metrics
- **Release Tracking**: Monitor issues across deployments
- **User Context**: Track which users are affected by issues
- **Breadcrumbs**: Debug trail leading to errors

---

## Getting Started

### 1. Create a Sentry Account

1. Go to [sentry.io](https://sentry.io) and create an account
2. Create a new project:
   - Platform: **Python**
   - Alert frequency: **On every new issue** (recommended)
3. Copy your DSN (Data Source Name) from the project settings

### 2. Configure Your Application

Add Sentry DSN to your environment variables (see below).

---

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# ============================================
# SENTRY CONFIGURATION (Optional but Recommended for Production)
# ============================================

# Sentry DSN - REQUIRED to enable Sentry
# Get this from: https://sentry.io/settings/[org]/projects/[project]/keys/
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0

# Environment name (development, staging, production)
# This helps filter issues by environment in Sentry dashboard
SENTRY_ENVIRONMENT=production

# Release version for tracking deployments
# Format: app-name@version or git-commit-sha
SENTRY_RELEASE=iob-maiis@1.0.0

# Performance Monitoring Settings
# ================================

# Trace sampling rate (0.0 to 1.0)
# 0.1 = 10% of transactions will be traced for performance monitoring
# Production: 0.1 (10%) - Recommended to reduce overhead
# Development: 1.0 (100%) - For testing
SENTRY_TRACES_SAMPLE_RATE=0.1

# Profile sampling rate (0.0 to 1.0)
# Percentage of traced transactions that will be profiled
# Production: 0.1 (10%)
# Development: 0.5 (50%)
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Enable/disable performance tracing
# Set to false to disable performance monitoring entirely
SENTRY_ENABLE_TRACING=true
```

### Configuration by Environment

#### Development
```bash
SENTRY_DSN=  # Leave empty or use a dev project DSN
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
SENTRY_ENABLE_TRACING=true
```

#### Staging
```bash
SENTRY_DSN=https://your-dsn@sentry.io/staging-project-id
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.5
SENTRY_PROFILES_SAMPLE_RATE=0.5
SENTRY_ENABLE_TRACING=true
```

#### Production
```bash
SENTRY_DSN=https://your-dsn@sentry.io/production-project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
SENTRY_ENABLE_TRACING=true
```

---

## Features Enabled

### 1. Automatic Error Capture

All unhandled exceptions are automatically captured and sent to Sentry with:
- Full stack traces
- Request context
- User information (sanitized)
- Environment data

### 2. Performance Monitoring

Tracks performance of:
- HTTP requests
- Database queries (SQLAlchemy)
- Redis operations
- Async operations

### 3. Integrations

The following integrations are enabled:

- **FastAPI**: Captures HTTP request context
- **SQLAlchemy**: Tracks database query performance
- **Redis**: Monitors cache operations
- **AsyncIO**: Handles async exception tracking
- **Logging**: Captures log messages as breadcrumbs

### 4. Data Filtering

Sensitive data is automatically filtered:
- Authorization headers
- Passwords
- API keys
- Tokens
- Cookie values
- User emails (PII)

### 5. Transaction Filtering

To reduce noise and costs, the following are NOT sent to Sentry:
- Health check endpoints (`/health`)
- Metrics endpoints (`/metrics`)
- API documentation (`/docs`, `/redoc`)
- Static files (`/_next/`)

High-volume endpoints are sampled at 10%:
- `/api/chat`
- `/api/voice`

---

## Testing Sentry Integration

### 1. Verify Configuration

Check application logs during startup for:
```
✅ Sentry initialized successfully for environment: production
Traces sample rate: 10.0%
Profiles sample rate: 10.0%
```

### 2. Test Error Capture

Create a test endpoint to trigger an error:

```python
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
```

Visit: `http://localhost:8000/sentry-debug`

Check Sentry dashboard for the error event.

### 3. Test Performance Monitoring

Make several requests to your API and check Sentry's **Performance** tab for:
- Transaction traces
- Slow queries
- High-latency endpoints

### 4. Manual Error Capture

Use the helper functions:

```python
from app.core.sentry import capture_exception, capture_message

# Capture an exception
try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        level="error",
        tags={"component": "payment"},
        extra={"transaction_id": "12345"}
    )

# Capture a message
capture_message(
    "User performed important action",
    level="info",
    tags={"action": "transfer"},
    extra={"amount": 1000}
)
```

---

## Best Practices

### 1. Use Environments Wisely

- Use separate Sentry projects for dev/staging/production
- Or use a single project with environment filtering
- Never send development errors to production project

### 2. Sample Rates

**Production Recommendations:**
- Traces: 0.05 - 0.1 (5-10%)
- Profiles: 0.05 - 0.1 (5-10%)

**Why?**
- Reduces performance overhead
- Lowers Sentry quota usage
- Still provides sufficient data for monitoring

### 3. Release Tracking

Update `SENTRY_RELEASE` on each deployment:
```bash
# Use git commit SHA
SENTRY_RELEASE=iob-maiis@$(git rev-parse HEAD)

# Or use version tags
SENTRY_RELEASE=iob-maiis@v1.2.3
```

This allows you to:
- Track which releases have issues
- Compare error rates between releases
- Set up deploy notifications

### 4. Add Context

Enrich errors with context:

```python
from app.core.sentry import set_user_context, set_context, add_breadcrumb

# Set user context (only user ID to avoid PII)
set_user_context(user_id="12345")

# Add custom context
set_context("transaction", {
    "transaction_id": "abc123",
    "amount": 100.00,
    "type": "transfer"
})

# Add breadcrumbs for debugging trail
add_breadcrumb(
    message="User initiated transfer",
    category="action",
    level="info",
    data={"from_account": "123", "to_account": "456"}
)
```

### 5. Alert Configuration

Set up alerts in Sentry for:
- New issues in production
- Regression (resolved issues that return)
- High error frequency
- Performance degradation

### 6. Data Privacy

**Already Implemented:**
- PII filtering in `before_send` hooks
- Sensitive headers removed
- User emails not sent
- Request body sanitization

**Additional Steps:**
- Review Sentry's data scrubbing settings
- Enable "Data Scrubber" in project settings
- Configure sensitive fields list

---

## Troubleshooting

### Sentry Not Capturing Errors

**1. Check DSN is set:**
```bash
echo $SENTRY_DSN
```

**2. Check initialization logs:**
Look for "Sentry initialized" message in application logs.

**3. Verify network connectivity:**
```bash
curl -I https://sentry.io
```

**4. Test with debug mode:**
Set `debug=True` in Sentry init to see verbose logging.

### High Quota Usage

**Solutions:**
1. Lower sample rates:
   ```bash
   SENTRY_TRACES_SAMPLE_RATE=0.05
   SENTRY_PROFILES_SAMPLE_RATE=0.05
   ```

2. Add more endpoint filters in `before_send_transaction_filter`

3. Increase quota in Sentry settings or upgrade plan

### Performance Impact

**Mitigation:**
- Use low sample rates (5-10%) in production
- Disable profiling if not needed
- Use async Sentry transport (already enabled)
- Filter out high-frequency low-value transactions

### Missing User Context

Ensure you're calling `set_user_context()` after authentication:

```python
from app.core.sentry import set_user_context

@app.middleware("http")
async def add_user_to_sentry(request: Request, call_next):
    if request.user:
        set_user_context(user_id=str(request.user.id))
    response = await call_next(request)
    return response
```

---

## Sentry Dashboard Navigation

### Issues Tab
- View all captured errors
- Filter by environment, release, user
- See error frequency and affected users
- Mark as resolved or ignored

### Performance Tab
- View transaction traces
- Identify slow endpoints
- Analyze database query performance
- Monitor Redis cache hit rates

### Releases Tab
- Track issues across deployments
- Compare error rates between versions
- See which releases introduced new issues

### Alerts Tab
- Configure alert rules
- Set notification channels (email, Slack, PagerDuty)
- Define issue frequency thresholds

---

## Advanced Features

### 1. Source Maps (for Frontend)

If using with Next.js frontend:
```bash
npm install --save-dev @sentry/webpack-plugin
```

Configure in `next.config.js` to upload source maps.

### 2. Custom Fingerprinting

Group similar errors together:
```python
def before_send_filter(event, hint):
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        event["fingerprint"] = ["{{ default }}", exc_type.__name__]
    return event
```

### 3. Performance Traces

Add custom spans:
```python
from app.core.sentry import trace_function

@trace_function(op="llm.generate")
async def generate_response(prompt: str):
    # Your code here
    pass
```

---

## Security Considerations

1. **Never commit DSN to version control**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Restrict DSN access**
   - Rotate DSN if exposed
   - Use different DSNs per environment

3. **Review captured data**
   - Regularly audit what's being sent
   - Update PII filters as needed
   - Comply with GDPR/data protection laws

4. **Access control**
   - Limit team member access in Sentry
   - Use role-based permissions
   - Enable 2FA for Sentry accounts

---

## Cost Optimization

### Free Tier Limits
- 5,000 errors/month
- 10,000 transactions/month
- 90-day retention

### Tips to Stay Within Limits
1. Use appropriate sample rates
2. Filter out noisy errors
3. Deduplicate similar issues
4. Use rate limiting on endpoints
5. Archive old issues regularly

---

## Support and Resources

- **Sentry Documentation**: https://docs.sentry.io/
- **Python SDK Docs**: https://docs.sentry.io/platforms/python/
- **FastAPI Integration**: https://docs.sentry.io/platforms/python/guides/fastapi/
- **Sentry Status**: https://status.sentry.io/
- **Community Forum**: https://forum.sentry.io/

---

## Quick Reference

### Disable Sentry
```bash
# Remove or comment out SENTRY_DSN
# SENTRY_DSN=
```

### Increase Sampling (Testing)
```bash
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

### Decrease Sampling (Production)
```bash
SENTRY_TRACES_SAMPLE_RATE=0.05
SENTRY_PROFILES_SAMPLE_RATE=0.05
```

### Disable Performance Monitoring
```bash
SENTRY_ENABLE_TRACING=false
```

---

**Last Updated**: 2025-01-17  
**Version**: 1.0.0  
**Maintainer**: IOB MAIIS Team