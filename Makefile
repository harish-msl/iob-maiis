# ============================================
# IOB MAIIS - Makefile
# Multimodal AI-Enabled Information System
# Project Management Commands
# Created: 2025-01-17
# ============================================

.PHONY: help setup start stop restart logs clean build test install dev prod health backup restore docs

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := iob-maiis
DOCKER_COMPOSE := docker-compose
BACKEND_CONTAINER := iob_maiis_backend
FRONTEND_CONTAINER := iob_maiis_frontend
POSTGRES_CONTAINER := iob_maiis_postgres
REDIS_CONTAINER := iob_maiis_redis
QDRANT_CONTAINER := iob_maiis_qdrant
OLLAMA_CONTAINER := iob_maiis_ollama

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================
# HELP & INFORMATION
# ============================================

help: ## Show this help message
	@echo "$(CYAN)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║                                                           ║$(NC)"
	@echo "$(CYAN)║     IOB MAIIS - Project Management Commands              ║$(NC)"
	@echo "$(CYAN)║     Multimodal AI-Enabled Information System             ║$(NC)"
	@echo "$(CYAN)║                                                           ║$(NC)"
	@echo "$(CYAN)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================
# SETUP & INSTALLATION
# ============================================

setup: ## Complete project setup (first time)
	@echo "$(CYAN)🚀 Starting IOB MAIIS setup...$(NC)"
	@chmod +x setup.sh
	@./setup.sh

install: setup ## Alias for setup

init: ## Initialize environment file
	@echo "$(CYAN)📝 Initializing environment...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ .env file created from .env.example$(NC)"; \
		echo "$(YELLOW)⚠️  Please update .env with your configuration$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  .env file already exists$(NC)"; \
	fi

# ============================================
# DOCKER OPERATIONS
# ============================================

build: ## Build all Docker images
	@echo "$(CYAN)🔨 Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Build complete$(NC)"

pull: ## Pull latest Docker images
	@echo "$(CYAN)📦 Pulling Docker images...$(NC)"
	@$(DOCKER_COMPOSE) pull
	@echo "$(GREEN)✅ Images pulled$(NC)"

start: ## Start all services
	@echo "$(CYAN)▶️  Starting all services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ All services started$(NC)"
	@make health

stop: ## Stop all services
	@echo "$(CYAN)⏸️  Stopping all services...$(NC)"
	@$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)✅ All services stopped$(NC)"

down: ## Stop and remove all containers
	@echo "$(CYAN)🔽 Stopping and removing containers...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ All containers removed$(NC)"

restart: ## Restart all services
	@echo "$(CYAN)🔄 Restarting all services...$(NC)"
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ All services restarted$(NC)"

up: start ## Alias for start

# ============================================
# DEVELOPMENT
# ============================================

dev: ## Start in development mode
	@echo "$(CYAN)🛠️  Starting in development mode...$(NC)"
	@$(DOCKER_COMPOSE) up
	@echo "$(GREEN)✅ Development mode started$(NC)"

dev-backend: ## Start backend in dev mode
	@echo "$(CYAN)🛠️  Starting backend in development mode...$(NC)"
	@cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload

dev-frontend: ## Start frontend in dev mode
	@echo "$(CYAN)🛠️  Starting frontend in development mode...$(NC)"
	@cd frontend && npm install && npm run dev

# ============================================
# LOGS & MONITORING
# ============================================

logs: ## View logs from all services
	@$(DOCKER_COMPOSE) logs -f

logs-backend: ## View backend logs
	@$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## View frontend logs
	@$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## View database logs
	@$(DOCKER_COMPOSE) logs -f postgres

logs-redis: ## View Redis logs
	@$(DOCKER_COMPOSE) logs -f redis

logs-ollama: ## View Ollama logs
	@$(DOCKER_COMPOSE) logs -f ollama

ps: ## List running containers
	@$(DOCKER_COMPOSE) ps

status: ps ## Alias for ps

# ============================================
# HEALTH & TESTING
# ============================================

health: ## Check health of all services
	@echo "$(CYAN)🏥 Checking service health...$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend:$(NC)"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "$(RED)❌ Backend unhealthy$(NC)"
	@echo ""
	@echo "$(YELLOW)Frontend:$(NC)"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✅ Frontend healthy$(NC)" || echo "$(RED)❌ Frontend unhealthy$(NC)"
	@echo ""
	@echo "$(YELLOW)Prometheus:$(NC)"
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "$(GREEN)✅ Prometheus healthy$(NC)" || echo "$(RED)❌ Prometheus unhealthy$(NC)"
	@echo ""
	@echo "$(YELLOW)Grafana:$(NC)"
	@curl -s http://localhost:3001/api/health > /dev/null && echo "$(GREEN)✅ Grafana healthy$(NC)" || echo "$(RED)❌ Grafana unhealthy$(NC)"

