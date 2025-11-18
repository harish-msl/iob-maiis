# Monitoring & Observability Guide

**IOB MAIIS - Production Monitoring & Observability**  
**Updated:** 2025-01-17  
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prometheus Metrics](#prometheus-metrics)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Alerting](#alerting)
6. [Sentry Integration](#sentry-integration)
7. [Log Aggregation](#log-aggregation)
8. [Performance Monitoring](#performance-monitoring)
9. [Custom Metrics](#custom-metrics)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

IOB MAIIS implements a comprehensive monitoring and observability stack:

- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards
- **Sentry** - Error tracking and performance monitoring
- **Alertmanager** - Alert routing and notifications (optional)
- **Exporters** - Service-specific metrics collection
- **Custom Metrics** - Application-level instrumentation

### Key Features

✅ **Real-time Monitoring** - Live metrics and dashboards  
✅ **Historical Analysis** - 30-day metric retention  
✅ **Alerting** - Automated alert notifications  
✅ **Error Tracking** - Detailed error reports with stack traces  
✅ **Performance Profiling** - Transaction tracing and bottleneck detection  
✅ **Service Health** - Uptime monitoring and health checks  
✅ **Resource Usage** - CPU, memory, disk, network tracking  
✅ **Custom Metrics** - Application-specific KPIs  

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     IOB MAIIS Services                       │
├─────────────────────────────────────────────────────────────┤
│  Backend  │  Frontend  │  Postgres  │  Redis  │  Qdrant    │
│  MinIO    │  Ollama    │   Nginx    │  ...    │            │
└────┬──────┴──────┬─────┴──────┬─────┴────┬────┴──────┬─────┘
     │             │            │          │           │
     │ /metrics    │ /metrics   │ :9187    │ :9121     │ :6333
     │             │            │          │           │
     └─────────────┴────────────┴──────────┴───────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Prometheus    │
                    │   (Scraping)    │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
         ┌──────────┐  ┌─────────┐  ┌──────────┐
         │  Grafana │  │ Alerts  │  │  Sentry  │
         │(Dashboards)│ │Manager│  │(Errors)  │
         └──────────┘  └─────────┘  └──────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Notifications  │
                    │ Slack/Email/PD  │
                    └─────────────────┘
```

### Components

1. **Metrics Collection**
   - Prometheus client libraries embedded in services
   - Exporters for third-party services (Postgres, Redis, Nginx)
   - System metrics (node-exporter, cAdvisor)

2. **Metrics Storage**
   - Prometheus TSDB (Time Series Database)
   - 30-day retention by default
   - Optional remote write for long-term storage

3. **Visualization**
   - Grafana dashboards
   - Pre-configured panels and queries
   - Custom dashboards supported

4. **Alerting**
   - Prometheus alert rules
   - Alertmanager routing (optional)
   - Multiple notification channels

5. **Error Tracking**
   - Sentry SDK integration
   - Automatic exception capture
   - Performance transaction tracing

---

## Prometheus Metrics

### Service Endpoints

```bash
# Backend API
http://localhost:8000/metrics

# Prometheus UI
http://localhost:9090

# Prometheus Targets
http://localhost:9090/targets

# Prometheus Alerts
http://localhost:9090/alerts
```

### Metric Categories

#### 1. HTTP Metrics

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Request duration (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Requests in progress
http_requests_in_progress

# Request size
histogram_quantile(0.95, rate(http_request_size_bytes_bucket[5m]))

# Response size
histogram_quantile(0.95, rate(http_response_size_bytes_bucket[5m]))
```

#### 2. Authentication Metrics

```promql
# Authentication attempts
rate(auth_attempts_total[5m])

# Authentication failures
rate(auth_failures_total[5m])

# Failure rate
rate(auth_failures_total[5m]) / rate(auth_attempts_total[5m])
```

#### 3. Database Metrics

```promql
# Query rate
rate(db_queries_total[5m])

# Query duration (95th percentile)
histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m]))

# Active connections
db_connections_active

# Idle connections
db_connections_idle

# PostgreSQL specific
pg_stat_database_numbackends
pg_stat_database_tup_fetched
pg_stat_database_conflicts
```

#### 4. Cache Metrics

```promql
# Cache operations
rate(cache_operations_total[5m])

# Cache hit ratio
cache_hit_ratio

# Redis specific
redis_connected_clients
redis_memory_used_bytes
redis_keys_total
```

#### 5. Storage Metrics

```promql
# Upload rate
rate(storage_operations_total{operation="upload"}[5m])

# Upload duration
histogram_quantile(0.95, rate(storage_upload_duration_seconds_bucket[5m]))

# Upload size
histogram_quantile(0.95, rate(storage_upload_size_bytes_bucket[5m]))

# Error rate
rate(storage_upload_errors_total[5m])

# MinIO specific
minio_bucket_usage_total_bytes
minio_s3_requests_total
```

#### 6. AI/LLM Metrics

```promql
# LLM request rate
rate(llm_requests_total[5m])

# LLM response time
histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))

# Token usage
rate(llm_tokens_total[5m])

# RAG pipeline duration
histogram_quantile(0.95, rate(rag_pipeline_duration_seconds_bucket[5m]))

# RAG errors
rate(rag_pipeline_errors_total[5m])

# Vector search latency
histogram_quantile(0.95, rate(vector_search_duration_seconds_bucket[5m]))
```

#### 7. Speech Provider Metrics

```promql
# Speech requests
rate(speech_provider_requests_total[5m])

# Speech duration
histogram_quantile(0.95, rate(speech_provider_duration_seconds_bucket[5m]))

# Fallback usage
rate(speech_provider_fallback_total[5m])

# Audio processing
histogram_quantile(0.95, rate(speech_audio_duration_seconds_bucket[5m]))
```

#### 8. System Metrics

```promql
# CPU usage
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Network I/O
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

### Querying Examples

#### Service Availability

```promql
# Uptime percentage (last 24h)
avg_over_time(up[24h]) * 100

# Services down
up == 0
```

#### Performance

```promql
# Slowest endpoints (avg response time)
topk(10, 
  avg by(endpoint) (
    rate(http_request_duration_seconds_sum[5m]) / 
    rate(http_request_duration_seconds_count[5m])
  )
)

# Highest error rate endpoints
topk(10, 
  sum by(endpoint) (
    rate(http_requests_total{status=~"5.."}[5m])
  )
)
```

#### Resource Utilization

```promql
# Top memory consumers
topk(5, container_memory_usage_bytes)

# Top CPU consumers
topk(5, rate(container_cpu_usage_seconds_total[5m]))
```

#### Business Metrics

```promql
# Document processing rate
rate(document_processing_total{status="success"}[1h])

# File upload volume
sum(rate(file_upload_size_bytes[1h]))

# Active users (WebSocket connections)
websocket_connections_active
```

---

## Grafana Dashboards

### Accessing Grafana

```bash
URL: http://localhost:3001
Username: admin
Password: admin  # CHANGE IN PRODUCTION!
```

### Pre-configured Dashboards

#### 1. System Overview

**Location:** `Dashboards > IOB MAIIS > System Overview`

**Panels:**
- CPU Usage (per service)
- Memory Usage (per service)
- Disk Usage
- Network I/O
- Container Stats

**Use Cases:**
- Resource capacity planning
- Identifying resource bottlenecks
- Detecting memory leaks

#### 2. Application Performance

**Location:** `Dashboards > IOB MAIIS > Application Performance`

**Panels:**
- Request Rate (RPS)
- Response Time (p50, p95, p99)
- Error Rate
- Requests in Progress
- Top 10 Slowest Endpoints
- Top 10 Highest Error Rate Endpoints

**Use Cases:**
- Performance optimization
- SLA monitoring
- Incident investigation

#### 3. Database Monitoring

**Location:** `Dashboards > IOB MAIIS > Database`

**Panels:**
- Query Rate
- Query Duration
- Active Connections
- Idle Connections
- Cache Hit Ratio
- Slow Queries
- Replication Lag (if applicable)

**Use Cases:**
- Database performance tuning
- Connection pool optimization
- Query optimization

#### 4. AI Services

**Location:** `Dashboards > IOB MAIIS > AI Services`

**Panels:**
- LLM Request Rate
- LLM Response Time
- Token Usage (cost tracking)
- RAG Pipeline Performance
- Embedding Generation Time
- Vector Search Latency
- Speech Provider Performance
- Fallback Usage

**Use Cases:**
- AI service cost monitoring
- Performance optimization
- Provider comparison

#### 5. Storage & Cache

**Location:** `Dashboards > IOB MAIIS > Storage`

**Panels:**
- Storage Usage (MinIO/S3)
- Upload/Download Rate
- Upload Duration
- Redis Memory Usage
- Cache Hit Ratio
- Storage Errors

**Use Cases:**
- Storage capacity planning
- Cache optimization
- Cost monitoring

#### 6. Security Dashboard

**Location:** `Dashboards > IOB MAIIS > Security`

**Panels:**
- Authentication Failure Rate
- Rate Limiting Events
- Suspicious Upload Activity
- SSL Certificate Expiry
- Failed Login Attempts
- Blocked IPs

**Use Cases:**
- Security monitoring
- Attack detection
- Compliance reporting

### Creating Custom Dashboards

```javascript
// Example: Custom panel for user activity
{
  "title": "Active Users",
  "targets": [
    {
      "expr": "websocket_connections_active",
      "legendFormat": "Active Connections"
    }
  ],
  "type": "graph"
}
```

### Dashboard Best Practices

1. **Use Variables** - Create dynamic dashboards with template variables
2. **Set Time Ranges** - Default to last 1 hour, allow user selection
3. **Add Annotations** - Mark deployments and incidents
4. **Use Alerts** - Configure dashboard alerts for critical metrics
5. **Organize Rows** - Group related panels together
6. **Add Descriptions** - Document what each panel shows
7. **Share Links** - Use short URLs for incident response

---

## Alerting

### Alert Configuration

Alerts defined in: `monitoring/prometheus-rules/alerts.yml`

### Alert Severity Levels

- **Critical** - Immediate action required (page on-call)
- **Warning** - Investigation needed (notify team)
- **Info** - Awareness (log only)

### Critical Alerts

```yaml
# Service Down
alert: ServiceDown
expr: up == 0
for: 2m
severity: critical

# High Error Rate
alert: HighAPIErrorRate
expr: (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100 > 5
for: 5m
severity: critical

# Disk Space Critical
alert: DiskSpaceCritical
expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 95
for: 2m
severity: critical

# Database Down
alert: PostgreSQLDown
expr: pg_up == 0
for: 2m
severity: critical

# SSL Certificate Expiring
alert: SSLCertificateExpiringCritical
expr: (ssl_certificate_expiry_seconds - time()) / 86400 < 7
for: 1h
severity: critical
```

### Warning Alerts

```yaml
# High CPU Usage
alert: HighCPUUsage
expr: 100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
for: 5m
severity: warning

# High Memory Usage
alert: HighMemoryUsage
expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
for: 5m
severity: warning

# Slow API Response
alert: SlowAPIResponseTime
expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
for: 5m
severity: warning

# Speech Provider Fallback
alert: SpeechProviderFallbackActive
expr: rate(speech_provider_fallback_total[5m]) > 0.1
for: 10m
severity: warning
```

### Alert Routing (Alertmanager)

```yaml
# monitoring/alertmanager.yml
route:
  receiver: 'team-notifications'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true
    
    - match:
        severity: warning
      receiver: 'slack'
    
    - match:
        severity: info
      receiver: 'email'

receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<pagerduty-key>'
  
  - name: 'slack'
    slack_configs:
      - api_url: '<slack-webhook>'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  - name: 'email'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.gmail.com:587'
```

### Silence Management

```bash
# Silence an alert (during maintenance)
amtool silence add \
  alertname="HighCPUUsage" \
  --duration=1h \
  --comment="Scheduled maintenance"

# List active silences
amtool silence query

# Expire a silence
amtool silence expire <silence-id>
```

---

## Sentry Integration

### Configuration

```python
# backend/app/core/sentry.py
from app.core.sentry import init_sentry

init_sentry(
    dsn="https://xxx@sentry.io/xxx",
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1
)
```

### Error Tracking

```python
from app.core.sentry import capture_exception, capture_message

# Automatic exception capture
try:
    process_document(doc_id)
except Exception as e:
    capture_exception(
        e,
        level="error",
        tags={"component": "document-processing"},
        extra={"document_id": doc_id}
    )
    raise

# Manual message capture
capture_message(
    "Storage quota approaching limit",
    level="warning",
    tags={"component": "storage"},
    extra={"usage_percent": 85}
)
```

### Performance Monitoring

```python
from app.core.sentry import start_transaction, trace_function

# Manual transaction
with start_transaction(name="process_rag_query", op="ai.rag"):
    with sentry_sdk.start_span(op="embedding", description="Generate embeddings"):
        embeddings = generate_embeddings(query)
    
    with sentry_sdk.start_span(op="search", description="Vector search"):
        results = search_vectors(embeddings)
    
    with sentry_sdk.start_span(op="llm", description="Generate response"):
        response = generate_response(results)

# Decorator-based tracing
@trace_function(op="database.query")
async def fetch_user(user_id: str):
    return await db.query(User).filter(User.id == user_id).first()
```

### Breadcrumbs

```python
from app.core.sentry import add_breadcrumb

# Add context for debugging
add_breadcrumb(
    message="Starting document upload",
    category="upload",
    level="info",
    data={"filename": filename, "size": file_size}
)

add_breadcrumb(
    message="OCR processing initiated",
    category="processing",
    level="info",
    data={"pages": page_count}
)
```

### User Context

```python
from app.core.sentry import set_user_context

# Set user context (anonymized)
set_user_context(
    user_id=user.id,
    # email and username filtered for privacy
)
```

### Sentry Dashboard

**Features:**
- Real-time error tracking
- Stack traces with source code
- Release tracking
- Performance trends
- User feedback
- Issue assignment
- Integration with Jira, Slack, etc.

**URL:** https://sentry.io/organizations/your-org/issues/

---

## Log Aggregation

### Structured Logging

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)

# JSON formatted logs
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Log with context
logger.info(
    "Document processed successfully",
    extra={
        "document_id": doc_id,
        "user_id": user_id,
        "duration_ms": duration,
        "pages": page_count
    }
)
```

### Log Levels

```python
# DEBUG - Development/troubleshooting
logger.debug("Cache key generated", extra={"key": cache_key})

# INFO - Normal operations
logger.info("User authenticated", extra={"user_id": user_id})

# WARNING - Unexpected but handled
logger.warning("API rate limit approaching", extra={"usage": 85})

# ERROR - Operation failed but recoverable
logger.error("Failed to upload to primary storage", extra={"error": str(e)})

# CRITICAL - System failure
logger.critical("Database connection lost", extra={"attempts": retry_count})
```

### ELK Stack Integration (Optional)

```yaml
# docker-compose.yml
elasticsearch:
  image: elasticsearch:8.11.0
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"

logstash:
  image: logstash:8.11.0
  volumes:
    - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  ports:
    - "5000:5000"

kibana:
  image: kibana:8.11.0
  ports:
    - "5601:5601"
  environment:
    ELASTICSEARCH_HOSTS: http://elasticsearch:9200
```

---

## Performance Monitoring

### Key Performance Indicators (KPIs)

1. **Availability**
   - Target: 99.9% uptime
   - Metric: `avg_over_time(up[30d]) * 100`

2. **Response Time**
   - Target: p95 < 500ms
   - Metric: `histogram_quantile(0.95, http_request_duration_seconds_bucket)`

3. **Error Rate**
   - Target: < 0.1%
   - Metric: `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])`

4. **Throughput**
   - Target: 1000 RPS
   - Metric: `rate(http_requests_total[1m])`

### Performance Testing

```python
# Load testing with locust
from locust import HttpUser, task, between

class IOBMAIISUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def chat_query(self):
        self.client.post("/api/chat", json={
            "query": "What are my recent transactions?",
            "use_rag": True
        })
    
    @task(1)
    def upload_document(self):
        with open("test.pdf", "rb") as f:
            self.client.post("/api/documents/upload", files={"file": f})
```

Run load test:
```bash
locust -f load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10
```

### Profiling

```python
# CPU profiling with cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
process_large_dataset()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)

# Memory profiling with memory_profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    large_list = [i for i in range(10000000)]
    return sum(large_list)
```

---

## Custom Metrics

### Adding Custom Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define custom metric
document_ocr_errors = Counter(
    'document_ocr_errors_total',
    'Total OCR processing errors',
    ['language', 'error_type']
)

# Increment metric
document_ocr_errors.labels(language='en', error_type='timeout').inc()

# Histogram for distributions
processing_time = Histogram(
    'custom_processing_duration_seconds',
    'Custom processing duration',
    ['operation_type'],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0)
)

# Observe value
processing_time.labels(operation_type='ocr').observe(duration)

# Gauge for current values
queue_size = Gauge(
    'processing_queue_size',
    'Number of items in processing queue'
)

# Set value
queue_size.set(len(processing_queue))
```

### Business Metrics

```python
# Track user activity
user_actions = Counter(
    'user_actions_total',
    'Total user actions',
    ['action_type', 'status']
)

user_actions.labels(action_type='document_upload', status='success').inc()

# Track revenue/cost
api_cost_total = Counter(
    'external_api_cost_dollars_total',
    'Total external API costs in dollars',
    ['provider']
)

api_cost_total.labels(provider='openai').inc(0.002)  # 0.2 cents per request
```

---

## Best Practices

### 1. Metric Naming

- Use descriptive names: `http_request_duration_seconds` not `http_time`
- Follow conventions: `<namespace>_<metric>_<unit>`
- Use labels for dimensions: `{method="POST", endpoint="/api/chat"}`

### 2. Label Cardinality

- Keep label cardinality low (< 100 unique values)
- Don't use UUIDs or timestamps as labels
- Use aggregation for high-cardinality data

### 3. Histogram Buckets

- Choose buckets based on SLOs
- Include both small and large values
- Default: (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)

### 4. Alert Fatigue

- Set appropriate thresholds
- Use `for` duration to avoid flapping
- Group related alerts
- Route by severity

### 5. Dashboard Design

- One purpose per dashboard
- Most important metrics at top
- Use consistent time ranges
- Add links to runbooks

### 6. Data Retention

- Prometheus: 30 days (configurable)
- Grafana: Unlimited (uses Prometheus as source)
- Sentry: 90 days (paid plans: longer)
- Logs: 7-90 days depending on environment

---

## Troubleshooting

### High Cardinality Issues

```promql
# Find high cardinality metrics
topk(10, count by(__name__)({__name__!=""}))

# Check label cardinality
count by(__name__, job)(up)
```

**Solution:** Reduce label dimensions, use recording rules

### Prometheus Performance

```bash
# Check TSDB stats
curl http://localhost:9090/api/v1/status/tsdb

# Check targets
curl http://localhost:9090/api/v1/targets

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

### Missing Metrics

1. Check target is up: http://localhost:9090/targets
2. Verify metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus logs: `docker logs iob_maiis_prometheus`
4. Verify scrape configuration in `prometheus.yml`

### Grafana Connection Issues

1. Test datasource connection in Grafana UI
2. Verify Prometheus is accessible: `curl http://prometheus:9090`
3. Check Grafana logs: `docker logs iob_maiis_grafana`
4. Verify datasource configuration

### Alert Not Firing

1. Check alert rule syntax in Prometheus UI
2. Verify metric exists: Query in Prometheus
3. Check `for` duration hasn't been met
4. Verify Alertmanager configuration
5. Check silence rules

---

## Quick Reference

### Useful Commands

```bash
# Prometheus
curl http://localhost:9090/api/v1/query?query=up
curl -X POST http://localhost:9090/-/reload

# Check metrics
curl http://localhost:8000/metrics | grep http_requests_total

# Grafana API
curl -u admin:admin http://localhost:3001/api/dashboards/home

# Container stats
docker stats --no-stream
```

### Useful Queries

```promql
# Request rate per endpoint
sum by(endpoint) (rate(http_requests_total[5m]))

# Error percentage
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100

# Apdex score (T=0.5s)
(
  sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
  +
  sum(rate(http_request_duration_seconds_bucket{le="2.0"}[5m])) / 2
)
/
sum(rate(http_request_duration_seconds_count[5m]))
```

---

## Additional Resources

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Observability Engineering (Book)](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)

---

**Last Updated:** 2025-01-17  
**Maintained By:** IOB MAIIS Team  
**Version:** 1.0.0