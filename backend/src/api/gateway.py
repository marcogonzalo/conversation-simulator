"""
API Gateway for the Conversation Simulator with DDD architecture.
"""
import logging
from typing import Callable
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.conversation import router as conversation_router
from src.api.routes.persona import router as persona_router
from src.api.routes.analysis import router as analysis_router
from src.api.routes.conversation_analysis import router as conversation_analysis_router
from src.api.routes.websocket import router as websocket_router
from src.api.routes.audio import router as audio_router
from src.api.routes.prompt import router as prompt_router

logger = logging.getLogger(__name__)


def create_app(lifespan: Callable = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Conversation Simulator API",
        description="API for the Conversation Simulator - AI-powered sales training platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Include API routes
    app.include_router(
        conversation_router,
        prefix="/api/v1/conversations",
        tags=["conversations"]
    )
    
    app.include_router(
        persona_router,
        prefix="/api/v1/personas",
        tags=["personas"]
    )
    
    app.include_router(
        analysis_router,
        prefix="/api/v1/analyses",
        tags=["analyses"]
    )
    
    app.include_router(
        conversation_analysis_router,
        prefix="/api/v1/conversation-analysis",
        tags=["conversation-analysis"]
    )
    
    app.include_router(
        websocket_router,
        prefix="/api/v1/ws",
        tags=["websocket"]
    )
    
    app.include_router(
        audio_router,
        prefix="/api/v1/audio",
        tags=["audio"]
    )
    
    app.include_router(
        prompt_router,
        prefix="/api/v1",
        tags=["prompts"]
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "conversation-simulator-api",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Conversation Simulator API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    logger.info("API Gateway configured successfully")
    return app