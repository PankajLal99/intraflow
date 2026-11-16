"""
WhatsApp Business Agentic Workflow - Agent Orchestrator
Main FastAPI application
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import uvicorn

from src.config.settings import settings
from src.api import routes
from src.api import auth_routes
from src.webhooks import webhook_router
from src.database import init_db, close_db
from src.services.queue_service import start_worker, close_redis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting IntraFlow Agent Orchestrator")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"LLM Model: {settings.LLM_MODEL}")
    
    await init_db()
    logger.info("Database initialized")
    
    worker_task = asyncio.create_task(start_worker())
    logger.info("Message queue worker started")
    
    yield
    
    worker_task.cancel()
    await close_redis()
    await close_db()
    logger.info("Shutting down IntraFlow Agent Orchestrator")


app = FastAPI(
    title="IntraFlow Agent Orchestrator",
    description="Multi-tenant WhatsApp Business AI automation platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


app.include_router(webhook_router)
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(routes.router)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "IntraFlow Agent Orchestrator",
        "version": "1.0.0",
        "status": "running",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "features": [
            "Multi-tenant WhatsApp automation",
            "Parent Agent guardrails",
            "Visual workflow execution",
            "LangChain agent orchestration"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "intraflow-orchestrator",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )
