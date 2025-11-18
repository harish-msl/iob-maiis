# Quick Reference - SSL/TLS & Monitoring

**IOB MAIIS - Production Security & Observability**  
**Last Updated:** 2025-01-17

---

## 🔐 SSL/TLS Setup

### Development (Self-Signed)
```bash
sudo ./scripts/setup-ssl.sh --self-signed
```

### Production (Let's Encrypt)
```bash
# Set environment
export DOMAIN="yourdomain.com"
export SSL_EMAIL="admin@yourdomain.com"

# Run setup
sudo ./scripts/setup-ssl.sh -d $DOMAIN -e $SSL_EMAIL

# Test renewal
sudo certbot renew --dry-run
```

### Staging Test (Recommended First)
```bash
sudo ./scripts/setup-ssl.sh -d $DOMAIN -e $SSL_EMAIL --staging
```

### Manual Renewal
```bash
sudo certbot renew
docker restart iob_maiis_nginx
```

### Verify SSL
```bash
# Test connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check expiry
openssl x509 -enddate -noout -in nginx/ssl/live/yourdomain.com/fullchain.pem

# Test SSL rating
https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
```

---

## 📊 Monitoring Access

### URLs
```
Grafana:     http://localhost:3001
Prometheus:  http://localhost:9090
Metrics:     http://localhost:8000/metrics
Sentry:      https://sentry.io/organizations/your-org
```

### Default Credentials
```
Grafana:  admin / admin (CHANGE IMMEDIATELY!)
```

---

## 📈 Prometheus Queries

### HTTP Metrics
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Response time (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Requests in progress
http_requests_in_progress

# Error percentage
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100
```

### Database Metrics
```promql
# Active connections
db_connections_active

# Query rate
rate(db_queries_total[5m])

# Query latency (p95)
histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m]))
```

### AI/LLM Metrics
```promql
# LLM request rate
rate(llm_requests_total[5m])

# LLM latency (p95)
histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))

# Token usage
rate(llm_tokens_total[5m])

# RAG pipeline duration
histogram_quantile(0.95, rate(rag_pipeline_duration_seconds_bucket[5m]))
```

### System Metrics
```promql
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

### Service Health
```promql
# Uptime percentage (24h)
avg_over_time(up[24h]) * 100

# Services down
up == 0

# Slowest endpoints
topk(10, avg by(endpoint) (
  rate(http_request_duration_seconds_sum[5m]) / 
  rate(http_request_duration_seconds_count[5m])
))
```

---

## 🚨 Alert Management

### View Alerts
```bash
# Prometheus UI
http://localhost:9090/alerts

# API
curl http://localhost:9090/api/v1/alerts
```

### Silence Alerts
```bash
# Using amtool (if Alertmanager deployed)
amtool silence add alertname="HighCPUUsage" --duration=1h --comment="Maintenance"

# List silences
amtool silence query

# Expire silence
amtool silence expire <silence-id>
```

---

## 🐛 Sentry Integration

### Configuration
```env
SENTRY_DSN=https://xxx@sentry.io/xxx
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
SENTRY_ENABLE_TRACING=true
```

### Usage in Code
```python
from app.core.sentry import capture_exception, capture_message

# Capture exception
try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        level="error",
        tags={"component": "documents"},
        extra={"doc_id": doc_id}
    )

# Capture message
capture_message(
    "High storage usage",
    level="warning",
    tags={"component": "storage"}
)
```

---

## 🔧 Docker Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker restart iob_maiis_nginx
docker restart iob_maiis_backend

# View logs
docker-compose logs -f backend
docker-compose logs -f nginx

# Check status
docker-compose ps

# View resource usage
docker stats
```

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/api/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3001/api/health
```

---

## 🔍 Troubleshooting

### SSL Issues

**Certificate Not Found**
```bash
ls -la nginx/ssl/live/yourdomain.com/
sudo ./scripts/setup-ssl.sh -d yourdomain.com -e admin@yourdomain.com
```

**Nginx Config Error**
```bash
docker exec iob_maiis_nginx nginx -t
docker logs iob_maiis_nginx
```

**502 Bad Gateway**
```bash
docker ps | grep backend
docker logs iob_maiis_backend
docker restart iob_maiis_backend
```

### Monitoring Issues

**Metrics Not Appearing**
```bash
# Check endpoint
curl http://localhost:8000/metrics | grep http_requests_total

# Check Prometheus targets
http://localhost:9090/targets

# Restart backend
docker restart iob_maiis_backend
```

