"""
Webhook handler for incoming WhatsApp messages
"""

import logging
import json
from fastapi import APIRouter, Request, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from prometheus_client import Counter

from src.webhooks.verification import verify_webhook_signature
from src.services.queue_service import queue_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

webhook_counter = Counter(
    'webhook_requests_total',
    'Total webhook requests received',
    ['event_type', 'status']
)


class WebhookMessage(BaseModel):
    """Webhook message model"""
    id: str
    sessionId: str
    from_: str = Field(..., alias="from")
    to: str
    body: Optional[str] = None
    type: str = "text"
    timestamp: int
    isGroupMsg: bool = False
    chat: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None
    caption: Optional[str] = None
    quotedMsg: Optional[Dict[str, Any]] = None


class WebhookPayload(BaseModel):
    """Webhook payload model"""
    event: str
    session: str
    data: Optional[WebhookMessage] = None


@router.post("/")
async def handle_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Signature")
):
    """
    Handle incoming WhatsApp webhook from OpenWA
    
    This endpoint:
    1. Verifies HMAC signature
    2. Validates payload structure
    3. Queues message for async processing
    """
    raw_body = await request.body()
    
    verify_webhook_signature(raw_body, x_signature)
    
    try:
        payload_dict = json.loads(raw_body)
        payload = WebhookPayload(**payload_dict)
        
        logger.info(
            f"Webhook received - Event: {payload.event}, "
            f"Session: {payload.session}"
        )
        
        if payload.event == "message" and payload.data:
            message = payload.data
            
            if message.type == "chat" or message.type == "text":
                await queue_message({
                    "message_id": message.id,
                    "session_id": message.sessionId,
                    "from": message.from_,
                    "to": message.to,
                    "body": message.body or message.caption or "",
                    "type": message.type,
                    "timestamp": message.timestamp,
                    "is_group": message.isGroupMsg,
                    "metadata": {
                        "chat": message.chat,
                        "sender": message.sender,
                        "quoted_msg": message.quotedMsg
                    }
                })
                
                webhook_counter.labels(
                    event_type=payload.event,
                    status="queued"
                ).inc()
                
                return {
                    "status": "success",
                    "message": "Message queued for processing"
                }
            else:
                logger.info(f"Skipping non-text message type: {message.type}")
                webhook_counter.labels(
                    event_type=payload.event,
                    status="skipped"
                ).inc()
                
                return {
                    "status": "skipped",
                    "message": f"Message type {message.type} not supported"
                }
        
        elif payload.event == "qr":
            logger.info(f"QR code event for session: {payload.session}")
            webhook_counter.labels(event_type="qr", status="received").inc()
            return {"status": "success", "message": "QR event received"}
        
        elif payload.event == "ready":
            logger.info(f"Session ready: {payload.session}")
            webhook_counter.labels(event_type="ready", status="received").inc()
            return {"status": "success", "message": "Ready event received"}
        
        else:
            logger.debug(f"Unhandled event type: {payload.event}")
            webhook_counter.labels(event_type=payload.event, status="ignored").inc()
            return {"status": "ignored", "message": f"Event {payload.event} ignored"}
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {str(e)}")
        webhook_counter.labels(event_type="unknown", status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        webhook_counter.labels(event_type="unknown", status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/health")
async def webhook_health():
    """Health check for webhook endpoint"""
    return {"status": "healthy", "service": "webhook-handler"}
