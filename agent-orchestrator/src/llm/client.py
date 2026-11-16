"""
LLM client wrapper for multiple providers
"""

import logging
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from src.config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client supporting multiple providers
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider (openai, anthropic, google)
            model: Model name
            temperature: Sampling temperature
        """
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM client"""
        try:
            if self.provider == "openai":
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not set")
                
                return ChatOpenAI(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=settings.MAX_TOKENS,
                    api_key=settings.OPENAI_API_KEY
                )
            
            elif self.provider == "anthropic":
                if not settings.ANTHROPIC_API_KEY:
                    raise ValueError("ANTHROPIC_API_KEY not set")
                
                return ChatAnthropic(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=settings.MAX_TOKENS,
                    anthropic_api_key=settings.ANTHROPIC_API_KEY
                )
            
            elif self.provider == "google":
                if not settings.GOOGLE_API_KEY:
                    raise ValueError("GOOGLE_API_KEY not set")
                
                return ChatGoogleGenerativeAI(
                    model=self.model,
                    temperature=self.temperature,
                    max_output_tokens=settings.MAX_TOKENS,
                    google_api_key=settings.GOOGLE_API_KEY
                )
            
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    async def ainvoke(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Async invoke the LLM with messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            LLM response text
        """
        try:
            langchain_messages = []
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
                else:
                    langchain_messages.append(HumanMessage(content=content))
            
            response = await self.llm.ainvoke(langchain_messages, **kwargs)
            
            return response.content
        
        except Exception as e:
            logger.error(f"LLM invocation error: {str(e)}")
            raise
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Synchronous invoke the LLM with messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            LLM response text
        """
        try:
            langchain_messages = []
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    langchain_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    langchain_messages.append(AIMessage(content=content))
                else:
                    langchain_messages.append(HumanMessage(content=content))
            
            response = self.llm.invoke(langchain_messages, **kwargs)
            
            return response.content
        
        except Exception as e:
            logger.error(f"LLM invocation error: {str(e)}")
            raise


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> LLMClient:
    """
    Get an LLM client instance
    
    Args:
        provider: LLM provider (openai, anthropic, google)
        model: Model name
        temperature: Sampling temperature
        
    Returns:
        LLMClient instance
    """
    return LLMClient(provider=provider, model=model, temperature=temperature)
