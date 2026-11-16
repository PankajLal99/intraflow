# Parent Agent / Supervisor Architecture

## Overview

The **Parent Agent** (also called Supervisor or Guardrail Agent) is a mandatory layer that runs BEFORE any user-created workflow executes. It ensures that all interactions stay within acceptable boundaries and comply with business rules.

## Why We Need It

### Without Parent Agent ❌
```
User Message → Customer's Workflow → Response
                     ↓
            Could do ANYTHING:
            - Spam users
            - Inappropriate content
            - Off-topic conversations
            - Resource abuse
            - Security violations
```

### With Parent Agent ✅
```
User Message
    ↓
┌─────────────────────────────┐
│   PARENT AGENT (Guardrail)  │
│  ┌─────────────────────┐    │
│  │ 1. Safety Check     │    │
│  │ 2. Content Filter   │    │
│  │ 3. Context Boundary │    │
│  │ 4. Rate Limiting    │    │
│  │ 5. Business Rules   │    │
│  └─────────────────────┘    │
│         ↓                   │
│    [ALLOW] or [BLOCK]       │
└─────────────────────────────┘
         ↓
    [If ALLOW]
         ↓
Customer's Workflow → Response
```

---

## Architecture

### 1. Parent Agent Pipeline

```python
class ParentAgent:
    """
    Supervisor that validates all interactions
    Runs BEFORE customer workflows
    """
    
    async def supervise(self, message: str, context: dict) -> SupervisionResult:
        """
        Run all supervision checks
        Returns: allow/block decision with reason
        """
        
        # 1. Safety Check
        safety_result = await self.check_safety(message)
        if not safety_result.safe:
            return SupervisionResult(
                allow=False,
                reason="safety_violation",
                message="This message violates our safety policies."
            )
        
        # 2. Content Filter
        content_result = await self.filter_content(message)
        if not content_result.appropriate:
            return SupervisionResult(
                allow=False,
                reason="inappropriate_content",
                message="Please keep the conversation professional."
            )
        
        # 3. Context Boundary
        context_result = await self.check_context(message, context)
        if not context_result.in_context:
            return SupervisionResult(
                allow=False,
                reason="out_of_context",
                message="I can only help with topics related to our business."
            )
        
        # 4. Rate Limiting
        rate_result = await self.check_rate_limit(context['user_id'])
        if not rate_result.allowed:
            return SupervisionResult(
                allow=False,
                reason="rate_limit_exceeded",
                message="You've reached the message limit. Please try again later."
            )
        
        # 5. Business Rules
        rules_result = await self.enforce_business_rules(message, context)
        if not rules_result.compliant:
            return SupervisionResult(
                allow=False,
                reason="business_rule_violation",
                message=rules_result.message
            )
        
        # All checks passed
        return SupervisionResult(
            allow=True,
            reason="approved",
            enhanced_context=self.enhance_context(message, context)
        )
```

### 2. Execution Flow

```
┌───────────────────────────────────────────────────────────────┐
│  Message Processing Pipeline                                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  1. User sends message                                        │
│          ↓                                                    │
│  ┌─────────────────────────────────────────┐                 │
│  │  PARENT AGENT (Platform Level)          │                 │
│  │  ┌───────────────────────────────────┐  │                 │
│  │  │ Safety Check                      │  │                 │
│  │  │  - Harmful content detection      │  │                 │
│  │  │  - Abuse prevention               │  │                 │
│  │  │  - PII detection                  │  │                 │
│  │  └───────────────────────────────────┘  │                 │
│  │  ┌───────────────────────────────────┐  │                 │
│  │  │ Content Filter                    │  │                 │
│  │  │  - Profanity filter               │  │                 │
│  │  │  - Spam detection                 │  │                 │
│  │  │  - Language appropriateness       │  │                 │
│  │  └───────────────────────────────────┘  │                 │
│  │  ┌───────────────────────────────────┐  │                 │
│  │  │ Context Boundary                  │  │                 │
│  │  │  - Topic relevance check          │  │                 │
│  │  │  - Business scope validation      │  │                 │
│  │  │  - Allowed intents only           │  │                 │
│  │  └───────────────────────────────────┘  │                 │
│  │  ┌───────────────────────────────────┐  │                 │
│  │  │ Rate Limiting                     │  │                 │
│  │  │  - Messages per minute/hour/day   │  │                 │
│  │  │  - Per-user limits                │  │                 │
│  │  │  - Global tenant limits           │  │                 │
│  │  └───────────────────────────────────┘  │                 │
│  │  ┌───────────────────────────────────┐  │                 │
│  │  │ Business Rules                    │  │                 │
│  │  │  - Operating hours check          │  │                 │
│  │  │  - Region restrictions            │  │                 │
│  │  │  - Feature flags                  │  │                 │
│  │  └───────────────────────────────────┘  │                 │
│  └─────────────────────────────────────────┘                 │
│          ↓                                                    │
│     [DECISION]                                                │
│          ↓                                                    │
│  ┌──────────┬──────────┐                                     │
│  │          │          │                                     │
│  ▼          ▼          ▼                                     │
│ BLOCK    ALLOW    ESCALATE                                   │
│  │          │          │                                     │
│  │          ↓          │                                     │
│  │  ┌────────────────┐ │                                     │
│  │  │ CUSTOMER'S     │ │                                     │
│  │  │ WORKFLOW       │ │                                     │
│  │  │ (If Allowed)   │ │                                     │
│  │  └────────────────┘ │                                     │
│  │          ↓          │                                     │
│  └──────────┼──────────┘                                     │
│             ↓                                                 │
│        Response to User                                       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Core Parent Agent Class

```python
# agent-orchestrator/src/agents/parent_agent.py

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class SupervisionResult(BaseModel):
    """Result of parent agent supervision"""
    allow: bool
    reason: str
    message: Optional[str] = None
    severity: str = "info"  # info, warning, critical
    enhanced_context: Optional[Dict[str, Any]] = None
    suggested_action: Optional[str] = None


class SafetyCheck(BaseModel):
    """Safety check result"""
    safe: bool
    categories: List[str] = []
    confidence: float = 0.0
    explanation: str = ""


class ParentAgentConfig(BaseModel):
    """Configuration for parent agent"""
    
    # Safety settings
    enable_safety_check: bool = True
    safety_threshold: float = 0.7
    
    # Content filtering
    enable_content_filter: bool = True
    profanity_filter: bool = True
    spam_detection: bool = True
    
    # Context boundaries
    enable_context_check: bool = True
    allowed_topics: List[str] = []
    blocked_topics: List[str] = []
    business_description: str = ""
    
    # Rate limiting
    enable_rate_limiting: bool = True
    messages_per_minute: int = 10
    messages_per_hour: int = 100
    messages_per_day: int = 500
    
    # Business rules
    operating_hours: Optional[Dict[str, str]] = None
    allowed_regions: List[str] = []
    blocked_keywords: List[str] = []
    
    # Escalation
    auto_escalate_on: List[str] = ["critical_safety", "repeated_violations"]
    escalation_webhook: Optional[str] = None


