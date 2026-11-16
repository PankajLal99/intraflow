"""
Agent Orchestrator - Routes messages to appropriate specialized agents
"""

import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.config.settings import settings
from src.agents.product_search import ProductSearchAgent
from src.agents.order_management import OrderManagementAgent
from src.agents.customer_support import CustomerSupportAgent

logger = logging.getLogger(__name__)


class IntentClassification(BaseModel):
    """Intent classification output"""
    intent: str = Field(description="The classified intent")
    confidence: float = Field(description="Confidence score between 0 and 1")
    agent_type: str = Field(description="The agent type to handle this intent")


class AgentOrchestrator:
    """
    Main orchestrator that classifies intent and routes to appropriate agents
    """
    
    def __init__(self):
        self.llm = self._get_llm()
        self.product_search_agent = ProductSearchAgent(self.llm)
        self.order_management_agent = OrderManagementAgent(self.llm)
        self.customer_support_agent = CustomerSupportAgent(self.llm)
        
        self.parser = PydanticOutputParser(pydantic_object=IntentClassification)
        
        self.intent_classifier_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for a WhatsApp business assistant.
            
Classify the user's message into one of these categories:
1. product_search - User wants to search for products, get recommendations, or browse catalog
2. order_management - User wants to create order, check order status, track shipment, or cancel order
3. customer_support - User needs help, has questions, complaints, or wants to talk to human

Analyze the message and provide the intent, confidence (0-1), and appropriate agent_type.

{format_instructions}"""),
            ("user", "{message}")
        ])
    
    def _get_llm(self):
        """Get LLM based on configuration"""
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY
            )
        elif settings.LLM_PROVIDER == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
            return ChatAnthropic(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                api_key=settings.ANTHROPIC_API_KEY
            )
        elif settings.LLM_PROVIDER == "google":
            if not settings.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is required for Google provider")
            return ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
                google_api_key=settings.GOOGLE_API_KEY
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
    
    async def classify_intent(self, message: str) -> IntentClassification:
        """Classify user intent"""
        try:
            chain = self.intent_classifier_prompt | self.llm | self.parser
            
            result = await chain.ainvoke({
                "message": message,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            logger.info(f"Intent classified: {result.intent} (confidence: {result.confidence})")
            return result
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return IntentClassification(
                intent="general_inquiry",
                confidence=0.5,
                agent_type="customer_support"
            )
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process incoming message and route to appropriate agent"""
        
        try:
            classification = await self.classify_intent(message)
            
            agent_response = None
            
            if classification.agent_type == "product_search":
                agent_response = await self.product_search_agent.process(
                    message, user_id, context
                )
            elif classification.agent_type == "order_management":
                agent_response = await self.order_management_agent.process(
                    message, user_id, context
                )
            else:
                agent_response = await self.customer_support_agent.process(
                    message, user_id, context
                )
            
            return {
                "success": True,
                "response": agent_response,
                "agentType": classification.agent_type,
                "intent": classification.intent,
                "confidence": classification.confidence,
                "nextAction": "await_user_response",
                "metadata": {
                    "llm_provider": settings.LLM_PROVIDER,
                    "llm_model": settings.LLM_MODEL
                }
            }
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}", exc_info=True)
            return {
                "success": False,
                "response": "I apologize, but I'm having trouble processing your request. Please try again.",
                "agentType": "error",
                "intent": "error",
                "confidence": 0.0,
                "metadata": {"error": str(e)}
            }
