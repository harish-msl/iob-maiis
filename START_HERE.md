# 🚀 IOB MAIIS - Quick Start Guide

**Multimodal AI-Enabled Information System**  
Complete Banking AI Assistant with RAG, Voice, and Document Processing

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running
- ✅ **Git** installed
- ✅ **8GB+ RAM** available
- ✅ **20GB+ Disk Space** available
- ✅ **Windows 10/11** (WSL2 enabled) or **Linux/macOS**

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Start Docker Desktop

**Windows:**
1. Open Docker Desktop from Start Menu
2. Wait for "Docker Desktop is running" status
3. Verify: Open PowerShell and run `docker ps`

**macOS/Linux:**
```bash
# Start Docker service
sudo systemctl start docker  # Linux
open -a Docker              # macOS

# Verify
docker ps
```

---

### Step 2: Clone & Setup (If Not Already Done)

```bash
cd D:\Work\iob-maiis
# or your project directory
```

---

### Step 3: Start All Services

```bash
# Start all services in background
docker compose up -d

# This will start:
# ✅ PostgreSQL (Database)
# ✅ Qdrant (Vector Database)
# ✅ Redis (Cache)
# ✅ MinIO (Object Storage)
# ✅ Ollama (LLM Service)
# ✅ Backend (FastAPI)
# ✅ Frontend (Next.js)
# ✅ Nginx (Reverse Proxy)
# ✅ Prometheus (Monitoring)
# ✅ Grafana (Dashboards)
```

**Expected Output:**
```
✔ Network iob_maiis_network     Created
✔ Container iob_maiis_postgres   Started
✔ Container iob_maiis_redis      Started
✔ Container iob_maiis_qdrant     Started
✔ Container iob_maiis_minio      Started
✔ Container iob_maiis_ollama     Started
✔ Container iob_maiis_backend    Started
✔ Container iob_maiis_frontend   Started
✔ Container iob_maiis_nginx      Started
✔ Container iob_maiis_prometheus Started
✔ Container iob_maiis_grafana    Started
```

---

### Step 4: Wait for Services to Initialize (2-3 minutes)

```bash
# Watch logs (Ctrl+C to exit)
docker compose logs -f

# Or check individual services
docker compose logs backend -f
docker compose logs frontend -f
```

**Wait for these messages:**
```
✅ backend    | ✅ IOB MAIIS started successfully!
✅ frontend   | ▲ Next.js 15.0.3
✅ frontend   | - Local:        http://localhost:3000
```

---

### Step 5: Download AI Models (First Time Only)

```bash
# Enter Ollama container
docker compose exec ollama bash

# Inside container, pull models
ollama pull llama3.1:8b          # Main LLM (~4.7GB)
ollama pull nomic-embed-text     # Embeddings (~274MB)
ollama pull llava:13b            # Vision model (optional, ~7.4GB)

# Verify models
ollama list

# Exit container
exit
```

**This takes 10-20 minutes depending on internet speed**

---

### Step 6: Access the Application

Open your browser and visit:

| Service | URL | Description |
|---------|-----|-------------|
| **🌐 Main App** | http://localhost:3000 | Next.js Frontend |
| **📚 API Docs** | http://localhost:8000/api/docs | Swagger UI |
| **📊 Grafana** | http://localhost:3001 | Monitoring Dashboard |
| **🔍 Prometheus** | http://localhost:9090 | Metrics |
| **💾 MinIO Console** | http://localhost:9001 | Object Storage |
| **🗄️ PgAdmin** | http://localhost:5050 | Database Admin |

**Default Credentials:**
- **Grafana**: admin / admin
- **MinIO**: minioadmin / minioadmin
- **PgAdmin**: admin@iobmaiis.local / admin

---

## 📱 Using the Application

### 1️⃣ Create an Account

1. Go to http://localhost:3000
2. Click **"Sign Up"**
3. Enter:
   - Email: `your@email.com`
   - Password: `SecurePass123!@`
   - Full Name: `Your Name`
4. Click **"Create Account"**

### 2️⃣ Login

1. Use your email and password
2. You'll receive JWT tokens (valid for 30 minutes)

### 3️⃣ Try Features

**💬 Chat with AI:**
- Navigate to "Chat" section
- Ask: "What types of bank accounts do you offer?"
- The system uses RAG to provide contextual answers

**🏦 Banking Operations:**
- Create a savings account
- Deposit $1000
- Check balance
- Transfer money

**📄 Upload Documents:**
- Upload a PDF, image, or Word document
- OCR will extract text
- Document gets indexed in vector database
- Can be searched via AI chat

**🎤 Voice Features:**
- Click microphone icon
- Speak your query
- Get voice response

---

## 🛠️ Common Commands

### Managing Services

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a specific service
docker compose restart backend

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Check service status
docker compose ps

# Remove everything (including data)
docker compose down -v
```

### Accessing Containers

```bash
# Backend shell
docker compose exec backend bash

# Frontend shell
docker compose exec frontend sh

# Ollama shell
docker compose exec ollama bash

# Database shell
docker compose exec postgres psql -U postgres -d iob_maiis_db
```

### Rebuilding Services

```bash
# Rebuild after code changes
docker compose build backend
docker compose build frontend

# Rebuild and restart
docker compose up -d --build
```

---

## 🔧 Troubleshooting

### Issue: Docker not running
```bash
# Error: "open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified"
# Solution: Start Docker Desktop and wait for it to fully initialize
```

### Issue: Port already in use
```bash
# Error: "Bind for 0.0.0.0:8000 failed: port is already allocated"
# Solution: Stop conflicting service or change port in docker-compose.yml
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux
```

### Issue: Backend fails to start
```bash
# Check logs
docker compose logs backend