**Grafana No Data**
```bash
# Test datasource connection in Grafana UI
# Configuration > Data Sources > Prometheus > Test

# Check Prometheus query
curl 'http://localhost:9090/api/v1/query?query=up'

# Restart Grafana
docker restart iob_maiis_grafana
```

**Sentry Not Receiving Events**
```bash
# Check DSN configured
docker exec iob_maiis_backend env | grep SENTRY_DSN

# Test manually
docker exec iob_maiis_backend python -c "
import sentry_sdk
sentry_sdk.init('YOUR_DSN')
sentry_sdk.capture_message('Test from CLI')
"

# Check logs
docker logs iob_maiis_backend | grep -i sentry
```

---

## 📋 Environment Variables

### Required for Production
```env
# Application
SECRET_KEY=<openssl rand -hex 32>
JWT_SECRET_KEY=<openssl rand -hex 32>
ENVIRONMENT=production

# Database
POSTGRES_PASSWORD=<openssl rand -base64 32>
REDIS_PASSWORD=<openssl rand -base64 32>

# SSL/TLS
DOMAIN=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
GRAFANA_ADMIN_PASSWORD=<strong-password>

# External APIs
OPENAI_API_KEY=sk-xxx
ELEVENLABS_API_KEY=xxx

# Storage (Production)
STORAGE_PROVIDER=s3
S3_BUCKET=iob-maiis-production
S3_ACCESS_KEY=xxx
S3_SECRET_KEY=xxx
```

---

## 🎯 Key Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Availability | 99.9% | < 99.5% |
| Response Time (p95) | < 500ms | > 2s |
| Error Rate | < 0.1% | > 1% |
| Throughput | 100+ RPS | N/A |
| DB Query (p95) | < 100ms | > 500ms |
| LLM Response (p95) | < 5s | > 30s |
| RAG Pipeline (p95) | < 2s | > 10s |

---

## 🚀 Quick Start Checklist

### Development
- [ ] Run `sudo ./scripts/setup-ssl.sh --self-signed`
- [ ] Update `backend/app/main.py` with monitoring integration
- [ ] Start services: `docker-compose up -d`
- [ ] Verify metrics: `curl http://localhost:8000/metrics`
- [ ] Access Grafana: http://localhost:3001 (admin/admin)
- [ ] Check Prometheus targets: http://localhost:9090/targets

### Production
- [ ] Generate production secrets
- [ ] Configure DNS records
- [ ] Run SSL setup: `./scripts/setup-ssl.sh -d domain.com -e email`
- [ ] Configure firewall (ports 22, 80, 443)
- [ ] Update environment variables
- [ ] Create Sentry project and add DSN
- [ ] Deploy services
- [ ] Verify SSL: `openssl s_client -connect domain:443`
- [ ] Check monitoring dashboards
- [ ] Test alerts
- [ ] Change default passwords
- [ ] Configure backups

---

## 📚 Documentation

- **SSL/TLS Guide:** `docs/SSL_TLS_CONFIGURATION.md` (879 lines)
- **Monitoring Guide:** `docs/MONITORING_OBSERVABILITY.md` (1,085 lines)
- **Implementation Summary:** `SSL_MONITORING_IMPLEMENTATION_SUMMARY.md` (1,000 lines)
- **Production Readiness:** `PRODUCTION_READINESS_2025-01-17.md` (760 lines)

---

## 🔗 Quick Links

- **Prometheus UI:** http://localhost:9090
- **Grafana:** http://localhost:3001
- **Metrics Endpoint:** http://localhost:8000/metrics
- **API Docs:** http://localhost:8000/docs
- **SSL Test:** https://www.ssllabs.com/ssltest/

---

## 🆘 Emergency Contacts

```
Critical Alerts:  PagerDuty → On-call engineer
Incidents:        Slack #incidents
Status Updates:   Slack #operations
Escalation:       CTO/Technical Lead
```

---

## 💡 Pro Tips

1. **Always test SSL with staging first:** `--staging` flag prevents rate limits
2. **Monitor dashboards during deployments:** Catch issues early
3. **Set alert thresholds conservatively:** Better to alert early than miss issues
4. **Use Sentry breadcrumbs liberally:** They're invaluable for debugging
5. **Review slow queries weekly:** Database optimization prevents future issues
6. **Check certificate expiry monthly:** Even with auto-renewal
7. **Test backup restoration regularly:** Backups are useless if restore fails
8. **Keep documentation updated:** Future you will thank present you

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-17  
**Status:** ✅ Production Ready