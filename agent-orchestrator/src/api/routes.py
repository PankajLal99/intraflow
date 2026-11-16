"""
API routes for Agent Orchestrator
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from prometheus_client import Counter, Histogram

from src.agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

request_counter = Counter(
    'agent_requests_total',
    'Total agent requests',
    ['agent_type', 'intent']
)

response_time_histogram = Histogram(
    'agent_response_time_seconds',
    'Agent response time',
    ['agent_type']
)

class ConversationContext(BaseModel):
    """Conversation context model"""
    conversationId: Optional[int] = None
    sessionId: str
    lastIntent: Optional[str] = None
    lastAgentType: Optional[str] = None


class AgentRequest(BaseModel):
    """Agent request model"""
    userId: str
    message: str
    messageType: str = "text"
    context: Optional[ConversationContext] = None
    metadata: Optional[Dict[str, Any]] = None


class Button(BaseModel):
    """Button model"""
    id: str
    text: str
    action: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent response model"""
    success: bool
    response: str
    buttons: Optional[List[Button]] = None
    nextAction: Optional[str] = None
    agentType: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


orchestrator = AgentOrchestrator()


@router.post("/process", response_model=AgentResponse)
async def process_message(request: AgentRequest):
    """
    Process incoming message and generate agent response
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing message for user {request.userId}")
        
        result = await orchestrator.process_message(
            user_id=request.userId,
            message=request.message,
            context=request.context.dict() if request.context else None,
            metadata=request.metadata
        )
        
        duration = time.time() - start_time
        response_time_histogram.labels(agent_type=result.get('agentType', 'unknown')).observe(duration)
        request_counter.labels(
            agent_type=result.get('agentType', 'unknown'),
            intent=result.get('intent', 'unknown')
        ).inc()
        
        logger.info(
            f"Message processed successfully - "
            f"Agent: {result.get('agentType')}, "
            f"Intent: {result.get('intent')}, "
            f"Time: {duration:.2f}s"
        )
        
        return AgentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
