# SSL/TLS & Security Configuration Guide

**IOB MAIIS - Production Security Hardening**  
**Updated:** 2025-01-17  
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [SSL/TLS Setup](#ssltls-setup)
3. [Let's Encrypt Integration](#lets-encrypt-integration)
4. [Nginx Security Configuration](#nginx-security-configuration)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Sentry Error Tracking](#sentry-error-tracking)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the complete SSL/TLS and security configuration for IOB MAIIS, including:

- ✅ **SSL/TLS Certificates** - Let's Encrypt with automatic renewal
- ✅ **Nginx Security Headers** - HSTS, CSP, X-Frame-Options, etc.
- ✅ **Rate Limiting** - Protection against abuse
- ✅ **Prometheus Monitoring** - Comprehensive metrics collection
- ✅ **Grafana Dashboards** - Real-time visualization
- ✅ **Sentry Integration** - Error tracking and performance monitoring
- ✅ **Security Hardening** - Production-grade security measures

---

## SSL/TLS Setup

### Prerequisites

1. **Domain Name** - Pointed to your server's IP address
2. **Ports Open** - 80 (HTTP) and 443 (HTTPS)
3. **Root Access** - Required for certbot
4. **Email Address** - For Let's Encrypt notifications

### Quick Start

#### Development (Self-Signed Certificate)

For local development, generate a self-signed certificate:

```bash
cd /path/to/iob-maiis
chmod +x scripts/setup-ssl.sh
sudo ./scripts/setup-ssl.sh --self-signed
```

This creates:
- `nginx/ssl/selfsigned.crt` - Self-signed certificate
- `nginx/ssl/selfsigned.key` - Private key
- `nginx/ssl/dhparam.pem` - DH parameters

#### Production (Let's Encrypt)

For production with a real domain:

```bash
# Set environment variables
export DOMAIN="yourdomain.com"
export SSL_EMAIL="admin@yourdomain.com"

# Run SSL setup
sudo ./scripts/setup-ssl.sh -d $DOMAIN -e $SSL_EMAIL
```

#### Staging Test (Recommended First)

Test with Let's Encrypt staging to avoid rate limits:

```bash
sudo ./scripts/setup-ssl.sh -d $DOMAIN -e $SSL_EMAIL --staging
```

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Obtain certificate
sudo certbot certonly --webroot \
  --webroot-path=./nginx/www \
  --email admin@yourdomain.com \
  --agree-tos \
  --no-eff-email \
  -d yourdomain.com

# Copy certificates
sudo cp -L /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/live/yourdomain.com/
sudo cp -L /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/live/yourdomain.com/
sudo cp -L /etc/letsencrypt/live/yourdomain.com/chain.pem nginx/ssl/live/yourdomain.com/

# Generate DH parameters
openssl dhparam -out nginx/ssl/dhparam.pem 2048
```

### Auto-Renewal

Certificates are automatically renewed via cron job:

```bash
# Check renewal configuration
sudo certbot renew --dry-run

# View cron jobs
crontab -l | grep certbot

# Manual renewal
sudo certbot renew
docker restart iob_maiis_nginx
```

The setup script configures renewal to run twice daily (as recommended by Let's Encrypt).

---

## Let's Encrypt Integration

### Certificate Locations

```
nginx/ssl/
├── live/
│   └── yourdomain.com/
│       ├── fullchain.pem    # Full certificate chain
│       ├── privkey.pem      # Private key
│       └── chain.pem        # Intermediate certificates
├── archive/
│   └── yourdomain.com/      # Previous certificates
├── dhparam.pem              # DH parameters
├── selfsigned.crt           # Development fallback
└── selfsigned.key           # Development fallback
```

### Nginx Configuration

The nginx configuration automatically uses Let's Encrypt certificates:

```nginx
# Production certificates
ssl_certificate /etc/nginx/ssl/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/live/yourdomain.com/privkey.pem;
ssl_trusted_certificate /etc/nginx/ssl/live/yourdomain.com/chain.pem;

# Development fallback (commented out in production)
# ssl_certificate /etc/nginx/ssl/selfsigned.crt;
# ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
```

### ACME Challenge

HTTP-01 challenge for certificate validation:

```nginx
location ^~ /.well-known/acme-challenge/ {
    default_type "text/plain";
    root /var/www/certbot;
    allow all;
}
```

### Rate Limits

Let's Encrypt has the following rate limits:

- **50 certificates** per registered domain per week
- **5 duplicate certificates** per week
- **300 new orders** per account per 3 hours

**Solution:** Use staging environment for testing (`--staging` flag).

---

## Nginx Security Configuration

### Security Headers

The nginx configuration includes comprehensive security headers:

#### 1. HTTP Strict Transport Security (HSTS)

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

- Forces HTTPS for 1 year
- Applies to all subdomains
- Preload-ready for browser inclusion

#### 2. Clickjacking Protection

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
```

- Prevents embedding in iframes (except same origin)
- Protects against clickjacking attacks

#### 3. XSS Protection

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

- Prevents MIME type sniffing
- Enables browser XSS filter

#### 4. Content Security Policy (CSP)

```nginx
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self' https: wss: ws:; media-src 'self' https:; object-src 'none'; frame-ancestors 'self';" always;
```

- Restricts resource loading
- Prevents XSS and data injection
- **Note:** Adjust based on your requirements

#### 5. Referrer Policy

```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

- Controls referrer information sent with requests

#### 6. Permissions Policy

```nginx
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

- Disables unnecessary browser features
- Enhances privacy

### Rate Limiting

Four rate limit zones configured:

```nginx
# General traffic: 10 requests/second
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;

# API traffic: 20 requests/second
limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;

# Uploads: 5 requests/second
limit_req_zone $binary_remote_addr zone=upload:10m rate=5r/s;

# Authentication: 5 requests/minute
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
```

Applied to endpoints:

```nginx
# API endpoints
location /api {
    limit_req zone=api burst=30 nodelay;
    # ...
}

# Upload endpoints
location ~ ^/api/(documents|upload|voice) {
    limit_req zone=upload burst=10 nodelay;
    # ...
}

# Authentication endpoints
location ~ ^/api/(auth|login|register|token) {
    limit_req zone=auth burst=5 nodelay;
    # ...
}
```

### TLS Configuration

Strong TLS configuration:

```nginx
# Modern TLS protocols only
ssl_protocols TLSv1.2 TLSv1.3;

# Strong cipher suites
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

# Prefer server ciphers
ssl_prefer_server_ciphers off;

# Session cache
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
```

### Connection Limiting

```nginx
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_conn addr 10;
```

Maximum 10 concurrent connections per IP address.

---

## Monitoring & Alerting

### Prometheus Metrics

Comprehensive metrics collection across all services:

#### Application Metrics

- **HTTP Requests**: Total, duration, size, in-progress
- **Authentication**: Attempts, failures
- **Database**: Queries, connections, duration
- **Cache**: Operations, hit ratio
- **Storage**: Uploads, downloads, errors
- **Speech**: Provider requests, fallbacks, audio duration
- **LLM**: Requests, tokens, response time
- **RAG Pipeline**: Duration, errors
- **Documents**: Processing time, OCR duration

#### Infrastructure Metrics

- **System**: CPU, memory, disk usage
- **Nginx**: Requests, errors, rate limits
- **PostgreSQL**: Connections, queries, replication lag
- **Redis**: Memory, connections, operations
- **Qdrant**: Vector operations, search latency
- **MinIO**: Storage usage, operations

#### Service Health

- **Health Checks**: Endpoint availability
- **Uptime**: Service availability percentage
- **Error Rates**: 5xx errors, exceptions

### Accessing Prometheus

```bash
# Prometheus UI
http://localhost:9090

# Metrics endpoint
http://localhost:8000/metrics

# Example queries:
# - Rate of HTTP requests: rate(http_requests_total[5m])
# - 95th percentile latency: histogram_quantile(0.95, http_request_duration_seconds_bucket)
# - Error rate: rate(http_requests_total{status=~"5.."}[5m])
```

### Grafana Dashboards

Pre-configured dashboards for monitoring:

```bash
# Grafana UI
http://localhost:3001

# Default credentials (CHANGE IN PRODUCTION!)
Username: admin
Password: admin
```

#### Available Dashboards

1. **System Overview** - CPU, memory, disk, network
2. **Application Performance** - Request rates, latency, errors
3. **Database Monitoring** - Query performance, connections
4. **AI Services** - LLM performance, RAG pipeline, speech providers
5. **Storage & Cache** - MinIO usage, Redis performance
6. **Security** - Authentication failures, rate limiting, anomalies

### Alert Rules

Configured alerts in `monitoring/prometheus-rules/alerts.yml`:

#### Critical Alerts

- Service down (> 2 minutes)
- High error rate (> 5%)
- Disk space critical (> 95%)
- Database down
- SSL certificate expiring (< 7 days)

#### Warning Alerts

- High CPU usage (> 80%)
- High memory usage (> 85%)
- Slow API response time (> 2s)
- High database connections (> 80%)
- Speech provider fallback active
- Storage quota warning (> 80%)

#### Info Alerts

- Rate limiting active
- High external API usage

### Alertmanager Integration (Optional)

To enable Alertmanager:

```yaml
# docker-compose.yml
alertmanager:
  image: prom/alertmanager:v0.26.0
  ports:
    - "9093:9093"
  volumes:
    - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

---

## Sentry Error Tracking

### Setup

1. **Create Sentry Account**: https://sentry.io
2. **Create Project**: Select FastAPI/Python
3. **Get DSN**: Copy the Data Source Name (DSN)

### Configuration

Add to `backend/.env`:

```env
# Sentry Configuration
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% profiling
SENTRY_ENABLE_TRACING=true
SENTRY_DEBUG=false
```

### Features

#### Error Tracking

- Automatic exception capture
- Stack traces with source code
- Breadcrumbs for debugging context
- User context (anonymized)

#### Performance Monitoring

- Transaction tracing
- Slow query detection
- External API latency tracking
- Database performance

#### Data Filtering

- Sensitive data scrubbing (passwords, tokens, API keys)
- PII removal (emails, usernames)
- Custom filtering for compliance

### Usage

```python
from app.core.sentry import capture_exception, capture_message, set_user_context

# Capture exceptions
try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        level="error",
        tags={"component": "document-processing"},
        extra={"document_id": doc_id}
    )

# Capture messages
capture_message(
    "High storage usage detected",
    level="warning",
    tags={"component": "storage"}
)

# Set user context
set_user_context(user_id="user123")
```

### Accessing Sentry

```bash
# Sentry Dashboard
https://sentry.io/organizations/your-org/issues/

# View:
# - Real-time errors
# - Performance trends
# - Release tracking
# - User feedback
```

---

## Security Best Practices

### 1. Secrets Management

**DO NOT** hardcode secrets in configuration files.

#### Development

```bash
# Use .env files (NOT committed to git)
cp backend/.env.example backend/.env
# Edit and add real secrets
```

#### Production

Use a secrets manager:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name iob-maiis/production \
  --secret-string file://secrets.json

# HashiCorp Vault
vault kv put secret/iob-maiis/prod \
  database_url=xxx \
  jwt_secret=xxx

# Docker Secrets
echo "super_secret_password" | docker secret create db_password -
```

### 2. Environment Variables

Required production variables:

```env
# Application
SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENVIRONMENT=production

# Database
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# Storage
MINIO_ROOT_USER=<username>
MINIO_ROOT_PASSWORD=<strong-password>
S3_ACCESS_KEY=<aws-access-key>
S3_SECRET_KEY=<aws-secret-key>

# External APIs
OPENAI_API_KEY=<openai-key>
ELEVENLABS_API_KEY=<elevenlabs-key>

# Monitoring
SENTRY_DSN=<sentry-dsn>
GRAFANA_ADMIN_PASSWORD=<strong-password>

# SSL/TLS
DOMAIN=yourdomain.com
SSL_EMAIL=admin@yourdomain.com
```

### 3. Database Security

```bash
# Strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# SSL connections (production)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require

# Connection pooling limits
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Backup encryption
pg_dump | gpg --encrypt > backup.sql.gpg
```

### 4. API Security

- ✅ Rate limiting enabled
- ✅ CORS configured
- ✅ JWT authentication
- ✅ Input validation
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection
- ✅ CSRF tokens (for state-changing operations)

### 5. File Upload Security

```python
# Implemented in backend:
# - File type validation
# - Size limits (50MB)
# - Virus scanning (TODO: integrate ClamAV)
# - Secure file storage (MinIO/S3)
# - User isolation (user_id namespacing)
```

### 6. Network Security

```bash
# Firewall configuration (example: ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Internal services (NOT exposed)
# - PostgreSQL: 5432
# - Redis: 6379
# - Qdrant: 6333
# - MinIO: 9000
# - Ollama: 11434
```

### 7. Container Security

```yaml
# docker-compose.yml security:
# - Non-root users
# - Read-only filesystems where possible
# - Resource limits
# - Health checks
# - Private networks
# - No privileged mode
```

### 8. Logging & Auditing

```bash
# Centralized logging (optional: ELK stack)
# - Request logs
# - Authentication logs
# - Error logs
# - Audit logs

# Log retention
# - Development: 7 days
# - Production: 90 days
# - Compliance: 1+ years
```

---

## Troubleshooting

### SSL Certificate Issues

#### Certificate Not Found

```bash
# Check certificate files
ls -la nginx/ssl/live/yourdomain.com/

# Verify ownership
sudo chown -R $(whoami):$(whoami) nginx/ssl/

# Re-run setup
sudo ./scripts/setup-ssl.sh -d yourdomain.com -e admin@yourdomain.com
```

#### Certificate Expired

```bash
# Check expiry
openssl x509 -enddate -noout -in nginx/ssl/live/yourdomain.com/fullchain.pem

# Force renewal
sudo certbot renew --force-renewal
docker restart iob_maiis_nginx
```

#### Rate Limit Exceeded

```bash
# Use staging environment
sudo ./scripts/setup-ssl.sh -d yourdomain.com -e admin@yourdomain.com --staging

# Wait for rate limit reset (1 week)
# Or use different domain/subdomain
```

### Nginx Issues

#### 502 Bad Gateway

```bash
# Check backend status
docker ps | grep backend
docker logs iob_maiis_backend

# Check nginx logs
docker logs iob_maiis_nginx
tail -f nginx/logs/error.log

# Test nginx config
docker exec iob_maiis_nginx nginx -t
```

#### SSL Handshake Failure

```bash
# Test SSL
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check certificate chain
openssl verify -CAfile nginx/ssl/live/yourdomain.com/chain.pem \
  nginx/ssl/live/yourdomain.com/fullchain.pem

# Verify protocols
nmap --script ssl-enum-ciphers -p 443 yourdomain.com
```

### Monitoring Issues

#### Prometheus Not Scraping

```bash
# Check Prometheus targets
http://localhost:9090/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus logs
docker logs iob_maiis_prometheus
```

#### Grafana No Data

```bash
# Verify datasource
# Grafana -> Configuration -> Data Sources -> Prometheus
# Test connection

# Check Prometheus query
# Grafana -> Explore -> Select metric

# Verify time range
# Adjust time picker in dashboard
```

#### Sentry Not Receiving Events

```bash
# Test Sentry DSN
curl -X POST \
  'https://sentry.io/api/PROJECT_ID/store/' \
  -H 'X-Sentry-Auth: Sentry sentry_key=YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Test from curl"}'

# Check backend logs
docker logs iob_maiis_backend | grep -i sentry

# Verify environment variable
docker exec iob_maiis_backend env | grep SENTRY_DSN
```

### Performance Issues

#### High Response Time

```bash
# Check Grafana dashboard: Application Performance
# Identify slow endpoints

# Review Prometheus metrics
http_request_duration_seconds{quantile="0.95"}

# Check database slow queries
# PostgreSQL: pg_stat_statements

# Profile with Sentry
# View transaction details in Sentry dashboard
```

#### Memory Leaks

```bash
# Monitor memory usage
docker stats

# Check Grafana: System Overview dashboard

# Restart affected service
docker restart iob_maiis_backend

# Investigate with profiling
# Add memory profiling to backend
```

---

## Quick Reference

### Commands

```bash
# SSL Setup
sudo ./scripts/setup-ssl.sh --self-signed           # Development
sudo ./scripts/setup-ssl.sh -d domain.com -e email  # Production
sudo certbot renew                                   # Manual renewal

# Docker
docker-compose up -d                    # Start services
docker-compose down                     # Stop services
docker-compose logs -f backend         # View logs
docker restart iob_maiis_nginx         # Restart nginx

# Monitoring
http://localhost:9090                  # Prometheus
http://localhost:3001                  # Grafana
http://localhost:8000/metrics          # Backend metrics

# SSL Testing
openssl s_client -connect domain:443   # Test connection
openssl x509 -text -in cert.pem        # View certificate
```

### Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] HSTS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Strong passwords generated
- [ ] Secrets moved to vault
- [ ] CORS configured correctly
- [ ] Firewall rules applied
- [ ] Backup strategy implemented
- [ ] Monitoring dashboards reviewed
- [ ] Alert rules configured
- [ ] Sentry integration tested
- [ ] Log aggregation setup
- [ ] Incident response plan documented

---

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Security Best Practices](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [OWASP Security Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Sentry Documentation](https://docs.sentry.io/)

---

**Last Updated:** 2025-01-17  
**Maintained By:** IOB MAIIS Team  
**Version:** 1.0.0