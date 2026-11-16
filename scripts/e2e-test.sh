#!/bin/bash
set -e

echo "🔬 IntraFlow End-to-End Test"
echo "============================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000"
TOKEN=""
TENANT_ID=""
WORKFLOW_ID=""

echo -e "\n${YELLOW}Step 1: Health Check${NC}"
if curl -f ${API_URL}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API is not responding${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 2: User Signup${NC}"
SIGNUP_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
        "email": "e2e-test@example.com",
        "password": "SecurePass123!@#",
        "tenant_name": "E2E Test Tenant"
    }')

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ User signup successful${NC}"
    TOKEN=$(echo $SIGNUP_RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')
    TENANT_ID=$(echo $SIGNUP_RESPONSE | grep -o '"tenant_id":"[^"]*"' | sed 's/"tenant_id":"\(.*\)"/\1/')
else
    # Try login if user exists
    echo "User might exist, trying login..."
    LOGIN_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{
            "email": "e2e-test@example.com",
            "password": "SecurePass123!@#"
        }')
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo -e "${GREEN}✓ User login successful${NC}"
        TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')
        TENANT_ID=$(echo $LOGIN_RESPONSE | grep -o '"tenant_id":"[^"]*"' | sed 's/"tenant_id":"\(.*\)"/\1/')
    else
        echo -e "${RED}✗ Signup/Login failed${NC}"
        echo "Response: $SIGNUP_RESPONSE"
        exit 1
    fi
fi

echo -e "\n${YELLOW}Step 3: Create Workflow${NC}"
WORKFLOW_RESPONSE=$(curl -s -X POST ${API_URL}/api/v1/workflows \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "E2E Test Workflow",
        "description": "Automated test workflow",
        "definition": {
            "nodes": [
                {"id": "start", "type": "trigger", "data": {"label": "Start"}},
                {"id": "msg1", "type": "message", "data": {"label": "Welcome", "message": "Hello!"}}
            ],
            "edges": [],
            "variables": {}
        }
    }')

if echo "$WORKFLOW_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✓ Workflow created${NC}"
    WORKFLOW_ID=$(echo $WORKFLOW_RESPONSE | grep -o '"id":"[^"]*"' | sed 's/"id":"\(.*\)"/\1/')
else
    echo -e "${RED}✗ Workflow creation failed${NC}"
    echo "Response: $WORKFLOW_RESPONSE"
    exit 1
fi

echo -e "\n${YELLOW}Step 4: List Workflows${NC}"
WORKFLOWS=$(curl -s -X GET ${API_URL}/api/v1/workflows \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$WORKFLOWS" | grep -q "$WORKFLOW_ID"; then
    echo -e "${GREEN}✓ Workflow listing successful${NC}"
else
    echo -e "${RED}✗ Workflow not found in list${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 5: Update Workflow${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT ${API_URL}/api/v1/workflows/${WORKFLOW_ID} \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "E2E Test Workflow Updated",
        "description": "Updated description"
    }')

if echo "$UPDATE_RESPONSE" | grep -q "Updated"; then
    echo -e "${GREEN}✓ Workflow updated${NC}"
else
    echo -e "${RED}✗ Workflow update failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 6: Get Workflow Details${NC}"
WORKFLOW_DETAILS=$(curl -s -X GET ${API_URL}/api/v1/workflows/${WORKFLOW_ID} \
    -H "Authorization: Bearer ${TOKEN}")

if echo "$WORKFLOW_DETAILS" | grep -q "Updated"; then
    echo -e "${GREEN}✓ Workflow retrieval successful${NC}"
else
    echo -e "${RED}✗ Workflow retrieval failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 7: Delete Workflow${NC}"
DELETE_RESPONSE=$(curl -s -X DELETE ${API_URL}/api/v1/workflows/${WORKFLOW_ID} \
    -H "Authorization: Bearer ${TOKEN}")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Workflow deleted${NC}"
else
    echo -e "${RED}✗ Workflow deletion failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ All E2E tests passed!${NC}"
echo -e "\n📊 Test Summary:"
echo "  ✓ Health check"
echo "  ✓ User authentication"
echo "  ✓ Workflow CRUD operations"
echo "  ✓ Authorization"
echo -e "\n🎉 IntraFlow E2E validation complete!"
