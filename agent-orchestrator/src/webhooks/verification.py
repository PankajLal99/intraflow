"""
Webhook HMAC signature verification
"""

import hmac
import hashlib
import logging
from fastapi import HTTPException, status
from src.config.settings import settings

logger = logging.getLogger(__name__)


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify HMAC-SHA256 signature of webhook payload
    
    Args:
        payload: Raw request body as bytes
        signature: Signature from X-Signature header
        
    Returns:
        True if signature is valid, raises HTTPException otherwise
    """
    if not signature:
        logger.error("Missing X-Signature header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    is_valid = hmac.compare_digest(signature, expected_signature)
    
    if not is_valid:
        logger.error("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    logger.debug("Webhook signature verified successfully")
    return True
