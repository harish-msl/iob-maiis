#!/bin/bash
# ============================================
# IOB MAIIS - SSL/TLS Certificate Setup
# Let's Encrypt with Certbot & Auto-Renewal
# Updated: 2025-01-17
# ============================================

set -e

# ============================================
# CONFIGURATION
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DOMAIN="${DOMAIN:-iobmaiis.com}"
EMAIL="${SSL_EMAIL:-admin@iobmaiis.com}"
STAGING="${STAGING:-false}"
CERT_DIR="./nginx/ssl"
WWW_DIR="./nginx/www"
NGINX_CONTAINER="iob_maiis_nginx"
COMPOSE_FILE="./docker-compose.yml"

# ============================================
# FUNCTIONS
# ============================================

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"

    # Check if running as root (needed for certbot)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is required for certbot."
    fi

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"

    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        print_warning "Certbot is not installed. Installing via snap..."

        if command -v snap &> /dev/null; then
            sudo snap install --classic certbot
            sudo ln -sf /snap/bin/certbot /usr/bin/certbot
            print_success "Certbot installed successfully"
        else
            print_error "Snap is not available. Please install certbot manually:"
            print_info "  Ubuntu/Debian: sudo apt-get install certbot"
            print_info "  CentOS/RHEL: sudo yum install certbot"
            print_info "  macOS: brew install certbot"
            exit 1
        fi
    else
        print_success "Certbot is installed"
    fi
}

create_directories() {
    print_header "Creating Required Directories"

    mkdir -p "$CERT_DIR/live/$DOMAIN"
    mkdir -p "$CERT_DIR/archive/$DOMAIN"
    mkdir -p "$WWW_DIR/.well-known/acme-challenge"

    print_success "Directories created"
}

generate_self_signed_cert() {
    print_header "Generating Self-Signed Certificate (Development)"

    if [[ -f "$CERT_DIR/selfsigned.crt" ]]; then
        print_warning "Self-signed certificate already exists. Skipping..."
        return
    fi

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERT_DIR/selfsigned.key" \
        -out "$CERT_DIR/selfsigned.crt" \
        -subj "/C=US/ST=State/L=City/O=IOB MAIIS/OU=IT/CN=$DOMAIN"

    print_success "Self-signed certificate generated"
    print_info "Certificate: $CERT_DIR/selfsigned.crt"
    print_info "Key: $CERT_DIR/selfsigned.key"
}

generate_dhparam() {
    print_header "Generating DH Parameters (2048 bit)"

    if [[ -f "$CERT_DIR/dhparam.pem" ]]; then
        print_warning "DH parameters already exist. Skipping..."
        return
    fi

    print_info "This may take several minutes..."
    openssl dhparam -out "$CERT_DIR/dhparam.pem" 2048

    print_success "DH parameters generated"
}

obtain_letsencrypt_cert() {
    print_header "Obtaining Let's Encrypt Certificate"

    # Prepare certbot command
    CERTBOT_CMD="certbot certonly --webroot"
    CERTBOT_CMD="$CERTBOT_CMD --webroot-path=$WWW_DIR"
    CERTBOT_CMD="$CERTBOT_CMD --email $EMAIL"
    CERTBOT_CMD="$CERTBOT_CMD --agree-tos"
    CERTBOT_CMD="$CERTBOT_CMD --no-eff-email"
    CERTBOT_CMD="$CERTBOT_CMD -d $DOMAIN"

    # Add staging flag if needed
    if [[ "$STAGING" == "true" ]]; then
        CERTBOT_CMD="$CERTBOT_CMD --staging"
        print_warning "Using Let's Encrypt staging environment"
    fi

    # Non-interactive mode
    CERTBOT_CMD="$CERTBOT_CMD --non-interactive"

    print_info "Running: $CERTBOT_CMD"

    # Execute certbot
    if eval $CERTBOT_CMD; then
        print_success "Certificate obtained successfully"

        # Copy certificates to nginx directory
        cp -L "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/live/$DOMAIN/"
        cp -L "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/live/$DOMAIN/"
        cp -L "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$CERT_DIR/live/$DOMAIN/"

        print_success "Certificates copied to nginx directory"
    else
        print_error "Failed to obtain certificate"
        print_info "Falling back to self-signed certificate for development"
        generate_self_signed_cert
        return 1
    fi
}

