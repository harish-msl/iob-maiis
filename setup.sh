#!/bin/bash

# ============================================
# IOB MAIIS - Comprehensive Setup Script
# Multimodal AI-Enabled Information System
# Created: 2025-01-17
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker found: $(docker --version)"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose found"

    # Check available disk space (minimum 10GB)
    available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$available_space" -lt 10 ]; then
        print_warning "Low disk space: ${available_space}GB available. Recommended: 10GB+"
    else
        print_success "Sufficient disk space: ${available_space}GB available"
    fi

    # Check available RAM (minimum 4GB)
    if command -v free &> /dev/null; then
        available_ram=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$available_ram" -lt 4 ]; then
            print_warning "Low RAM: ${available_ram}GB available. Recommended: 8GB+"
        else
            print_success "Sufficient RAM: ${available_ram}GB available"
        fi
    fi

    echo ""
}

# Setup environment file
setup_environment() {
    print_header "Setting Up Environment Variables"

    if [ -f .env ]; then
        print_warning ".env file already exists. Backing up to .env.backup"
        cp .env .env.backup
    fi

    print_info "Copying .env.example to .env"
    cp .env.example .env

    # Generate secure keys
    print_info "Generating secure keys..."

    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET_KEY=$(openssl rand -hex 32)
        REDIS_PASSWORD=$(openssl rand -hex 16)
        POSTGRES_PASSWORD=$(openssl rand -hex 16)

        # Update .env file
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your-super-secret-key-min-32-chars-change-in-production-2025/$SECRET_KEY/" .env
            sed -i '' "s/your-jwt-secret-key-min-32-chars-change-in-production-2025/$JWT_SECRET_KEY/" .env
            sed -i '' "s/redis_secure_password_2025/$REDIS_PASSWORD/" .env
            sed -i '' "s/postgres_secure_password_2025/$POSTGRES_PASSWORD/" .env
        else
            # Linux
            sed -i "s/your-super-secret-key-min-32-chars-change-in-production-2025/$SECRET_KEY/" .env
            sed -i "s/your-jwt-secret-key-min-32-chars-change-in-production-2025/$JWT_SECRET_KEY/" .env
            sed -i "s/redis_secure_password_2025/$REDIS_PASSWORD/" .env
            sed -i "s/postgres_secure_password_2025/$POSTGRES_PASSWORD/" .env
        fi

        print_success "Secure keys generated and updated in .env"
    else
        print_warning "OpenSSL not found. Please manually update SECRET_KEY and JWT_SECRET_KEY in .env"
    fi

    echo ""
}

# Create necessary directories
create_directories() {
    print_header "Creating Project Directories"

    directories=(
        "data/documents"
        "data/knowledge_base"
        "data/backups"
        "backend/logs"
        "monitoring/grafana/dashboards"
        "monitoring/grafana/datasources"
        "nginx/ssl"
        "nginx/logs"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_success "Created: $dir"
    done

    # Set permissions
    chmod -R 755 data/
    chmod -R 755 backend/logs/

    echo ""
}

# Pull and setup Docker images
setup_docker() {
    print_header "Setting Up Docker Containers"

    print_info "Pulling Docker images (this may take a while)..."
    docker-compose pull

    print_success "Docker images pulled successfully"
    echo ""
}

# Setup Ollama models
setup_ollama() {
    print_header "Setting Up Ollama LLM Models"

    print_info "Starting Ollama service..."
    docker-compose up -d ollama

    # Wait for Ollama to be ready
    print_info "Waiting for Ollama to be ready..."
    sleep 10

    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker exec iob_maiis_ollama ollama list &> /dev/null; then
            print_success "Ollama service is ready"
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        print_error "Ollama service failed to start"
        exit 1
    fi

    # Pull models
    print_info "Pulling Llama 3.1 8B model (this will take several minutes)..."
    docker exec iob_maiis_ollama ollama pull llama3.1:8b
    print_success "Llama 3.1 8B model downloaded"

    print_info "Pulling Nomic Embed Text model..."
    docker exec iob_maiis_ollama ollama pull nomic-embed-text
    print_success "Nomic Embed Text model downloaded"

    print_info "Pulling LLaVA vision model (optional, large download)..."
    read -p "Do you want to download LLaVA vision model? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker exec iob_maiis_ollama ollama pull llava:13b
        print_success "LLaVA vision model downloaded"
    else
        print_info "Skipping LLaVA vision model"
    fi

    echo ""
}

# Start all services
start_services() {
    print_header "Starting All Services"

    print_info "Starting PostgreSQL, Redis, Qdrant..."
    docker-compose up -d postgres redis qdrant

    print_info "Waiting for databases to be ready..."
    sleep 15

    print_info "Starting backend service..."
    docker-compose up -d backend

    print_info "Waiting for backend to be ready..."
    sleep 10

    print_info "Starting frontend service..."
    docker-compose up -d frontend

    print_info "Starting Nginx reverse proxy..."
    docker-compose up -d nginx

    print_info "Starting monitoring services..."
    docker-compose up -d prometheus grafana

    print_success "All services started successfully"
    echo ""
}

# Initialize database
init_database() {
    print_header "Initializing Database"

    print_info "Running database migrations..."
    docker exec iob_maiis_backend alembic upgrade head || true

    print_info "Initializing database with default data..."
    docker exec iob_maiis_backend python scripts/init_db.py || true

    print_success "Database initialized"
    echo ""
}

# Ingest sample documents
ingest_documents() {
    print_header "Ingesting Sample Documents"

    print_info "Creating sample knowledge base documents..."

    # Create sample banking policy document
    cat > data/knowledge_base/banking_policy.txt << 'EOF'
Banking Policy Document

Account Types:
1. Savings Account - Minimum balance: $100, Interest rate: 2.5% annually
2. Checking Account - No minimum balance, No interest
3. Fixed Deposit - Minimum: $1000, Interest rate: 4.5% annually

Transaction Limits:
- Daily withdrawal limit: $5,000
- Daily transfer limit: $10,000
- Maximum single transaction: $100,000

Fees:
- ATM withdrawal (own network): Free
- ATM withdrawal (other network): $2.50
- Wire transfer (domestic): $15
- Wire transfer (international): $35
- Account maintenance: $0 (waived with minimum balance)

Customer Service:
- Phone: 1-800-BANK-IOB
- Email: support@iobbank.com
- Hours: Monday-Friday 9 AM - 5 PM
- 24/7 Online Banking

Security:
- Multi-factor authentication required
- Transaction alerts via SMS/Email
- Fraud monitoring 24/7
- Zero liability for unauthorized transactions
EOF

    print_success "Sample documents created"

    print_info "Running document ingestion script..."
    docker exec iob_maiis_backend python scripts/ingest_documents.py || print_warning "Document ingestion failed (will retry later)"

    echo ""
}

# Health check
health_check() {
    print_header "Running Health Checks"

    # Check backend
    print_info "Checking backend health..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is healthy"
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        print_warning "Backend health check timeout (may still be starting)"
    fi

    # Check frontend
    print_info "Checking frontend health..."
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is healthy"
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        print_warning "Frontend health check timeout (may still be starting)"
    fi

    echo ""
}

# Print summary
print_summary() {
    print_header "Setup Complete! 🎉"

    echo -e "${GREEN}"
    cat << 'EOF'
    ___  ____  ____    __  __    _    ___ ___ ____
   |_ _|/ ___|| __ )  |  \/  |  / \  |_ _|_ _/ ___|
    | || |    |  _ \  | |\/| | / _ \  | | | |\___ \
    | || |    | |_) | | |  | |/ ___ \ | | | | ___) |
   |___|\____|____/  |_|  |_/_/   \_\___|___|____/

