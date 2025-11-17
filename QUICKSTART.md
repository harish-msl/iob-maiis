# 🚀 IOB MAIIS - Quick Start Guide

## Prerequisites Check
```bash
docker --version   # Should be 24.0+
docker-compose --version  # Should be 2.20+
```

## Installation (5 Minutes)

### Option 1: Automated Setup (Recommended)
```bash
# Make setup script executable
chmod +x setup.sh

# Run complete setup
./setup.sh
```

This script will:
- ✅ Check prerequisites
- ✅ Generate secure keys
- ✅ Create directories
- ✅ Pull Docker images
- ✅ Download AI models
- ✅ Start all services
- ✅ Initialize database
- ✅ Run health checks

### Option 2: Manual Setup
```bash
# 1. Create .env from example
cp .env.example .env

# 2. Generate secure keys (Linux/Mac)
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Update .env with these keys

# 3. Start services
docker-compose up -d

# 4. Pull AI models
docker exec iob_maiis_ollama ollama pull llama3.1:8b
docker exec iob_maiis_ollama ollama pull nomic-embed-text

# 5. Initialize database
docker exec iob_maiis_backend python scripts/init_db.py
```

## Access the Application

### URLs
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### Test Accounts
```
Admin Account:
Email: admin@iobmaiis.local
Password: Admin@123456

Demo Account:
Email: demo@iobmaiis.local
Password: Demo@123456
```

## Quick Commands (Makefile)

```bash
make start          # Start all services
make stop           # Stop all services
make restart        # Restart all services
make logs           # View all logs
make logs-backend   # View backend logs
make logs-frontend  # View frontend logs
make health         # Check service health
make test           # Run all tests
make clean          # Clean up everything
```

## Verify Installation

### 1. Check Services
```bash
docker-compose ps
```

All services should show as "Up" and "healthy".

### 2. Test Backend API
```bash
curl http://localhost:8000/health
```

Should return:
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

### 3. Test Authentication
```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123456",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123456"
  }'
```

## Troubleshooting

### Services Not Starting
```bash
# Check Docker is running
docker info

# View service logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

### Database Connection Issues
```bash
# Check PostgreSQL
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Wait 10 seconds, then restart backend
docker-compose restart backend
```

### Ollama Models Not Downloaded
```bash
# Check Ollama is running
docker exec iob_maiis_ollama ollama list

# Pull models manually
docker exec iob_maiis_ollama ollama pull llama3.1:8b
docker exec iob_maiis_ollama ollama pull nomic-embed-text
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 [PID]

# Or change ports in docker-compose.yml
```

## Development Workflow

### Backend Development
```bash
# Access backend container
docker exec -it iob_maiis_backend bash

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest

# Format code
black app/
isort app/
```

### Frontend Development
```bash
# Access frontend container
docker exec -it iob_maiis_frontend sh

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Database Management
```bash
# Access database shell
make db-shell

# Or manually
docker exec -it iob_maiis_postgres psql -U postgres -d iob_maiis_db

# Backup database
make db-backup

# List tables
\dt

# Describe table
\d users
```

## What's Next?

1. **Complete Missing Files** (see PROJECT_STATUS.md)
2. **Implement Frontend UI** (React components)
3. **Add RAG Pipeline** (Document processing)
4. **Create Chat Interface** (AI conversation)
5. **Add Banking Features** (Transactions, accounts)
6. **Write Tests** (Unit, integration, E2E)
7. **Deploy to Production** (SSL, monitoring)

## Need Help?

1. Check `README.md` for comprehensive documentation
2. Review `PROJECT_STATUS.md` for completion status
3. Check logs: `make logs`
4. View API docs: http://localhost:8000/api/docs
5. Review health status: `make health`

## Stop the Application

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything (DESTROYS DATA!)
docker-compose down -v
```

---

**🎉 You're all set! Happy coding!**
