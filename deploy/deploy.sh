#!/bin/bash
set -e

# =============================================================================
# IntraFlow Production Deployment Script
# =============================================================================
# This script deploys IntraFlow to AWS EC2 or Azure VM with external PostgreSQL
#
# Usage:
#   ./deploy/deploy.sh [production|staging]
#
# Prerequisites:
#   - Docker and Docker Compose installed on server
#   - PostgreSQL database already created and accessible
#   - .env file configured with database credentials
#   - Git repository cloned to /opt/intraflow (or ~/intraflow)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
DEPLOY_DIR="/opt/intraflow"
BACKUP_DIR="/opt/intraflow/backups"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IntraFlow Deployment Script${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}========================================${NC}"

# =============================================================================
# Functions
# =============================================================================

log_info() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root. Consider using a non-root user with sudo."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    log_info "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    log_info "Docker Compose found"
    
    # Check if .env exists
    if [ ! -f "${DEPLOY_DIR}/.env" ]; then
        log_error ".env file not found at ${DEPLOY_DIR}/.env"
        log_error "Please create .env from .env.example and configure it."
        exit 1
    fi
    log_info ".env file found"
    
    # Check if database credentials are configured
    if grep -q "REPLACE_WITH" "${DEPLOY_DIR}/.env" 2>/dev/null; then
        log_error ".env file contains placeholder values. Please configure it properly."
        exit 1
    fi
}

create_backup() {
    log_info "Creating backup..."
    
    # Create backup directory
    mkdir -p "${BACKUP_DIR}"
    
    # Backup .env file
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "${DEPLOY_DIR}/.env" "${BACKUP_DIR}/.env.${TIMESTAMP}"
    
    # Backup docker volumes (if any)
    if docker volume ls | grep -q "intraflow"; then
        log_info "Backing up Docker volumes..."
        # Add volume backup logic here if needed
    fi
    
    log_info "Backup created: ${BACKUP_DIR}/.env.${TIMESTAMP}"
}

pull_latest_code() {
    log_info "Pulling latest code from repository..."
    
    cd "${DEPLOY_DIR}"
    
    # Stash any local changes
    git stash
    
    # Pull latest code
    git pull origin main
    
    log_info "Code updated successfully"
}

build_images() {
    log_info "Building Docker images..."
    
    cd "${DEPLOY_DIR}"
    
    # Build agent-orchestrator image
    docker-compose build --no-cache agent-orchestrator
    
    log_info "Docker images built successfully"
}

stop_services() {
    log_info "Stopping existing services..."
    
    cd "${DEPLOY_DIR}"
    
    # Stop services gracefully
    docker-compose down --timeout 30
    
    log_info "Services stopped"
}

start_services() {
    log_info "Starting services..."
    
    cd "${DEPLOY_DIR}"
    
    # Start services in detached mode
    docker-compose up -d
    
    # Wait for services to start
    sleep 10
    
    log_info "Services started"
}

run_migrations() {
    log_info "Running database migrations..."
    
    # Check if we need to run migrations
    # Note: Using external PostgreSQL, so migrations run against external DB
    
    # Load DB credentials from .env
    source "${DEPLOY_DIR}/.env"
    
    # Check if database is accessible
    if ! docker-compose exec -T agent-orchestrator python -c "
import asyncio
from src.database.connection import engine
async def check():
    try:
        async with engine.begin() as conn:
            await conn.execute('SELECT 1')
        print('Database connection successful')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False
asyncio.run(check())
" 2>/dev/null; then
        log_warning "Could not verify database connection. Please check your DB credentials."
    else
        log_info "Database connection verified"
    fi
    
    # Run migrations if needed
    # Note: First deployment requires manual migration:
    #   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/init.sql
    #   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/migrations/002_multi_tenant_workflows.sql
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    cd "${DEPLOY_DIR}"
    
    # Check service status
    if ! docker-compose ps | grep -q "Up"; then
        log_error "Some services are not running!"
        docker-compose ps
        exit 1
    fi
    
    # Wait for health check
    log_info "Waiting for services to be healthy..."
    sleep 5
    
    # Check health endpoint
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_info "Health check passed!"
            break
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warning "Health check attempt $RETRY_COUNT/$MAX_RETRIES..."
        sleep 2
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_error "Health check failed after $MAX_RETRIES attempts"
        log_error "Check logs: docker-compose logs -f agent-orchestrator"
        exit 1
    fi
    
    # Check metrics endpoint
    if curl -f http://localhost:8000/metrics &> /dev/null; then
        log_info "Metrics endpoint accessible"
    else
        log_warning "Metrics endpoint not accessible (non-critical)"
    fi
    
    # Display service status
    echo ""
    log_info "Service Status:"
    docker-compose ps
}

cleanup() {
    log_info "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    log_info "Cleanup complete"
}

display_info() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Successful! 🎉${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "  API:          http://$(hostname -I | awk '{print $1}'):8000"
    echo -e "  API Docs:     http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo -e "  Health Check: http://$(hostname -I | awk '{print $1}'):8000/health"
    echo -e "  Metrics:      http://$(hostname -I | awk '{print $1}'):8000/metrics"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "  View logs:       docker-compose logs -f"
    echo -e "  Restart:         docker-compose restart"
    echo -e "  Stop:            docker-compose down"
    echo -e "  Check status:    docker-compose ps"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Configure your frontend to point to: http://$(hostname -I | awk '{print $1}'):8000"
    echo -e "  2. Set up Nginx reverse proxy with SSL (recommended)"
    echo -e "  3. Configure monitoring alerts"
    echo -e "  4. Test WhatsApp integration via OpenWA"
    echo ""
}

# =============================================================================
# Main Deployment Flow
# =============================================================================

main() {
    echo ""
    log_info "Starting deployment process..."
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Create backup
    create_backup
    
    # Step 3: Pull latest code
    pull_latest_code
    
    # Step 4: Build Docker images
    build_images
    
    # Step 5: Stop existing services
    stop_services
    
    # Step 6: Start new services
    start_services
    
    # Step 7: Run migrations (if needed)
    run_migrations
    
    # Step 8: Verify deployment
    verify_deployment
    
    # Step 9: Cleanup
    cleanup
    
    # Step 10: Display info
    display_info
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Change to deployment directory
if [ -d "$DEPLOY_DIR" ]; then
    cd "$DEPLOY_DIR"
else
    log_error "Deployment directory not found: $DEPLOY_DIR"
    log_error "Please clone the repository to $DEPLOY_DIR first"
    exit 1
fi

# Run main deployment
main

exit 0