test: ## Run all tests
	@echo "$(CYAN)🧪 Running all tests...$(NC)"
	@$(DOCKER_COMPOSE) exec backend pytest
	@echo "$(GREEN)✅ All tests passed$(NC)"

test-backend: ## Run backend tests
	@echo "$(CYAN)🧪 Running backend tests...$(NC)"
	@$(DOCKER_COMPOSE) exec backend pytest -v

test-coverage: ## Run tests with coverage report
	@echo "$(CYAN)🧪 Running tests with coverage...$(NC)"
	@$(DOCKER_COMPOSE) exec backend pytest --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	@echo "$(CYAN)🧪 Running frontend tests...$(NC)"
	@$(DOCKER_COMPOSE) exec frontend npm test

# ============================================
# DATABASE OPERATIONS
# ============================================

db-init: ## Initialize database
	@echo "$(CYAN)🗄️  Initializing database...$(NC)"
	@$(DOCKER_COMPOSE) exec backend python scripts/init_db.py
	@echo "$(GREEN)✅ Database initialized$(NC)"

db-migrate: ## Run database migrations
	@echo "$(CYAN)🗄️  Running database migrations...$(NC)"
	@$(DOCKER_COMPOSE) exec backend alembic upgrade head
	@echo "$(GREEN)✅ Migrations complete$(NC)"

db-rollback: ## Rollback last migration
	@echo "$(CYAN)🗄️  Rolling back last migration...$(NC)"
	@$(DOCKER_COMPOSE) exec backend alembic downgrade -1
	@echo "$(GREEN)✅ Rollback complete$(NC)"

db-shell: ## Open database shell
	@echo "$(CYAN)🗄️  Opening database shell...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres psql -U postgres -d iob_maiis_db

db-backup: ## Backup database
	@echo "$(CYAN)💾 Creating database backup...$(NC)"
	@mkdir -p data/backups
	@$(DOCKER_COMPOSE) exec -T postgres pg_dump -U postgres iob_maiis_db > data/backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup created$(NC)"

