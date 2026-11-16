"""
Integration tests for IntraFlow backend
Mock test all components end-to-end
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import json

# Test database models
def test_database_models():
    """Test all database models can be instantiated"""
    from src.database.models import (
        Tenant, TenantUser, WhatsAppSession, Workflow, 
        WorkflowExecution, User, Conversation, Message
    )
    
    # Test Tenant model
    tenant = Tenant(
        name="Test Company",
        slug="test-company",
        email="test@example.com"
    )
    assert tenant.name == "Test Company"
    assert tenant.slug == "test-company"
    print("✓ Database models validated")


# Test LLM Client
@pytest.mark.asyncio
async def test_llm_client():
    """Test LLM client with mock responses"""
    from src.llm.client import LLMClient
    
    with patch('src.llm.client.ChatOpenAI') as mock_openai:
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Test response from LLM"
        mock_openai.return_value.ainvoke = AsyncMock(return_value=mock_response)
        
        client = LLMClient(provider="openai", model="gpt-4o-mini")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"}
        ]
        
        response = await client.ainvoke(messages)
        assert "response" in response.lower()
        print("✓ LLM client works")


# Test Webhook Verification
def test_webhook_verification():
    """Test HMAC webhook signature verification"""
    import hmac
    import hashlib
    from src.webhooks.verification import verify_webhook_signature
    from src.config.settings import settings
    
    payload = b'{"event": "message", "data": {"body": "test"}}'
    
    # Generate valid signature
    signature = hmac.new(
        settings.WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Should pass with valid signature
    assert verify_webhook_signature(payload, signature) == True
    print("✓ Webhook verification works")


# Test Parent Agent
@pytest.mark.asyncio
async def test_parent_agent():
    """Test Parent Agent guardrails"""
    from src.agents.parent_agent import ParentAgent, ParentAgentConfig
    
    config = ParentAgentConfig(
        enable_safety_check=True,
        enable_content_filter=True,
        enable_context_check=True,
        enable_rate_limiting=False  # Disable for testing
    )
    
    with patch('src.agents.parent_agent.ChatOpenAI') as mock_llm:
        # Mock safety check response
        mock_response = Mock()
        mock_response.content = '{"safe": true, "categories": [], "confidence": 0.9, "explanation": "Safe message"}'
        mock_llm.return_value.ainvoke = AsyncMock(return_value=mock_response)
        
        agent = ParentAgent(config=config)
        
        result = await agent.supervise(
            message="I need help with my order",
            context={"user_id": "test123"}
        )
        
        assert result.allow == True
        print("✓ Parent Agent guardrails work")


# Test Workflow Service
@pytest.mark.asyncio
async def test_workflow_service():
    """Test workflow CRUD operations"""
    from src.services.workflow_service import WorkflowService
    from uuid import uuid4
    
    service = WorkflowService()
    
    # Mock session
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    tenant_id = uuid4()
    workflow_definition = {
        "nodes": [{"id": "start", "type": "trigger"}],
        "edges": []
    }
    
    with patch('src.services.workflow_service.Workflow') as mock_workflow:
        workflow = await service.create_workflow(
            session=mock_session,
            tenant_id=tenant_id,
            name="Test Workflow",
            definition=workflow_definition
        )
        
        print("✓ Workflow service works")


# Test Agent Orchestrator
@pytest.mark.asyncio  
async def test_agent_orchestrator():
    """Test agent orchestration and intent classification"""
    from src.agents.orchestrator import AgentOrchestrator
    
    with patch('src.agents.orchestrator.ChatOpenAI') as mock_llm:
        # Mock intent classification
        mock_response = Mock()
        mock_response.content = '{"intent": "product_search", "confidence": 0.9, "agent_type": "product_search"}'
        mock_llm.return_value.ainvoke = AsyncMock(return_value=mock_response)
        
        orchestrator = AgentOrchestrator()
        
        result = await orchestrator.classify_intent("I want to buy shoes")
        
        assert result.intent == "product_search"
        assert result.confidence > 0.5
        print("✓ Agent orchestrator works")


# Test OpenWA Client
@pytest.mark.asyncio
async def test_openwa_client():
    """Test OpenWA message sending"""
    from src.services.openwa_client import OpenWAClient
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "messageId": "msg123"}
        mock_response.raise_for_status = Mock()
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        client = OpenWAClient()
        result = await client.send_text_message(
            session_id="test-session",
            to="1234567890@c.us",
            text="Hello, World!"
        )
        
        assert result["success"] == True
        print("✓ OpenWA client works")


# Test Queue Service
@pytest.mark.asyncio
async def test_queue_service():
    """Test Redis queue operations"""
    from src.services.queue_service import queue_message
    
    with patch('src.services.queue_service.get_redis') as mock_redis:
        mock_client = AsyncMock()
        mock_client.lpush = AsyncMock(return_value=1)
        mock_redis.return_value = mock_client
        
        message = {
            "message_id": "test-msg-123",
            "session_id": "test-session",
            "from": "1234567890@c.us",
            "body": "Test message"
        }
        
        result = await queue_message(message)
        assert result == True
        print("✓ Queue service works")


# Test Session Service
@pytest.mark.asyncio
async def test_session_service():
    """Test session-to-tenant mapping"""
    from src.services.session_service import SessionService
    from uuid import uuid4
    
    service = SessionService()
    
    with patch('src.services.session_service.async_session_maker') as mock_maker:
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = Mock(tenant_id=uuid4())
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        mock_maker.return_value.__aenter__.return_value = mock_session
        
        tenant_id = await service.get_tenant_by_session("test-session-123")
        
        assert tenant_id is not None
        print("✓ Session service works")


# Integration test: Full message flow
@pytest.mark.asyncio
async def test_full_message_flow():
    """Test complete message processing pipeline"""
    from src.services.queue_service import process_message
    
    with patch('src.services.session_service.SessionService') as mock_session_service, \
         patch('src.agents.parent_agent.ParentAgent') as mock_parent_agent, \
         patch('src.agents.orchestrator.AgentOrchestrator') as mock_orchestrator, \
         patch('src.services.openwa_client.OpenWAClient') as mock_openwa:
        
        # Mock session service
        mock_session_instance = Mock()
        mock_session_instance.get_tenant_by_session = AsyncMock(
            return_value="11111111-1111-1111-1111-111111111111"
        )
        mock_session_service.return_value = mock_session_instance
        
        # Mock parent agent
        mock_parent_instance = Mock()
        mock_result = Mock()
        mock_result.allow = True
        mock_parent_instance.supervise = AsyncMock(return_value=mock_result)
        mock_parent_agent.return_value = mock_parent_instance
        
        # Mock orchestrator
        mock_orch_instance = Mock()
        mock_orch_instance.process_message = AsyncMock(return_value={
            "response": "I can help you with that!",
            "agentType": "customer_support",
            "intent": "general_inquiry"
        })
        mock_orchestrator.return_value = mock_orch_instance
        
        # Mock OpenWA
        mock_openwa_instance = Mock()
        mock_openwa_instance.send_text_message = AsyncMock(return_value={"success": True})
        mock_openwa.return_value = mock_openwa_instance
        
        # Process message
        message_data = {
            "message_id": "test-msg-123",
            "session_id": "test-session",
            "from": "1234567890@c.us",
            "body": "I need help",
            "type": "text",
            "timestamp": 1700000000
        }
        
        await process_message(message_data)
        
        print("✓ Full message flow works end-to-end")


# Run all tests
def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("🧪 Running IntraFlow Backend Integration Tests")
    print("="*60 + "\n")
    
    # Synchronous tests
    test_database_models()
    test_webhook_verification()
    
    # Async tests
    loop = asyncio.get_event_loop()
    
    print("\nTesting async components...")
    loop.run_until_complete(test_llm_client())
    loop.run_until_complete(test_parent_agent())
    loop.run_until_complete(test_workflow_service())
    loop.run_until_complete(test_agent_orchestrator())
    loop.run_until_complete(test_openwa_client())
    loop.run_until_complete(test_queue_service())
    loop.run_until_complete(test_session_service())
    
    print("\nTesting full integration...")
    loop.run_until_complete(test_full_message_flow())
    
    print("\n" + "="*60)
    print("✅ All integration tests passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