# Common causes:
# 1. Database not ready - wait 30s and retry
# 2. Missing .env file - ensure .env exists
# 3. Model not downloaded - pull Ollama models
```

### Issue: Frontend build errors
```bash
# Clear cache and rebuild
docker compose down
docker compose build --no-cache frontend
docker compose up -d
```

### Issue: Ollama models not downloading
```bash
# Check Ollama service
docker compose logs ollama

# Manually pull models
docker compose exec ollama ollama pull llama3.1:8b

# Verify available space
docker system df
```

### Issue: Out of disk space
```bash
# Clean up Docker
docker system prune -a --volumes

# Remove old images
docker image prune -a

# Check disk usage
docker system df
```

---

## 📊 Health Checks

### Quick Health Check

```bash
# All services should return "healthy"
curl http://localhost:8000/health
curl http://localhost:3000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "qdrant": "healthy"
  }
}
```

### Individual Service Checks

```bash
# PostgreSQL
docker compose exec postgres pg_isready

# Redis
docker compose exec redis redis-cli ping

# Qdrant
curl http://localhost:6333/health

# Ollama
curl http://localhost:11434/api/tags
```

---

## 🔐 Security Notes

### Development vs Production

**Current Setup (Development):**
- ✅ Debug mode enabled
- ✅ Verbose logging
- ✅ Hot reload enabled
- ⚠️ Default passwords (CHANGE IN PRODUCTION!)

**For Production:**
1. Set `ENVIRONMENT=production` in `.env`
2. Change all default passwords
3. Enable SSL/TLS
4. Configure Sentry DSN
5. Use proper secret management
6. Set up backup strategy

### Changing Default Passwords

Edit `.env` file:
```bash
# Database
POSTGRES_PASSWORD=your-secure-db-password

# Redis
REDIS_PASSWORD=your-secure-redis-password

# MinIO
MINIO_ROOT_PASSWORD=your-secure-minio-password

# Grafana
GRAFANA_ADMIN_PASSWORD=your-secure-grafana-password

# Secret Keys (already generated)
SECRET_KEY=<already-secure>
JWT_SECRET_KEY=<already-secure>
```

Then restart:
```bash
docker compose down
docker compose up -d
```

---

## 📈 Monitoring & Observability

### Grafana Dashboards

1. Open http://localhost:3001
2. Login: admin / admin
3. Change password on first login
4. Navigate to **Dashboards**
5. Pre-configured dashboards:
   - Application Metrics
   - Database Performance
   - API Response Times
   - Error Rates

### Prometheus Metrics

Visit http://localhost:9090 for raw metrics:
- `http_requests_total` - Request counts
- `http_request_duration_seconds` - Latency
- `http_errors_total` - Error rates
- `db_connection_pool_size` - DB connections
- `rag_pipeline_duration_seconds` - RAG performance

### Application Logs

```bash
# Backend logs
docker compose logs -f backend | grep ERROR

# Frontend logs
docker compose logs -f frontend

# All logs
docker compose logs -f
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test authentication
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!@",
    "full_name": "Test User"
  }'

# Test chat
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What are your banking services?"
  }'
```

### Automated Tests

```bash
# Backend tests
docker compose exec backend pytest

# Frontend tests
docker compose exec frontend npm test

# E2E tests
docker compose exec frontend npm run test:e2e
```

---

## 🚀 Performance Optimization

### For Development

```bash
# Reduce resource limits in docker-compose.yml
# Use smaller models: llama3.1:3b instead of llama3.1:8b
# Disable unnecessary services
```

### For Production

```bash
# Enable production mode
ENVIRONMENT=production

# Use production builds
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker compose up -d --scale backend=3
```

---

## 📚 Next Steps

1. ✅ **Read Documentation**: Check `/docs` folder
2. ✅ **Explore API**: Visit http://localhost:8000/api/docs
3. ✅ **Customize**: Edit `.env` for your needs
4. ✅ **Add Data**: Upload documents to knowledge base
5. ✅ **Monitor**: Set up Grafana alerts
6. ✅ **Secure**: Change default passwords

---

## 🆘 Getting Help

- **Documentation**: `/docs` folder
- **API Reference**: http://localhost:8000/api/docs
- **Logs**: `docker compose logs -f`
- **GitHub Issues**: Create an issue in the repository

---

## 📝 Important Files

```
iob-maiis/
├── .env                    # Environment variables (REQUIRED)
├── docker-compose.yml      # Service definitions
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py        # Entry point
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, security
│   │   └── services/      # Business logic
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js application
│   ├── src/
│   │   ├── app/          # App router
│   │   ├── components/   # UI components
│   │   └── lib/          # Utilities
│   └── package.json      # Node dependencies
└── monitoring/           # Prometheus & Grafana configs
```

---

## ✅ Success Checklist

Before deploying, ensure:

- [ ] Docker Desktop is running
- [ ] `.env` file exists with secure secrets
- [ ] All services are healthy (`docker compose ps`)
- [ ] Ollama models downloaded (`ollama list`)
- [ ] Can access frontend (http://localhost:3000)
- [ ] Can access API docs (http://localhost:8000/api/docs)
- [ ] Can create account and login
- [ ] Chat with AI works
- [ ] Banking operations work
- [ ] Monitoring dashboards accessible

---

## 🎉 You're Ready!

Your IOB MAIIS application is now running!

**Default Access:**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs

**Enjoy your Multimodal AI Banking System! 🚀**

---

*Last Updated: 2025-01-18*  
*Version: 1.0.0*