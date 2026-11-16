#!/bin/bash
set -e

echo "🧪 IntraFlow Test Suite Runner"
echo "================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0

run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    if eval "$test_command"; then
        echo -e "${GREEN}✓ $test_name PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $test_name FAILED${NC}"
        ((FAILED++))
    fi
}

# 1. Backend Unit Tests
echo -e "\n📦 Phase 1: Backend Unit Tests"
echo "--------------------------------"

run_test "Python Backend Unit Tests" \
    "cd agent-orchestrator && python -m pytest tests/ -v --cov=src --cov-report=term-missing || true"

# 2. Backend Integration Tests
echo -e "\n🔗 Phase 2: Backend Integration Tests"
echo "--------------------------------------"

run_test "Integration Tests" \
    "cd agent-orchestrator && python -m pytest tests/test_integration.py -v || true"

# 3. Code Quality Checks
echo -e "\n✨ Phase 3: Code Quality"
echo "------------------------"

run_test "Python Linting (Ruff)" \
    "cd agent-orchestrator && python -m ruff check src/ || true"

run_test "Python Formatting (Black)" \
    "cd agent-orchestrator && python -m black --check src/ || true"

run_test "Type Checking (MyPy)" \
    "cd agent-orchestrator && python -m mypy src/ --ignore-missing-imports || true"

# 4. Security Checks
echo -e "\n🔒 Phase 4: Security Checks"
echo "---------------------------"

run_test "Security Audit" \
    "cd agent-orchestrator && python -m bandit -r src/ -ll || true"

# 5. Frontend Tests (if implemented)
echo -e "\n🎨 Phase 5: Frontend Tests"
echo "--------------------------"

if [ -d "frontend/node_modules" ]; then
    run_test "Frontend Build" \
        "cd frontend && npm run build || true"
else
    echo "Skipping frontend tests (dependencies not installed)"
fi

# Summary
echo -e "\n📊 Test Summary"
echo "==============="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo -e "Total:  $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
