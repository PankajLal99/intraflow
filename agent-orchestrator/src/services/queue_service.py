"""
Redis queue service for async message processing
"""

import logging
import json
import asyncio
from typing import Dict, Any
from redis import asyncio as aioredis
from src.config.settings import settings
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

redis_client: aioredis.Redis = None

message_queue_counter = Counter(
    'message_queue_total',
    'Total messages queued',
    ['status']
)

message_processing_time = Histogram(
    'message_processing_seconds',
    'Message processing time'
)


async def get_redis() -> aioredis.Redis:
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def queue_message(message: Dict[str, Any]) -> bool:
    """
    Queue a message for async processing
    
    Args:
        message: Message dictionary containing message data
        
    Returns:
        True if queued successfully
    """
    try:
        redis = await get_redis()
        
        message_json = json.dumps(message)
        
        await redis.lpush(settings.REDIS_QUEUE_NAME, message_json)
        
        message_queue_counter.labels(status="queued").inc()
        
        logger.info(f"Message queued: {message['message_id']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error queuing message: {str(e)}", exc_info=True)
        message_queue_counter.labels(status="error").inc()
        return False


async def process_message(message_data: Dict[str, Any]):
    """
    Process a message from the queue
    
    This is the main message processing pipeline:
    1. Load tenant from session
    2. Run Parent Agent guardrails
    3. Load and execute workflow
    4. Send response via OpenWA
    """
    from src.services.session_service import SessionService
    from src.services.openwa_client import OpenWAClient
    from src.agents.parent_agent import ParentAgent
    from src.agents.orchestrator import AgentOrchestrator
    
    message_id = message_data.get("message_id")
    session_id = message_data.get("session_id")
    from_number = message_data.get("from")
    body = message_data.get("body", "")
    
    logger.info(f"Processing message {message_id} from {from_number}")
    
    try:
        session_service = SessionService()
        tenant_id = await session_service.get_tenant_by_session(session_id)
        
        if not tenant_id:
            logger.error(f"No tenant found for session {session_id}")
            message_queue_counter.labels(status="no_tenant").inc()
            return
        
        from src.agents.parent_agent import ParentAgent, ParentAgentConfig
        
        config = ParentAgentConfig(
            enable_safety_check=True,
            enable_content_filter=True,
            enable_context_check=True,
            enable_rate_limiting=True
        )
        parent_agent = ParentAgent(config=config)
        
        supervision_result = await parent_agent.supervise(
            message=body,
            context={
                "user_id": from_number,
                "session_id": session_id,
                "tenant_id": str(tenant_id)
            }
        )
        
        if not supervision_result.allow:
            logger.warning(
                f"Message blocked by Parent Agent: {supervision_result.reason}"
            )
            
            if supervision_result.message:
                openwa = OpenWAClient()
                await openwa.send_text_message(
                    session_id=session_id,
                    to=from_number,
                    text=supervision_result.message
                )
            
            message_queue_counter.labels(status="blocked").inc()
            return
        
        orchestrator = AgentOrchestrator()
        result = await orchestrator.process_message(
            user_id=from_number,
            message=body,
            context={
                "session_id": session_id,
                "tenant_id": str(tenant_id)
            }
        )
        
        openwa = OpenWAClient()
        
        if result.get("buttons"):
            await openwa.send_button_message(
                session_id=session_id,
                to=from_number,
                text=result["response"],
                buttons=result["buttons"]
            )
        else:
            await openwa.send_text_message(
                session_id=session_id,
                to=from_number,
                text=result["response"]
            )
        
        message_queue_counter.labels(status="processed").inc()
        logger.info(f"Message {message_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {str(e)}", exc_info=True)
        message_queue_counter.labels(status="error").inc()


async def start_worker():
    """
    Start the message queue worker
    
    This continuously polls Redis for new messages and processes them
    """
    logger.info("Starting message queue worker")
    redis = await get_redis()
    
    while True:
        try:
            result = await redis.brpop(settings.REDIS_QUEUE_NAME, timeout=1)
            
            if result:
                queue_name, message_json = result
                message_data = json.loads(message_json)
                
                with message_processing_time.time():
                    await process_message(message_data)
            
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Worker error: {str(e)}", exc_info=True)
            await asyncio.sleep(1)