db-restore: ## Restore database from latest backup
	@echo "$(CYAN)♻️  Restoring database from latest backup...$(NC)"
	@$(DOCKER_COMPOSE) exec -T postgres psql -U postgres iob_maiis_db < $$(ls -t data/backups/*.sql | head -1)
	@echo "$(GREEN)✅ Database restored$(NC)"

# ============================================
# AI MODEL OPERATIONS
# ============================================

ollama-pull: ## Pull Ollama models
	@echo "$(CYAN)🤖 Pulling Ollama models...$(NC)"
	@$(DOCKER_COMPOSE) exec ollama ollama pull llama3.1:8b
	@$(DOCKER_COMPOSE) exec ollama ollama pull nomic-embed-text
	@echo "$(GREEN)✅ Models pulled$(NC)"

ollama-list: ## List installed Ollama models
	@echo "$(CYAN)🤖 Listing Ollama models...$(NC)"
	@$(DOCKER_COMPOSE) exec ollama ollama list

ollama-shell: ## Open Ollama shell
	@echo "$(CYAN)🤖 Opening Ollama shell...$(NC)"
	@$(DOCKER_COMPOSE) exec ollama bash

ingest: ## Ingest documents into vector database
	@echo "$(CYAN)📄 Ingesting documents...$(NC)"
	@$(DOCKER_COMPOSE) exec backend python scripts/ingest_documents.py
	@echo "$(GREEN)✅ Documents ingested$(NC)"

# ============================================
# SHELL ACCESS
# ============================================

shell-backend: ## Open backend shell
	@echo "$(CYAN)🐚 Opening backend shell...$(NC)"
	@$(DOCKER_COMPOSE) exec backend bash

shell-frontend: ## Open frontend shell
	@echo "$(CYAN)🐚 Opening frontend shell...$(NC)"
	@$(DOCKER_COMPOSE) exec frontend sh

shell-db: db-shell ## Alias for db-shell

shell-redis: ## Open Redis CLI
	@echo "$(CYAN)🐚 Opening Redis CLI...$(NC)"
	@$(DOCKER_COMPOSE) exec redis redis-cli

# ============================================
# CLEAN & RESET
# ============================================

clean: ## Clean up containers, volumes, and build artifacts
	@echo "$(CYAN)🧹 Cleaning up...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@rm -rf backend/__pycache__ backend/.pytest_cache backend/.coverage
	@rm -rf frontend/.next frontend/node_modules
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-volumes: ## Remove all Docker volumes (WARNING: destroys data)
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) down -v; \
		echo "$(GREEN)✅ Volumes removed$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled$(NC)"; \
	fi

clean-logs: ## Clean log files
	@echo "$(CYAN)🧹 Cleaning logs...$(NC)"
	@rm -rf backend/logs/*.log
	@rm -rf nginx/logs/*.log
	@echo "$(GREEN)✅ Logs cleaned$(NC)"

reset: clean setup ## Complete reset and setup

# ============================================
# PRODUCTION OPERATIONS
# ============================================

prod: ## Start in production mode
	@echo "$(CYAN)🚀 Starting in production mode...$(NC)"
	@export ENVIRONMENT=production DEBUG=false
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production mode started$(NC)"

prod-build: ## Build for production
	@echo "$(CYAN)🔨 Building for production...$(NC)"
	@export ENVIRONMENT=production DEBUG=false
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml build
	@echo "$(GREEN)✅ Production build complete$(NC)"

# ============================================
# UTILITIES
# ============================================

lint-backend: ## Lint backend code
	@echo "$(CYAN)🔍 Linting backend code...$(NC)"
	@$(DOCKER_COMPOSE) exec backend black app/
	@$(DOCKER_COMPOSE) exec backend flake8 app/
	@$(DOCKER_COMPOSE) exec backend mypy app/

lint-frontend: ## Lint frontend code
	@echo "$(CYAN)🔍 Linting frontend code...$(NC)"
	@$(DOCKER_COMPOSE) exec frontend npm run lint

format: ## Format all code
	@echo "$(CYAN)✨ Formatting code...$(NC)"
	@$(DOCKER_COMPOSE) exec backend black app/
	@$(DOCKER_COMPOSE) exec backend isort app/
	@$(DOCKER_COMPOSE) exec frontend npm run format

docs: ## Generate documentation
	@echo "$(CYAN)📚 Generating documentation...$(NC)"
	@echo "$(YELLOW)Not implemented yet$(NC)"

update: ## Update all dependencies
	@echo "$(CYAN)📦 Updating dependencies...$(NC)"
	@$(DOCKER_COMPOSE) pull
	@$(DOCKER_COMPOSE) exec backend pip install --upgrade -r requirements.txt
	@$(DOCKER_COMPOSE) exec frontend npm update
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

# ============================================
# ACCESS URLs
# ============================================

urls: ## Display all access URLs
	@echo "$(CYAN)🌐 Access URLs:$(NC)"
	@echo ""
	@echo "  $(GREEN)Frontend:$(NC)        http://localhost:3000"
	@echo "  $(GREEN)Backend API:$(NC)     http://localhost:8000"
	@echo "  $(GREEN)API Docs:$(NC)        http://localhost:8000/api/docs"
	@echo "  $(GREEN)Grafana:$(NC)         http://localhost:3001"
	@echo "  $(GREEN)Prometheus:$(NC)      http://localhost:9090"
	@echo "  $(GREEN)PgAdmin:$(NC)         http://localhost:5050 (--profile tools)"
	@echo ""

info: urls ## Alias for urls

# ============================================
# MONITORING & METRICS
# ============================================

metrics: ## View Prometheus metrics
	@echo "$(CYAN)📊 Fetching metrics...$(NC)"
	@curl -s http://localhost:8000/metrics

grafana-password: ## Reset Grafana admin password
	@echo "$(CYAN)🔐 Resetting Grafana password...$(NC)"
	@$(DOCKER_COMPOSE) exec grafana grafana-cli admin reset-admin-password admin
	@echo "$(GREEN)✅ Password reset to 'admin'$(NC)"

# ============================================
# BACKUP & RESTORE
# ============================================

backup: db-backup ## Create full backup
	@echo "$(CYAN)💾 Creating full backup...$(NC)"
	@mkdir -p data/backups
	@tar -czf data/backups/full_backup_$$(date +%Y%m%d_%H%M%S).tar.gz data/documents data/knowledge_base
	@echo "$(GREEN)✅ Full backup created$(NC)"

restore-full: ## Restore from full backup
	@echo "$(CYAN)♻️  Restoring from full backup...$(NC)"
	@tar -xzf $$(ls -t data/backups/full_backup_*.tar.gz | head -1) -C /
	@echo "$(GREEN)✅ Full restore complete$(NC)"

# ============================================
# QUICK SHORTCUTS
# ============================================

q: down ## Quick shutdown

s: start ## Quick start

r: restart ## Quick restart

l: logs ## Quick logs

h: health ## Quick health check

t: test ## Quick test
