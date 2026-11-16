"""
Configuration settings for Agent Orchestrator
"""

import os
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings"""
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://whatsapp:whatsapp123@postgres:5432/whatsapp"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    LLM_PROVIDER: Literal["openai", "anthropic", "google", "ollama"] = os.getenv(
        "LLM_PROVIDER", "openai"
    )
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "500"))
    
    PRODUCT_API_URL: str = os.getenv("PRODUCT_API_URL", "")
    PRODUCT_API_KEY: str = os.getenv("PRODUCT_API_KEY", "")
    ORDER_API_URL: str = os.getenv("ORDER_API_URL", "")
    ORDER_API_KEY: str = os.getenv("ORDER_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