setup_auto_renewal() {
    print_header "Setting Up Auto-Renewal"

    # Create renewal script
    RENEWAL_SCRIPT="/etc/cron.monthly/certbot-renew"

    cat > "$RENEWAL_SCRIPT" << 'EOF'
#!/bin/bash
# Auto-renew Let's Encrypt certificates

certbot renew --quiet --post-hook "docker restart iob_maiis_nginx"

# Copy renewed certificates
DOMAIN="${DOMAIN:-iobmaiis.com}"
CERT_DIR="./nginx/ssl"

if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    cp -L "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERT_DIR/live/$DOMAIN/"
    cp -L "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$CERT_DIR/live/$DOMAIN/"
    cp -L "/etc/letsencrypt/live/$DOMAIN/chain.pem" "$CERT_DIR/live/$DOMAIN/"
fi
EOF

    chmod +x "$RENEWAL_SCRIPT"

    # Add to crontab (run twice daily as recommended by Let's Encrypt)
    CRON_CMD="0 0,12 * * * $RENEWAL_SCRIPT"

    if ! crontab -l 2>/dev/null | grep -q "$RENEWAL_SCRIPT"; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        print_success "Auto-renewal configured (runs twice daily)"
    else
        print_warning "Auto-renewal already configured"
    fi

    # Test renewal
    print_info "Testing certificate renewal..."
    if certbot renew --dry-run; then
        print_success "Renewal test passed"
    else
        print_warning "Renewal test failed. Please check configuration."
    fi
}

reload_nginx() {
    print_header "Reloading Nginx"

    if docker ps --format '{{.Names}}' | grep -q "$NGINX_CONTAINER"; then
        docker restart "$NGINX_CONTAINER"
        print_success "Nginx reloaded"
    else
        print_warning "Nginx container not running. Skipping reload."
    fi
}

verify_ssl() {
    print_header "Verifying SSL Configuration"

    print_info "Checking certificate expiry..."

    if [[ -f "$CERT_DIR/live/$DOMAIN/fullchain.pem" ]]; then
        EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_DIR/live/$DOMAIN/fullchain.pem" | cut -d= -f2)
        print_success "Certificate expires: $EXPIRY"
    fi

    print_info "Testing SSL handshake..."
    if echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | grep -q "Verify return code: 0"; then
        print_success "SSL handshake successful"
    else
        print_warning "SSL handshake test could not be completed"
        print_info "This is normal if the server is not publicly accessible yet"
    fi
}

display_summary() {
    print_header "SSL Setup Complete!"

    echo ""
    print_success "SSL/TLS certificates configured successfully"
    echo ""
    print_info "Certificate location: $CERT_DIR/live/$DOMAIN/"
    print_info "Domain: $DOMAIN"
    print_info "Email: $EMAIL"
    echo ""
    print_info "Auto-renewal is configured and will run twice daily"
    echo ""
    print_warning "IMPORTANT SECURITY NOTES:"
    echo "  1. Ensure port 80 and 443 are open in your firewall"
    echo "  2. DNS records for $DOMAIN must point to this server"
    echo "  3. Update nginx configuration to use the new certificates"
    echo "  4. Test HTTPS access: https://$DOMAIN"
    echo ""
    print_info "To manually renew certificates, run:"
    echo "  sudo certbot renew"
    echo ""
    print_info "To test renewal (dry-run):"
    echo "  sudo certbot renew --dry-run"
    echo ""
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Setup SSL/TLS certificates for IOB MAIIS using Let's Encrypt

OPTIONS:
    -d, --domain DOMAIN         Domain name (default: iobmaiis.com)
    -e, --email EMAIL           Email for Let's Encrypt notifications
    -s, --staging               Use Let's Encrypt staging environment
    --self-signed               Generate self-signed certificate only
    --renew                     Renew existing certificates
    -h, --help                  Show this help message

EXAMPLES:
    # Generate self-signed certificate for development
    $0 --self-signed

    # Obtain Let's Encrypt certificate for production
    $0 -d example.com -e admin@example.com

    # Test with Let's Encrypt staging
    $0 -d example.com -e admin@example.com --staging

    # Renew existing certificates
    $0 --renew

ENVIRONMENT VARIABLES:
    DOMAIN                      Domain name
    SSL_EMAIL                   Email address
    STAGING                     Use staging (true/false)

EOF
}

# ============================================
# MAIN
# ============================================

main() {
    MODE="production"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -e|--email)
                EMAIL="$2"
                shift 2
                ;;
            -s|--staging)
                STAGING="true"
                shift
                ;;
            --self-signed)
                MODE="self-signed"
                shift
                ;;
            --renew)
                MODE="renew"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    print_header "IOB MAIIS - SSL/TLS Setup"

    # Always check requirements
    check_requirements

    # Create directories
    create_directories

    # Generate DH parameters
    generate_dhparam

    # Execute based on mode
    case $MODE in
        self-signed)
            generate_self_signed_cert
            display_summary
            ;;
        renew)
            print_header "Renewing Certificates"
            certbot renew
            reload_nginx
            verify_ssl
            print_success "Certificate renewal complete"
            ;;
        production)
            # Try to obtain Let's Encrypt certificate
            if obtain_letsencrypt_cert; then
                setup_auto_renewal
                reload_nginx
                verify_ssl
                display_summary
            else
                print_warning "Could not obtain Let's Encrypt certificate"
                print_info "Using self-signed certificate for development"
            fi
            ;;
    esac
}

# Run main function
main "$@"