class ParentAgent:
    """
    Parent/Supervisor agent that validates all interactions
    Runs BEFORE any customer workflow
    """
    
    def __init__(
        self,
        config: ParentAgentConfig,
        llm: Optional[ChatOpenAI] = None
    ):
        self.config = config
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        
        # In-memory rate limiting (use Redis in production)
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Violation tracking
        self.violations: Dict[str, List[Dict]] = {}
        
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Set up LLM prompts for various checks"""
        
        # Safety check prompt
        self.safety_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a safety validator. Analyze if the message contains:
            - Harmful content (violence, self-harm, illegal activities)
            - Harassment or hate speech
            - Sexual content
            - Privacy violations (PII sharing)
            - Scams or fraud attempts
            
            Respond with JSON:
            {{
                "safe": true/false,
                "categories": ["category1", "category2"],
                "confidence": 0.0-1.0,
                "explanation": "brief explanation"
            }}"""),
            ("user", "Analyze this message: {message}")
        ])
        
        # Context boundary check prompt
        self.context_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a context validator.
            
            Business Description: {business_description}
            Allowed Topics: {allowed_topics}
            Blocked Topics: {blocked_topics}
            
            Determine if the user's message is:
            1. Relevant to the business
            2. Within allowed topics
            3. Not in blocked topics
            
            Respond with JSON:
            {{
                "in_context": true/false,
                "relevance_score": 0.0-1.0,
                "explanation": "why in/out of context"
            }}"""),
            ("user", "User message: {message}")
        ])
    
    async def supervise(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> SupervisionResult:
        """
        Main supervision method - runs all checks
        """
        
        user_id = context.get('user_id', 'unknown')
        tenant_id = context.get('tenant_id', 'unknown')
        
        logger.info(f"Parent agent supervising message for user {user_id}")
        
        try:
            # 1. Safety Check
            if self.config.enable_safety_check:
                safety_result = await self.check_safety(message)
                if not safety_result.safe:
                    self._record_violation(user_id, "safety", safety_result.categories)
                    return SupervisionResult(
                        allow=False,
                        reason="safety_violation",
                        message="This message violates our safety policies. Please keep conversations respectful and appropriate.",
                        severity="critical"
                    )
            
            # 2. Content Filter
            if self.config.enable_content_filter:
                content_result = await self.filter_content(message)
                if not content_result['appropriate']:
                    self._record_violation(user_id, "content", [content_result['reason']])
                    return SupervisionResult(
                        allow=False,
                        reason="inappropriate_content",
                        message="Please keep the conversation professional and appropriate.",
                        severity="warning"
                    )
            
            # 3. Context Boundary
            if self.config.enable_context_check:
                context_result = await self.check_context(message, context)
                if not context_result['in_context']:
                    return SupervisionResult(
                        allow=False,
                        reason="out_of_context",
                        message=f"I can only help with {self.config.business_description}. Your message seems unrelated.",
                        severity="info",
                        suggested_action="redirect_to_scope"
                    )
            
            # 4. Rate Limiting
            if self.config.enable_rate_limiting:
                rate_result = self.check_rate_limit(user_id)
                if not rate_result['allowed']:
                    return SupervisionResult(
                        allow=False,
                        reason="rate_limit_exceeded",
                        message=f"You've reached the message limit ({rate_result['limit']} per {rate_result['period']}). Please try again later.",
                        severity="warning"
                    )
            
            # 5. Business Rules
            rules_result = await self.enforce_business_rules(message, context)
            if not rules_result['compliant']:
                return SupervisionResult(
                    allow=False,
                    reason="business_rule_violation",
                    message=rules_result['message'],
                    severity="info"
                )
            
            # All checks passed - enhance context and allow
            enhanced_context = self._enhance_context(message, context)
            
            logger.info(f"Parent agent APPROVED message for user {user_id}")
            
            return SupervisionResult(
                allow=True,
                reason="approved",
                message=None,
                severity="info",
                enhanced_context=enhanced_context
            )
        
        except Exception as e:
            logger.error(f"Parent agent error: {str(e)}", exc_info=True)
            # Fail open but log the error
            return SupervisionResult(
                allow=True,
                reason="supervision_error",
                message=None,
                severity="warning"
            )
    
    async def check_safety(self, message: str) -> SafetyCheck:
        """
        Check message for safety violations
        Uses LLM for nuanced safety detection
        """
        
        try:
            # Use LLM to analyze safety
            chain = self.safety_prompt | self.llm
            result = await chain.ainvoke({"message": message})
            
            # Parse LLM response (assuming JSON output)
            # In production, use structured output parsing
            response_text = result.content
            
            # Simple keyword-based fallback
            unsafe_keywords = [
                'violence', 'harm', 'illegal', 'scam', 'fraud',
                'hack', 'steal', 'drugs', 'weapons'
            ]
            
            message_lower = message.lower()
            found_keywords = [kw for kw in unsafe_keywords if kw in message_lower]
            
            if found_keywords:
                return SafetyCheck(
                    safe=False,
                    categories=found_keywords,
                    confidence=0.8,
                    explanation=f"Contains concerning keywords: {', '.join(found_keywords)}"
                )
            
            return SafetyCheck(
                safe=True,
                categories=[],
                confidence=0.9,
                explanation="No safety concerns detected"
            )
        
        except Exception as e:
            logger.error(f"Safety check error: {str(e)}")
            # Fail safe - allow but log
            return SafetyCheck(
                safe=True,
                categories=[],
                confidence=0.0,
                explanation="Safety check failed, allowing by default"
            )
    
    async def filter_content(self, message: str) -> Dict[str, Any]:
        """
        Filter inappropriate content
        """
        
        message_lower = message.lower()
        
        # Profanity filter
        if self.config.profanity_filter:
            profanity_words = ['badword1', 'badword2']  # Add actual list
            if any(word in message_lower for word in profanity_words):
                return {
                    'appropriate': False,
                    'reason': 'profanity',
                    'explanation': 'Message contains inappropriate language'
                }
        
        # Spam detection
        if self.config.spam_detection:
            # Simple spam indicators
            spam_indicators = [
                len(message) > 1000,  # Too long
                message.count('!') > 5,  # Excessive punctuation
                message.count('http') > 3,  # Too many links
                message.upper() == message and len(message) > 50  # All caps
            ]
            
            if any(spam_indicators):
                return {
                    'appropriate': False,
                    'reason': 'spam',
                    'explanation': 'Message appears to be spam'
                }
        
        return {
            'appropriate': True,
            'reason': None,
            'explanation': 'Content is appropriate'
        }
    
    async def check_context(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if message is within business context
        """
        
        # If no business description, allow everything
        if not self.config.business_description:
            return {
                'in_context': True,
                'relevance_score': 1.0,
                'explanation': 'No context restrictions configured'
            }
        
        try:
            # Use LLM to check context relevance
            chain = self.context_prompt | self.llm
            result = await chain.ainvoke({
                "message": message,
                "business_description": self.config.business_description,
                "allowed_topics": ", ".join(self.config.allowed_topics),
                "blocked_topics": ", ".join(self.config.blocked_topics)
            })
            
            # Parse response
            # For now, simple keyword matching
            message_lower = message.lower()
            
            # Check blocked topics
            for topic in self.config.blocked_topics:
                if topic.lower() in message_lower:
                    return {
                        'in_context': False,
                        'relevance_score': 0.0,
                        'explanation': f'Message mentions blocked topic: {topic}'
                    }
            
            # If allowed topics specified, check if message relates to any
            if self.config.allowed_topics:
                matches = any(
                    topic.lower() in message_lower
                    for topic in self.config.allowed_topics
                )
                
                if not matches:
                    return {
                        'in_context': False,
                        'relevance_score': 0.3,
                        'explanation': 'Message does not relate to our services'
                    }
            
            return {
                'in_context': True,
                'relevance_score': 0.9,
                'explanation': 'Message is within business context'
            }
        
        except Exception as e:
            logger.error(f"Context check error: {str(e)}")
            # Fail open
            return {
                'in_context': True,
                'relevance_score': 0.5,
                'explanation': 'Context check failed, allowing by default'
            }
    
    def check_rate_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user has exceeded rate limits
        """
        
        now = datetime.utcnow()
        
        # Initialize user's rate limit history
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Clean old timestamps
        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id]
            if now - ts < timedelta(days=1)
        ]
        
        timestamps = self.rate_limits[user_id]
        
        # Check per-minute limit
        minute_ago = now - timedelta(minutes=1)
        messages_last_minute = sum(1 for ts in timestamps if ts > minute_ago)
        
        if messages_last_minute >= self.config.messages_per_minute:
            return {
                'allowed': False,
                'limit': self.config.messages_per_minute,
                'period': 'minute',
                'current_count': messages_last_minute
            }
        
        # Check per-hour limit
        hour_ago = now - timedelta(hours=1)
        messages_last_hour = sum(1 for ts in timestamps if ts > hour_ago)
        
        if messages_last_hour >= self.config.messages_per_hour:
            return {
                'allowed': False,
                'limit': self.config.messages_per_hour,
                'period': 'hour',
                'current_count': messages_last_hour
            }
        
        # Check per-day limit
        day_ago = now - timedelta(days=1)
        messages_last_day = sum(1 for ts in timestamps if ts > day_ago)
        
        if messages_last_day >= self.config.messages_per_day:
            return {
                'allowed': False,
                'limit': self.config.messages_per_day,
                'period': 'day',
                'current_count': messages_last_day
            }
        
        # Record this message
        self.rate_limits[user_id].append(now)
        
        return {
            'allowed': True,
            'limit': None,
            'period': None,
            'current_count': len(timestamps)
        }
    
    async def enforce_business_rules(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforce business-specific rules
        """
        
        # Check operating hours
        if self.config.operating_hours:
            now = datetime.utcnow()
            hour = now.hour
            day = now.strftime('%A')
            
            # TODO: Implement proper time zone handling
            # For now, assume UTC
            
            # If outside operating hours, inform user
            # (But still allow - just inform)
            pass
        
        # Check blocked keywords
        message_lower = message.lower()
        for keyword in self.config.blocked_keywords:
            if keyword.lower() in message_lower:
                return {
                    'compliant': False,
                    'message': f"Sorry, I cannot process messages containing '{keyword}'."
                }
        
        return {
            'compliant': True,
            'message': None
        }
    
    def _enhance_context(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance context with parent agent insights
        """
        
        enhanced = context.copy()
        enhanced['parent_agent_approved'] = True
        enhanced['supervision_timestamp'] = datetime.utcnow().isoformat()
        
        # Add any extracted metadata
        enhanced['message_length'] = len(message)
        enhanced['message_word_count'] = len(message.split())
        
        return enhanced
    
    def _record_violation(
        self,
        user_id: str,
        violation_type: str,
        details: List[str]
    ):
        """
        Record a violation for tracking repeat offenders
        """
        
        if user_id not in self.violations:
            self.violations[user_id] = []
        
        self.violations[user_id].append({
            'type': violation_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Check for repeat violations
        if len(self.violations[user_id]) >= 3:
            logger.warning(f"User {user_id} has {len(self.violations[user_id])} violations")
            # TODO: Implement escalation


# Example usage
async def example():
    """Example of parent agent usage"""
    
    config = ParentAgentConfig(
        enable_safety_check=True,
        enable_content_filter=True,
        enable_context_check=True,
        business_description="e-commerce store selling electronics",
        allowed_topics=["products", "orders", "shipping", "returns"],
        blocked_topics=["politics", "religion"],
        messages_per_minute=5,
        messages_per_hour=50
    )
    
    parent_agent = ParentAgent(config)
    
    # Test messages
    test_cases = [
        "I want to buy a laptop",  # Should pass
        "Tell me about your return policy",  # Should pass
        "Buy cheap drugs here!!!",  # Should fail - safety
        "Let's talk about politics",  # Should fail - out of context
    ]
    
    for message in test_cases:
        result = await parent_agent.supervise(
            message,
            {'user_id': 'test_user', 'tenant_id': 'test_tenant'}
        )
        print(f"\nMessage: {message}")
        print(f"Allowed: {result.allow}")
        print(f"Reason: {result.reason}")
        if result.message:
            print(f"User Message: {result.message}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(example())
```

---

## Integration with Workflow Executor

### Modified Execution Flow

```python
# agent-orchestrator/src/agents/orchestrator.py

from src.agents.parent_agent import ParentAgent, ParentAgentConfig
from src.workflow.executor import WorkflowExecutor, Workflow

class AgentOrchestrator:
    """
    Main orchestrator with parent agent integration
    """
    
    def __init__(self):
        self.llm = self._get_llm()
        
        # Initialize parent agent (platform-wide)
        self.parent_agent = self._initialize_parent_agent()
    
    def _initialize_parent_agent(self) -> ParentAgent:
        """Initialize parent agent with default config"""
        
        config = ParentAgentConfig(
            enable_safety_check=True,
            enable_content_filter=True,
            enable_context_check=True,
            enable_rate_limiting=True,
            
            # Default business rules
            messages_per_minute=10,
            messages_per_hour=100,
            messages_per_day=500,
            
            # Will be overridden per tenant
            business_description="",
            allowed_topics=[],
            blocked_topics=[]
        )
        
        return ParentAgent(config, self.llm)
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming message with parent agent supervision
        """
        
        try:
            # Prepare context
            full_context = {
                'user_id': user_id,
                'tenant_id': tenant_id,
                'timestamp': datetime.utcnow().isoformat(),
                **(context or {})
            }
            
            # STEP 1: Parent Agent Supervision
            logger.info(f"Running parent agent supervision for tenant {tenant_id}")
            
            supervision_result = await self.parent_agent.supervise(
                message=message,
                context=full_context
            )
            
            # If blocked, return parent agent's message
            if not supervision_result.allow:
                logger.warning(
                    f"Parent agent BLOCKED message: {supervision_result.reason}"
                )
                
                # Log the block
                await self._log_supervision_block(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    reason=supervision_result.reason,
                    severity=supervision_result.severity
                )
                
                return {
                    'success': False,
                    'response': supervision_result.message,
                    'blocked_by': 'parent_agent',
                    'reason': supervision_result.reason,
                    'severity': supervision_result.severity
                }
            
            # STEP 2: Load tenant's workflow
            logger.info(f"Parent agent APPROVED - Loading workflow for tenant {tenant_id}")
            
            workflow = await self._load_tenant_workflow(tenant_id, full_context)
            
            # Use enhanced context from parent agent
            if supervision_result.enhanced_context:
                full_context.update(supervision_result.enhanced_context)
            
            # STEP 3: Execute workflow
            executor = WorkflowExecutor(
                workflow=workflow,
                conversation_id=full_context.get('conversation_id', 'new'),
                tenant_id=tenant_id,
                llm=self.llm
            )
            
            result = await executor.execute(message)
            
            # Add supervision metadata
            result['supervised_by_parent'] = True
            result['supervision_timestamp'] = supervision_result.enhanced_context.get(
                'supervision_timestamp'
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}", exc_info=True)
            return {
                'success': False,
                'response': 'Sorry, I encountered an error. Please try again.',
                'error': str(e)
            }
    
    async def _log_supervision_block(
        self,
        tenant_id: str,
        user_id: str,
        reason: str,
        severity: str
    ):
        """Log when parent agent blocks a message"""
        
        # Store in database for analytics
        # await db.supervision_logs.create({
        #     'tenant_id': tenant_id,
        #     'user_id': user_id,
        #     'reason': reason,
        #     'severity': severity,
        #     'timestamp': datetime.utcnow()
        # })
        pass
```

---

## Tenant-Specific Parent Agent Configuration

### Per-Tenant Customization

```python
class TenantParentAgentConfig(BaseModel):
    """Tenant-specific parent agent configuration"""
    
    tenant_id: str
    
    # Override global settings
    business_description: str = ""
    allowed_topics: List[str] = []
    blocked_topics: List[str] = []
    blocked_keywords: List[str] = []
    
    # Custom rate limits
    custom_rate_limits: bool = False
    messages_per_minute: Optional[int] = None
    messages_per_hour: Optional[int] = None
    
    # Custom rules
    custom_safety_rules: Dict[str, Any] = {}
    operating_hours: Optional[Dict[str, str]] = None


# Store in database
CREATE TABLE tenant_parent_agent_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    
    business_description TEXT,
    allowed_topics TEXT[] DEFAULT '{}',
    blocked_topics TEXT[] DEFAULT '{}',
    blocked_keywords TEXT[] DEFAULT '{}',
    
    enable_safety_check BOOLEAN DEFAULT TRUE,
    enable_content_filter BOOLEAN DEFAULT TRUE,
    enable_context_check BOOLEAN DEFAULT TRUE,
    enable_rate_limiting BOOLEAN DEFAULT TRUE,
    
    messages_per_minute INTEGER,
    messages_per_hour INTEGER,
    messages_per_day INTEGER,
    
    custom_rules JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id)
);
```

---

## Admin Dashboard for Parent Agent

### Configuration UI

```
┌────────────────────────────────────────────────────────┐
│  Parent Agent Configuration                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Business Description:                                 │
│  [We are an e-commerce store selling electronics...]  │
│                                                        │
│  Allowed Topics:                                       │
│  [products] [orders] [shipping] [returns] [+ Add]     │
│                                                        │
│  Blocked Topics:                                       │
│  [politics] [religion] [+ Add]                        │
│                                                        │
│  Blocked Keywords:                                     │
│  [spam] [scam] [+ Add]                                │
│                                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │ Safety Settings                              │     │
│  ├──────────────────────────────────────────────┤     │
│  │ ☑ Enable safety check                       │     │
│  │ ☑ Enable content filter                     │     │
│  │ ☑ Block profanity                           │     │
│  │ ☑ Spam detection                            │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │ Rate Limiting                                │     │
│  ├──────────────────────────────────────────────┤     │
│  │ Messages per minute:  [10]                   │     │
│  │ Messages per hour:    [100]                  │     │
│  │ Messages per day:     [500]                  │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  [Save Configuration]  [Test]  [Reset to Default]     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Analytics & Monitoring

