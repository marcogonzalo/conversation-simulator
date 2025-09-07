"""
Main FastAPI application entry point with DDD architecture.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.shared.infrastructure.messaging.event_configuration import EventBusSetup
from src.shared.infrastructure.database.database_config import db_config
from src.shared.infrastructure.external_apis.api_config import api_config
from src.api.gateway import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Conversation Simulator API...")
    
    # Validate API configuration
    if not api_config.validate_config():
        logger.error("API configuration validation failed")
        raise RuntimeError("Invalid API configuration")
    
    # Setup database
    try:
        db_config.setup_database()
        logger.info("Database setup completed")
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise
    
    # Setup event bus
    try:
        await EventBusSetup.setup_all()
        logger.info("Event bus setup completed")
    except Exception as e:
        logger.error(f"Event bus setup failed: {e}")
        raise
    
    logger.info("Conversation Simulator API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Conversation Simulator API...")


# Create FastAPI application
app = create_app(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )