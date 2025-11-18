# 🏦 IOB MAIIS - Multimodal AI-Enabled Information System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.0-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Enterprise-Grade Dockerized RAG-Powered Multimodal AI Banking Assistant**

A comprehensive, production-ready banking information system powered by cutting-edge AI technologies, featuring multimodal interactions (text, voice, images), RAG (Retrieval Augmented Generation), and enterprise-grade security.

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Tech Stack](#-tech-stack)
- [🔧 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🧪 Testing](#-testing)
- [📊 Monitoring](#-monitoring)
- [🔒 Security](#-security)
- [📚 API Documentation](#-api-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

### 🤖 AI-Powered Capabilities
- **RAG Pipeline**: Retrieval-Augmented Generation for accurate, context-aware responses
- **Multimodal Interactions**: 
  - 💬 Text-based chat
  - 🎤 Voice commands and responses
  - 📸 Image/document processing via OCR
- **Local LLM**: Powered by Ollama (Llama 3.1) - no external API dependencies
- **Semantic Search**: Vector similarity search using Qdrant
- **Document Intelligence**: Extract insights from PDFs, images, and documents

### 🏦 Banking Features
- **Account Management**: Create, view, and manage bank accounts
- **Transactions**: Real-time transaction processing with fraud detection
- **Balance Inquiries**: Instant balance checks via AI chat
- **Fund Transfers**: Secure peer-to-peer transfers
- **Transaction History**: Detailed transaction logs with AI-powered insights
- **Financial Analytics**: AI-driven spending patterns and recommendations

### 🔒 Enterprise Security
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Granular permission management
- **Password Encryption**: bcrypt hashing with configurable rounds
- **Rate Limiting**: Protection against brute force attacks
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **CORS Protection**: Configurable cross-origin policies
- **Audit Logging**: Complete audit trail of all operations

### 🎯 Developer Experience
- **Fully Dockerized**: One-command deployment
- **Hot Reload**: Development mode with auto-reload
- **Comprehensive Testing**: Unit, integration, and E2E tests
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **Monitoring**: Prometheus + Grafana dashboards
- **Type Safety**: TypeScript frontend, type-hinted Python backend

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
│                    (Load Balancer & SSL)                     │
└────────────┬────────────────────────────────────┬───────────┘
             │                                    │
    ┌────────▼────────┐                  ┌───────▼────────┐
    │  Frontend (Next) │                  │ Backend (API)  │
    │   - React 18     │◄────────────────►│  - FastAPI     │
    │   - TypeScript   │     WebSocket    │  - Python 3.12 │
    │   - Tailwind CSS │                  │  - SQLAlchemy  │
    └──────────────────┘                  └────────┬────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────┐
                    │                              │                  │
            ┌───────▼──────┐            ┌─────────▼─────┐   ┌───────▼──────┐
            │  PostgreSQL  │            │    Qdrant     │   │    Redis     │
            │   (Primary)  │            │   (Vector)    │   │   (Cache)    │
            │    DB 16     │            │   Database    │   │   Store 7.2  │
            └──────────────┘            └───────────────┘   └──────────────┘
                    │
            ┌───────▼──────┐
            │    Ollama    │
            │  LLM Service │
            │  (Llama 3.1) │
            └──────────────┘
```

### Data Flow

1. **User Request** → Nginx → Frontend/Backend
2. **Authentication** → JWT Validation → Redis Session Check
3. **AI Chat** → RAG Pipeline → Qdrant (Vector Search) → LLM (Ollama)
4. **Banking Operations** → PostgreSQL → Transaction Processing
5. **Real-time Updates** → WebSocket → Live notifications

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 24.0+ & **Docker Compose** 2.20+
- **Git** 2.40+
- **4GB+ RAM** (8GB+ recommended)
- **10GB+ Disk Space**

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/harish-msl/iob-maiis.git
cd iob-maiis

# Copy environment file
cp .env.example .env

# Generate secure keys (Linux/Mac)
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/your-super-secret-key-min-32-chars-change-in-production-2025/$SECRET_KEY/" .env
sed -i "s/your-jwt-secret-key-min-32-chars-change-in-production-2025/$JWT_SECRET_KEY/" .env

# Start all services
docker-compose up -d

# Pull Ollama models
docker exec iob_maiis_ollama ollama pull llama3.1:8b
docker exec iob_maiis_ollama ollama pull nomic-embed-text

# Initialize database and ingest sample documents
docker exec iob_maiis_backend python scripts/init_db.py
docker exec iob_maiis_backend python scripts/ingest_documents.py
```

### Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **PgAdmin**: http://localhost:5050 (optional)

---

## 📦 Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Core language |
| **FastAPI** | 0.115.0 | Web framework |
| **SQLAlchemy** | 2.0 | ORM |
| **PostgreSQL** | 16 | Primary database |
| **Qdrant** | Latest | Vector database |
| **Redis** | 7.2 | Cache & sessions |
| **Ollama** | Latest | LLM service |
| **LangChain** | 0.1.0 | LLM orchestration |
| **Sentence Transformers** | 2.3.1 | Embeddings |
| **Tesseract** | Latest | OCR |
| **Whisper** | Latest | Speech-to-text |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.0 | React framework |
| **React** | 18.3 | UI library |
| **TypeScript** | 5.3 | Type safety |
| **Tailwind CSS** | 3.4 | Styling |
| **Zustand** | 4.4 | State management |
| **Radix UI** | Latest | Component library |
| **Axios** | 1.6 | HTTP client |

### Infrastructure
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | 24.0+ | Containerization |
| **Nginx** | 1.25 | Reverse proxy |
| **Prometheus** | 2.48 | Metrics |
| **Grafana** | 10.2 | Dashboards |

---

## 🔧 Installation

### Development Setup

#### Backend Development

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

### Production Deployment

```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Update .env with production values
# - Strong passwords
# - Production URLs
# - SSL certificates

# Deploy with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Enable SSL (using Let's Encrypt)
docker exec iob_maiis_nginx certbot --nginx -d yourdomain.com
```

---

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Security (MUST CHANGE IN PRODUCTION!)
SECRET_KEY=your-32-char-secret-key
JWT_SECRET_KEY=your-32-char-jwt-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# LLM Models
LLM_MODEL=llama3.1:8b              # Main chat model
EMBEDDING_MODEL=nomic-embed-text    # Embedding model
VISION_MODEL=llava:13b              # Vision model

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
CHAT_RATE_LIMIT=30
```

### Model Configuration

Download additional Ollama models:

```bash
# Larger models (better quality, slower)
docker exec iob_maiis_ollama ollama pull llama3.1:70b
docker exec iob_maiis_ollama ollama pull llava:34b

# Smaller models (faster, less resource intensive)
docker exec iob_maiis_ollama ollama pull phi3:mini
docker exec iob_maiis_ollama ollama pull tinyllama
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_auth.py          # Authentication tests
pytest tests/test_rag.py           # RAG pipeline tests
pytest tests/test_banking.py       # Banking logic tests
pytest -m integration              # Integration tests only

# Run in parallel
pytest -n 4
```

### Frontend Tests

```bash
cd frontend

# Unit tests
npm test

# E2E tests
npm run test:e2e

# Watch mode
npm test -- --watch

# Coverage report
npm test -- --coverage
```

### Load Testing

```bash
# Install k6
brew install k6  # Mac
# or download from https://k6.io/

# Run load tests
k6 run tests/load/chat_endpoint.js
```

---

## 📊 Monitoring

### Grafana Dashboards

Access Grafana at http://localhost:3001

**Pre-configured Dashboards:**
- Application Performance
- Database Metrics
- API Response Times
- Error Rates
- Resource Usage (CPU, Memory, Disk)
- LLM Performance

### Prometheus Metrics

Access Prometheus at http://localhost:9090

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `db_connection_pool_size` - Database connections
- `llm_generation_time_seconds` - LLM response times
- `vector_search_duration_seconds` - Vector search performance

### Logs

```bash
# View all logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Backend application logs
tail -f backend/logs/application.log

# Access logs
tail -f nginx/logs/access.log
```

---

## 🔒 Security

### Security Features

✅ **Authentication & Authorization**
- JWT tokens with expiration
- Refresh token rotation
- Role-based access control
- Session management via Redis

✅ **Data Protection**
- bcrypt password hashing (12 rounds)
- Database encryption at rest
- TLS/SSL in production
- Secure cookie attributes

✅ **API Security**
- Rate limiting per endpoint
- Request validation with Pydantic
- SQL injection prevention
- XSS protection
- CSRF tokens

✅ **Monitoring & Audit**
- Complete audit trail
- Failed login tracking
- Suspicious activity detection
- Security event logging

### Security Best Practices

```bash
# 1. Change default passwords
# Edit .env and update all *_PASSWORD variables

# 2. Generate strong secrets
openssl rand -hex 32

# 3. Enable HTTPS in production
# Update nginx/nginx.conf with SSL certificates

# 4. Review CORS settings
ALLOWED_ORIGINS=https://yourdomain.com

# 5. Enable 2FA (optional)
ENABLE_2FA=true
```

### Compliance

- **GDPR**: Data retention policies, user data export/deletion
- **PCI DSS**: Secure payment processing (if enabled)
- **SOC 2**: Audit logging, access controls
- **HIPAA**: Data encryption, access logs (if healthcare data)

---

## 📚 API Documentation

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Spec**: http://localhost:8000/api/openapi.json

### Key Endpoints

#### Authentication
```http
POST /api/auth/signup          # Register new user
POST /api/auth/login           # Login
POST /api/auth/refresh         # Refresh access token
POST /api/auth/logout          # Logout
```

#### Chat & AI
```http
POST /api/chat/message         # Send chat message
GET  /api/chat/history         # Get chat history
WS   /api/chat/stream          # WebSocket streaming
POST /api/chat/voice           # Voice input
```

#### Banking
```http
GET  /api/banking/accounts     # List accounts
POST /api/banking/transfer     # Transfer funds
GET  /api/banking/transactions # Transaction history
GET  /api/banking/balance      # Check balance
```

#### Documents
```http
POST /api/documents/upload     # Upload document
POST /api/documents/ocr        # OCR processing
GET  /api/documents/list       # List documents
DELETE /api/documents/{id}     # Delete document
```

### Example Usage

```bash
# Register
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!","full_name":"John Doe"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'

# Chat (with token)
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is my account balance?"}'
```

---

## 🛠️ Development

### Project Structure

```
iob-maiis/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── auth/           # Authentication
│   │   ├── core/           # Core config
│   │   ├── db/             # Database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   └── scripts/            # Utility scripts
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   ├── store/         # State management
│   │   └── types/         # TypeScript types
│   └── tests/             # Frontend tests
├── data/                  # Data storage
├── docs/                  # Documentation
├── monitoring/            # Monitoring configs
├── nginx/                 # Nginx config
└── scripts/               # Setup scripts
```

### Adding New Features

1. **Backend API Endpoint**
```python
# backend/app/api/new_feature.py
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint(user = Depends(get_current_user)):
    return {"message": "New feature"}
```

2. **Frontend Component**
```typescript
// frontend/src/components/NewFeature.tsx
'use client'
import { useState } from 'react'

export function NewFeature() {
  const [data, setData] = useState(null)
  
  return <div>New Feature</div>
}
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Standards

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Follow ESLint rules
- **Tests**: Maintain 80%+ code coverage
- **Documentation**: Update README and API docs

---

## 📝 Changelog

### Version 1.0.0 (2025-01-17)
- Initial release
- RAG pipeline implementation
- Multimodal AI capabilities
- Banking core features
- Docker orchestration
- Comprehensive testing suite

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **Qdrant** - Vector database
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **LangChain** - LLM orchestration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/harish-msl/iob-maiis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/harish-msl/iob-maiis/discussions)
- **Email**: support@iobmaiis.local

---

## 🚀 Roadmap

- [ ] Mobile application (React Native)
- [ ] Multi-language support
- [ ] Advanced fraud detection ML models
- [ ] Blockchain integration
- [ ] Voice-only banking mode
- [ ] AR/VR banking interface
- [ ] API marketplace
- [ ] Plugin system

---

**Built with ❤️ by the IOB MAIIS Team**

*Powered by AI, Secured by Design, Built for the Future*