### Supervision Dashboard

```
┌────────────────────────────────────────────────────────┐
│  Parent Agent Analytics                                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Today's Statistics:                                   │
│  ┌──────────────────────────────────────────────┐     │
│  │ Total Messages: 1,234                        │     │
│  │ Approved: 1,150 (93%)                        │     │
│  │ Blocked: 84 (7%)                             │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  Block Reasons:                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │ Out of Context:        45 (54%)              │     │
│  │ Rate Limit:            28 (33%)              │     │
│  │ Safety Violation:       8  (10%)             │     │
│  │ Inappropriate Content:  3  (3%)              │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  Recent Blocks:                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │ 10:45 AM | User_123 | Out of Context        │     │
│  │ 10:42 AM | User_456 | Rate Limit            │     │
│  │ 10:38 AM | User_789 | Safety Violation      │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
│  [View Full Log]  [Export Report]                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Benefits

### For Platform (You)
- ✅ Prevent abuse and spam
- ✅ Maintain quality standards
- ✅ Reduce support burden
- ✅ Compliance with regulations
- ✅ Brand protection

### For Tenants (Customers)
- ✅ Their workflows can't go rogue
- ✅ Automatic content moderation
- ✅ Rate limiting protects their resources
- ✅ Context boundaries improve UX
- ✅ Safety checks protect their brand

---

## Next Steps

1. **Implement parent_agent.py** (provided above)
2. **Integrate with orchestrator** (code provided)
3. **Create tenant configuration table**
4. **Build admin UI** for configuration
5. **Add analytics dashboard**
6. **Test with edge cases**

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026  
**Status**: Ready for Implementation
