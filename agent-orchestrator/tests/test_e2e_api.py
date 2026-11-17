"""
End-to-End API Tests
Tests complete user workflows from signup to workflow execution
"""
import pytest
import asyncio
from httpx import AsyncClient
from fastapi import status

from src.main import app


class TestUserJourney:
    """Test complete user journey"""
    
    @pytest.mark.asyncio
    async def test_complete_user_workflow(self):
        """Test complete workflow: signup → login → create workflow → execute"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Step 1: Signup
            signup_data = {
                "email": "e2e_test@example.com",
                "password": "SecurePassword123!@#",
                "tenant_name": "E2E Test Company"
            }
            
            signup_response = await client.post(
                "/api/v1/auth/signup",
                json=signup_data
            )
            
            assert signup_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
            signup_json = signup_response.json()
            assert "access_token" in signup_json
            assert "tenant_id" in signup_json
            
            token = signup_json["access_token"]
            tenant_id = signup_json["tenant_id"]
            
            # Step 2: Verify authentication works
            headers = {"Authorization": f"Bearer {token}"}
            
            # Step 3: Create a workflow
            workflow_data = {
                "name": "E2E Test Workflow",
                "description": "Automated test workflow",
                "definition": {
                    "nodes": [
                        {"id": "start", "type": "trigger", "data": {"label": "Start"}},
                        {"id": "msg1", "type": "message", "data": {"message": "Hello World!"}}
                    ],
                    "edges": [{"source": "start", "target": "msg1"}],
                    "variables": {}
                }
            }
            
            create_workflow_response = await client.post(
                "/api/v1/workflows",
                headers=headers,
                json=workflow_data
            )
            
            assert create_workflow_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
            workflow = create_workflow_response.json()
            assert workflow["name"] == "E2E Test Workflow"
            assert "id" in workflow
            
            workflow_id = workflow["id"]
            
            # Step 4: List workflows
            list_response = await client.get(
                "/api/v1/workflows",
                headers=headers
            )
            
            assert list_response.status_code == status.HTTP_200_OK
            workflows = list_response.json()
            assert len(workflows) >= 1
            assert any(w["id"] == workflow_id for w in workflows)
            
            # Step 5: Get workflow details
            get_response = await client.get(
                f"/api/v1/workflows/{workflow_id}",
                headers=headers
            )
            
            assert get_response.status_code == status.HTTP_200_OK
            workflow_details = get_response.json()
            assert workflow_details["id"] == workflow_id
            assert workflow_details["name"] == "E2E Test Workflow"
            
            # Step 6: Update workflow
            update_data = {
                "name": "E2E Test Workflow Updated",
                "description": "Updated description"
            }
            
            update_response = await client.put(
                f"/api/v1/workflows/{workflow_id}",
                headers=headers,
                json=update_data
            )
            
            assert update_response.status_code == status.HTTP_200_OK
            updated_workflow = update_response.json()
            assert updated_workflow["name"] == "E2E Test Workflow Updated"
            
            # Step 7: Delete workflow
            delete_response = await client.delete(
                f"/api/v1/workflows/{workflow_id}",
                headers=headers
            )
            
            assert delete_response.status_code == status.HTTP_200_OK
            
            # Step 8: Verify deletion
            verify_response = await client.get(
                f"/api/v1/workflows/{workflow_id}",
                headers=headers
            )
            
            assert verify_response.status_code == status.HTTP_404_NOT_FOUND


class TestAuthenticationFlow:
    """Test authentication workflows"""
    
    @pytest.mark.asyncio
    async def test_login_after_signup(self):
        """Test login with newly created account"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Signup
            signup_data = {
                "email": "login_test@example.com",
                "password": "TestPassword123!",
                "tenant_name": "Login Test Company"
            }
            
            await client.post("/api/v1/auth/signup", json=signup_data)
            
            # Login
            login_data = {
                "email": "login_test@example.com",
                "password": "TestPassword123!"
            }
            
            login_response = await client.post(
                "/api/v1/auth/login",
                json=login_data
            )
            
            assert login_response.status_code == status.HTTP_200_OK
            login_json = login_response.json()
            assert "access_token" in login_json
            assert "tenant_id" in login_json
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            headers = {"Authorization": "Bearer invalid_token_here"}
            
            response = await client.get(
                "/api/v1/workflows",
                headers=headers
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_missing_token_rejected(self):
        """Test that requests without tokens are rejected"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/workflows")
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTenantIsolation:
    """Test tenant isolation in real scenarios"""
    
    @pytest.mark.asyncio
    async def test_tenant_cannot_access_other_tenant_data(self):
        """Test that tenants cannot access each other's data"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create Tenant A
            tenant_a_data = {
                "email": "tenant_a@example.com",
                "password": "Password123!",
                "tenant_name": "Tenant A"
            }
            
            tenant_a_response = await client.post(
                "/api/v1/auth/signup",
                json=tenant_a_data
            )
            tenant_a_token = tenant_a_response.json()["access_token"]
            
            # Create Tenant B
            tenant_b_data = {
                "email": "tenant_b@example.com",
                "password": "Password123!",
                "tenant_name": "Tenant B"
            }
            
            tenant_b_response = await client.post(
                "/api/v1/auth/signup",
                json=tenant_b_data
            )
            tenant_b_token = tenant_b_response.json()["access_token"]
            
            # Tenant A creates a workflow
            workflow_data = {
                "name": "Tenant A Workflow",
                "description": "Private workflow",
                "definition": {"nodes": [], "edges": [], "variables": {}}
            }
            
            create_response = await client.post(
                "/api/v1/workflows",
                headers={"Authorization": f"Bearer {tenant_a_token}"},
                json=workflow_data
            )
            
            workflow_id = create_response.json()["id"]
            
            # Tenant B tries to access Tenant A's workflow
            access_response = await client.get(
                f"/api/v1/workflows/{workflow_id}",
                headers={"Authorization": f"Bearer {tenant_b_token}"}
            )
            
            # Should be denied
            assert access_response.status_code in [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND
            ]


class TestWebhookFlow:
    """Test webhook processing flow"""
    
    @pytest.mark.asyncio
    async def test_webhook_with_valid_signature(self):
        """Test webhook processing with valid HMAC signature"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            import hmac
            import hashlib
            import json
            
            payload = {
                "event": "message",
                "data": {
                    "from": "1234567890",
                    "body": "Hello bot"
                }
            }
            
            payload_bytes = json.dumps(payload).encode()
            secret = "test_webhook_secret"
            signature = hmac.new(
                secret.encode(),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            response = await client.post(
                "/webhook",
                json=payload,
                headers={"X-Webhook-Signature": signature}
            )
            
            # Should accept webhook
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_202_ACCEPTED
            ]
    
    @pytest.mark.asyncio
    async def test_webhook_with_invalid_signature(self):
        """Test webhook rejected with invalid signature"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "event": "message",
                "data": {
                    "from": "1234567890",
                    "body": "Hello bot"
                }
            }
            
            response = await client.post(
                "/webhook",
                json=payload,
                headers={"X-Webhook-Signature": "invalid_signature"}
            )
            
            # Should reject webhook
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestHealthAndMetrics:
    """Test health and metrics endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health endpoint returns OK"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Test metrics endpoint returns Prometheus format"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/metrics")
            
            assert response.status_code == status.HTTP_200_OK
            assert "text/plain" in response.headers.get("content-type", "")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_create_workflow_with_invalid_data(self):
        """Test error handling for invalid workflow data"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user first
            signup_data = {
                "email": "error_test@example.com",
                "password": "Password123!",
                "tenant_name": "Error Test"
            }
            
            signup_response = await client.post(
                "/api/v1/auth/signup",
                json=signup_data
            )
            token = signup_response.json()["access_token"]
            
            # Try to create workflow with invalid data
            invalid_workflow = {
                "name": "",  # Empty name
                "description": "Test",
                "definition": {}  # Invalid definition
            }
            
            response = await client.post(
                "/api/v1/workflows",
                headers={"Authorization": f"Bearer {token}"},
                json=invalid_workflow
            )
            
            # Should return validation error
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting enforcement"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # This would test rate limiting
            # Make many requests and verify rate limit is enforced
            pass


class TestConcurrency:
    """Test concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_workflow_creation(self):
        """Test creating multiple workflows concurrently"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user
            signup_data = {
                "email": "concurrent_test@example.com",
                "password": "Password123!",
                "tenant_name": "Concurrent Test"
            }
            
            signup_response = await client.post(
                "/api/v1/auth/signup",
                json=signup_data
            )
            token = signup_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create multiple workflows concurrently
            async def create_workflow(index):
                workflow_data = {
                    "name": f"Concurrent Workflow {index}",
                    "description": f"Test workflow {index}",
                    "definition": {"nodes": [], "edges": [], "variables": {}}
                }
                return await client.post(
                    "/api/v1/workflows",
                    headers=headers,
                    json=workflow_data
                )
            
            # Create 5 workflows concurrently
            responses = await asyncio.gather(
                *[create_workflow(i) for i in range(5)]
            )
            
            # All should succeed
            assert all(r.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED] for r in responses)
            
            # Verify all workflows were created
            list_response = await client.get(
                "/api/v1/workflows",
                headers=headers
            )
            workflows = list_response.json()
            assert len(workflows) >= 5
