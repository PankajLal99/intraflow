"""
Pytest configuration and fixtures
"""

import pytest
import os

os.environ.update({
    "ENVIRONMENT": "test",
    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
    "REDIS_URL": "redis://localhost:6379/1",
    "WEBHOOK_SECRET": "test-webhook-secret",
    "JWT_SECRET": "test-jwt-secret",
    "OPENAI_API_KEY": "test-key",
    "LLM_PROVIDER": "openai",
    "LLM_MODEL": "gpt-4o-mini"
})


@pytest.fixture
def sample_message_data():
    """Sample WhatsApp message data"""
    return {
        "message_id": "test-msg-123",
        "session_id": "test-session-123",
        "from": "1234567890@c.us",
        "to": "9876543210@c.us",
        "body": "Hello, I need help with my order",
        "type": "text",
        "timestamp": 1700000000,
        "is_group": False
    }


@pytest.fixture
def sample_webhook_payload():
    """Sample webhook payload from OpenWA"""
    return {
        "event": "message",
        "session": "test-session-123",
        "data": {
            "id": "test-msg-123",
            "sessionId": "test-session-123",
            "from": "1234567890@c.us",
            "to": "9876543210@c.us",
            "body": "Test message",
            "type": "chat",
            "timestamp": 1700000000,
            "isGroupMsg": False
        }
    }


@pytest.fixture
def sample_user_data():
    """Sample user signup data"""
    return {
        "tenant_name": "Test Company",
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }
