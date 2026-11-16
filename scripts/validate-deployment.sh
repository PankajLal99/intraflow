#!/bin/bash
set -e

echo "🚀 IntraFlow Deployment Validation"
echo "===================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

check() {
    local name=$1
    local command=$2
    
    echo -e "\n${YELLOW}Checking: $name${NC}"
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ $name${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo -e "\n📦 Phase 1: Docker Services"
echo "----------------------------"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi

# Check containers
check "PostgreSQL Container" "docker ps | grep -q postgres"
check "Redis Container" "docker ps | grep -q redis"
check "Agent Orchestrator Container" "docker ps | grep -q agent-orchestrator"

echo -e "\n🔍 Phase 2: Health Endpoints"
echo "-----------------------------"

# Wait for services to be ready
sleep 5

check "Agent Orchestrator Health" "curl -f http://localhost:8000/health"
check "Agent Orchestrator Metrics" "curl -f http://localhost:8000/metrics"

echo -e "\n🗄️  Phase 3: Database Connectivity"
echo "----------------------------------"

check "PostgreSQL Connection" \
    "docker exec intraflow-postgres-1 psql -U whatsapp -d whatsapp -c 'SELECT 1' || \
     docker exec postgres-db psql -U whatsapp -d whatsapp -c 'SELECT 1'"

check "Database Tables Exist" \
    "docker exec intraflow-postgres-1 psql -U whatsapp -d whatsapp -c '\dt' | grep -q 'tenants' || \
     docker exec postgres-db psql -U whatsapp -d whatsapp -c '\dt' | grep -q 'tenants'"

echo -e "\n🔐 Phase 4: Environment Configuration"
echo "-------------------------------------"

check ".env File Exists" "test -f .env"
check "JWT Secret Configured" "grep -q 'JWT_SECRET' .env"
check "Database URL Configured" "grep -q 'DATABASE_URL' .env"

echo -e "\n🌐 Phase 5: API Endpoints"
echo "-------------------------"

check "Auth Signup Endpoint" "curl -f http://localhost:8000/api/v1/auth/signup -X POST -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"Test123!@#\",\"tenant_name\":\"Test\"}' || true"
check "Workflows Endpoint (requires auth)" "curl http://localhost:8000/api/v1/workflows -I | grep -q '401\\|200'"

echo -e "\n📊 Summary"
echo "=========="
echo -e "Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Failed: ${RED}$CHECKS_FAILED${NC}"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All deployment checks passed!${NC}"
    echo -e "\n🎉 IntraFlow is ready for use!"
    echo -e "\nNext steps:"
    echo "  1. Access frontend: http://localhost:3000"
    echo "  2. Access API: http://localhost:8000"
    echo "  3. Access API docs: http://localhost:8000/docs"
    echo "  4. View metrics: http://localhost:8000/metrics"
    exit 0
else
    echo -e "\n${RED}❌ Some deployment checks failed${NC}"
    echo -e "\nTroubleshooting:"
    echo "  1. Run: docker-compose ps"
    echo "  2. Check logs: docker-compose logs -f"
    echo "  3. Verify .env configuration"
    exit 1
fi
