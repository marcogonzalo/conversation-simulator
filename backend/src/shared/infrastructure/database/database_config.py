"""
Database configuration for the application.
"""
import os
import logging
from typing import Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self.metadata = MetaData()
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        # For MVP, use SQLite
        db_path = os.getenv("DATABASE_PATH", "data/conversation_simulator.db")
        return f"sqlite:///{db_path}"
    
    def create_engine(self) -> None:
        """Create database engine."""
        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
            )
            logger.info(f"Database engine created: {self.database_url}")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    def create_session_factory(self) -> None:
        """Create session factory."""
        if not self.engine:
            raise RuntimeError("Database engine not created")
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        logger.info("Session factory created")
    
    def create_tables(self) -> None:
        """Create database tables."""
        if not self.engine:
            raise RuntimeError("Database engine not created")
        
        try:
            self.Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_session(self):
        """Get database session."""
        if not self.SessionLocal:
            raise RuntimeError("Session factory not created")
        
        return self.SessionLocal()
    
    def setup_database(self) -> None:
        """Setup complete database configuration."""
        self.create_engine()
        self.create_session_factory()
        self.create_tables()
        logger.info("Database setup completed successfully")


# Global database configuration
db_config = DatabaseConfig()
