"""
Tests for webhook handling
"""

import pytest
import hmac
import hashlib
import json
from fastapi import HTTPException
from src.webhooks.verification import verify_webhook_signature
from src.config.settings import settings


class TestWebhookVerification:
    """Test webhook signature verification"""
    
    def test_verify_valid_signature(self):
        """Test verification with valid HMAC signature"""
        payload = b'{"event": "message", "session": "test"}'
        
        signature = hmac.new(
            settings.WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        assert verify_webhook_signature(payload, signature) is True
    
    def test_verify_invalid_signature(self):
        """Test verification with invalid signature"""
        payload = b'{"event": "message", "session": "test"}'
        invalid_signature = "invalid_signature_here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_webhook_signature(payload, invalid_signature)
        
        assert exc_info.value.status_code == 401
    
    def test_verify_missing_signature(self):
        """Test verification with missing signature"""
        payload = b'{"event": "message", "session": "test"}'
        
        with pytest.raises(HTTPException) as exc_info:
            verify_webhook_signature(payload, None)
        
        assert exc_info.value.status_code == 401
    
    def test_verify_tampered_payload(self):
        """Test verification with tampered payload"""
        original_payload = b'{"event": "message", "session": "test"}'
        
        signature = hmac.new(
            settings.WEBHOOK_SECRET.encode('utf-8'),
            original_payload,
            hashlib.sha256
        ).hexdigest()
        
        tampered_payload = b'{"event": "message", "session": "hacked"}'
        
        with pytest.raises(HTTPException) as exc_info:
            verify_webhook_signature(tampered_payload, signature)
        
        assert exc_info.value.status_code == 401


class TestWebhookPayload:
    """Test webhook payload validation"""
    
    def test_valid_message_payload(self, sample_webhook_payload):
        """Test validation of valid message payload"""
        from src.webhooks.handler import WebhookPayload
        
        payload = WebhookPayload(**sample_webhook_payload)
        
        assert payload.event == "message"
        assert payload.session == "test-session-123"
        assert payload.data is not None
        assert payload.data.id == "test-msg-123"
        assert payload.data.body == "Test message"
    
    def test_qr_event_payload(self):
        """Test QR code event payload"""
        from src.webhooks.handler import WebhookPayload
        
        qr_payload = {
            "event": "qr",
            "session": "test-session-123",
            "data": None
        }
        
        payload = WebhookPayload(**qr_payload)
        
        assert payload.event == "qr"
        assert payload.session == "test-session-123"
        assert payload.data is None