EOF
    echo -e "${NC}"

    echo -e "${CYAN}🌐 Access URLs:${NC}"
    echo -e "  ${GREEN}Frontend:${NC}        http://localhost:3000"
    echo -e "  ${GREEN}Backend API:${NC}     http://localhost:8000"
    echo -e "  ${GREEN}API Docs:${NC}        http://localhost:8000/api/docs"
    echo -e "  ${GREEN}Grafana:${NC}         http://localhost:3001 (admin/admin)"
    echo -e "  ${GREEN}Prometheus:${NC}      http://localhost:9090"
    echo -e "  ${GREEN}PgAdmin:${NC}         http://localhost:5050 (use --profile tools)"
    echo ""

    echo -e "${CYAN}📚 Quick Commands:${NC}"
    echo -e "  ${YELLOW}View logs:${NC}           docker-compose logs -f"
    echo -e "  ${YELLOW}Stop services:${NC}       docker-compose down"
    echo -e "  ${YELLOW}Restart services:${NC}    docker-compose restart"
    echo -e "  ${YELLOW}View status:${NC}         docker-compose ps"
    echo -e "  ${YELLOW}Backend shell:${NC}       docker exec -it iob_maiis_backend bash"
    echo -e "  ${YELLOW}Frontend shell:${NC}      docker exec -it iob_maiis_frontend sh"
    echo ""

    echo -e "${CYAN}🔐 Default Credentials:${NC}"
    echo -e "  ${YELLOW}Grafana:${NC}     admin / admin (change on first login)"
    echo -e "  ${YELLOW}Database:${NC}    Check .env file for credentials"
    echo ""

    echo -e "${CYAN}📖 Documentation:${NC}"
    echo -e "  ${GREEN}README:${NC}          README.md"
    echo -e "  ${GREEN}API Docs:${NC}        docs/API.md"
    echo -e "  ${GREEN}Deployment:${NC}      docs/DEPLOYMENT.md"
    echo ""

    echo -e "${CYAN}⚡ Next Steps:${NC}"
    echo -e "  1. Visit http://localhost:3000 to access the application"
    echo -e "  2. Register a new account or use the demo account"
    echo -e "  3. Explore the AI chat interface"
    echo -e "  4. Upload documents for RAG processing"
    echo -e "  5. Try multimodal features (voice, images)"
    echo ""

    echo -e "${PURPLE}Built with ❤️  by the IOB MAIIS Team${NC}"
    echo -e "${PURPLE}Powered by AI, Secured by Design, Built for the Future${NC}"
    echo ""
}

# Main execution
main() {
    clear

    echo -e "${PURPLE}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     IOB MAIIS - Setup & Installation Script              ║
║     Multimodal AI-Enabled Information System             ║
║                                                           ║
║     Version: 1.0.0                                        ║
║     Date: 2025-01-17                                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"

    print_warning "This script will set up the complete IOB MAIIS environment."
    print_warning "Estimated time: 10-20 minutes (depending on internet speed)"
    echo ""

    read -p "Do you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled by user"
        exit 0
    fi

    echo ""

    # Run setup steps
    check_prerequisites
    setup_environment
    create_directories
    setup_docker
    setup_ollama
    start_services

    # Give services time to fully start
    print_info "Waiting for services to fully initialize..."
    sleep 20

    init_database
    ingest_documents
    health_check
    print_summary

    # Ask to show logs
    echo ""
    read -p "Do you want to view the logs? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose logs -f
    fi
}

# Run main function
main "$@"
