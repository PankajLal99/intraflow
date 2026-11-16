"""
Configuration settings for Agent Orchestrator
"""

import os
import secrets
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://whatsapp:whatsapp123@postgres:5432/whatsapp"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    REDIS_QUEUE_NAME: str = "whatsapp_messages"
    
    # Security
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", secrets.token_urlsafe(32))
    JWT_SECRET: str = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # OpenWA Configuration
    OPENWA_API_URL: str = os.getenv("OPENWA_API_URL", "http://openwa:2785/api")
    OPENWA_API_KEY: str = os.getenv("OPENWA_API_KEY", "")
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    LLM_PROVIDER: Literal["openai", "anthropic", "google", "ollama"] = os.getenv(
        "LLM_PROVIDER", "openai"
    )
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "500"))
    
    # External APIs
    PRODUCT_API_URL: str = os.getenv("PRODUCT_API_URL", "")
    PRODUCT_API_KEY: str = os.getenv("PRODUCT_API_KEY", "")
    ORDER_API_URL: str = os.getenv("ORDER_API_URL", "")
    ORDER_API_KEY: str = os.getenv("ORDER_API_KEY", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
