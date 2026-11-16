"""
Parent Agent / Supervisor
Validates all interactions before executing customer workflows
"""

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
    severity: str = "info"
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
    
    enable_safety_check: bool = True
    safety_threshold: float = 0.7
    
    enable_content_filter: bool = True
    profanity_filter: bool = True
    spam_detection: bool = True
    
    enable_context_check: bool = True
    allowed_topics: List[str] = []
    blocked_topics: List[str] = []
    business_description: str = ""
    
    enable_rate_limiting: bool = True
    messages_per_minute: int = 10
    messages_per_hour: int = 100
    messages_per_day: int = 500
    
    operating_hours: Optional[Dict[str, str]] = None
    allowed_regions: List[str] = []
    blocked_keywords: List[str] = []
    
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
        
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.violations: Dict[str, List[Dict]] = {}
        
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Set up LLM prompts for various checks"""
        
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
            
            if self.config.enable_rate_limiting:
                rate_result = self.check_rate_limit(user_id)
                if not rate_result['allowed']:
                    return SupervisionResult(
                        allow=False,
                        reason="rate_limit_exceeded",
                        message=f"You've reached the message limit ({rate_result['limit']} per {rate_result['period']}). Please try again later.",
                        severity="warning"
                    )
            
            rules_result = await self.enforce_business_rules(message, context)
            if not rules_result['compliant']:
                return SupervisionResult(
                    allow=False,
                    reason="business_rule_violation",
                    message=rules_result['message'],
                    severity="info"
                )
            
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
            return SupervisionResult(
                allow=True,
                reason="supervision_error",
                message=None,
                severity="warning"
            )
    
    async def check_safety(self, message: str) -> SafetyCheck:
        """Check message for safety violations"""
        
        try:
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
            return SafetyCheck(
                safe=True,
                categories=[],
                confidence=0.0,
                explanation="Safety check failed, allowing by default"
            )
    
    async def filter_content(self, message: str) -> Dict[str, Any]:
        """Filter inappropriate content"""
        
        message_lower = message.lower()
        
        if self.config.profanity_filter:
            profanity_words = ['badword1', 'badword2']
            if any(word in message_lower for word in profanity_words):
                return {
                    'appropriate': False,
                    'reason': 'profanity',
                    'explanation': 'Message contains inappropriate language'
                }
        
        if self.config.spam_detection:
            spam_indicators = [
                len(message) > 1000,
                message.count('!') > 5,
                message.count('http') > 3,
                message.upper() == message and len(message) > 50
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
        """Check if message is within business context"""
        
        if not self.config.business_description:
            return {
                'in_context': True,
                'relevance_score': 1.0,
                'explanation': 'No context restrictions configured'
            }
        
        try:
            message_lower = message.lower()
            
            for topic in self.config.blocked_topics:
                if topic.lower() in message_lower:
                    return {
                        'in_context': False,
                        'relevance_score': 0.0,
                        'explanation': f'Message mentions blocked topic: {topic}'
                    }
            
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
            return {
                'in_context': True,
                'relevance_score': 0.5,
                'explanation': 'Context check failed, allowing by default'
            }
    
    def check_rate_limit(self, user_id: str) -> Dict[str, Any]:
        """Check if user has exceeded rate limits"""
        
        now = datetime.utcnow()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        self.rate_limits[user_id] = [
            ts for ts in self.rate_limits[user_id]
            if now - ts < timedelta(days=1)
        ]
        
        timestamps = self.rate_limits[user_id]
        
        minute_ago = now - timedelta(minutes=1)
        messages_last_minute = sum(1 for ts in timestamps if ts > minute_ago)
        
        if messages_last_minute >= self.config.messages_per_minute:
            return {
                'allowed': False,
                'limit': self.config.messages_per_minute,
                'period': 'minute',
                'current_count': messages_last_minute
            }
        
        hour_ago = now - timedelta(hours=1)
        messages_last_hour = sum(1 for ts in timestamps if ts > hour_ago)
        
        if messages_last_hour >= self.config.messages_per_hour:
            return {
                'allowed': False,
                'limit': self.config.messages_per_hour,
                'period': 'hour',
                'current_count': messages_last_hour
            }
        
        day_ago = now - timedelta(days=1)
        messages_last_day = sum(1 for ts in timestamps if ts > day_ago)
        
        if messages_last_day >= self.config.messages_per_day:
            return {
                'allowed': False,
                'limit': self.config.messages_per_day,
                'period': 'day',
                'current_count': messages_last_day
            }
        
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
        """Enforce business-specific rules"""
        
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
        """Enhance context with parent agent insights"""
        
        enhanced = context.copy()
        enhanced['parent_agent_approved'] = True
        enhanced['supervision_timestamp'] = datetime.utcnow().isoformat()
        enhanced['message_length'] = len(message)
        enhanced['message_word_count'] = len(message.split())
        
        return enhanced
    
    def _record_violation(
        self,
        user_id: str,
        violation_type: str,
        details: List[str]
    ):
        """Record a violation for tracking repeat offenders"""
        
        if user_id not in self.violations:
            self.violations[user_id] = []
        
        self.violations[user_id].append({
            'type': violation_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        if len(self.violations[user_id]) >= 3:
            logger.warning(f"User {user_id} has {len(self.violations[user_id])} violations")
