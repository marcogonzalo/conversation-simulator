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

from src.shared.infrastructure.config.environment_config import env_config

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.database_type = env_config.get_database_type()
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self.metadata = MetaData()
        
        logger.info(f"Database configuration initialized: {self.database_type}")
        logger.info(f"Environment: {env_config.environment}")
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        # Check for explicit database URL first
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Ensure PostgreSQL URLs use psycopg driver
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
            return database_url
        
        # Check for PostgreSQL configuration
        postgres_host = os.getenv("POSTGRES_HOST")
        postgres_port = os.getenv("POSTGRES_PORT", "5432")
        postgres_db = os.getenv("POSTGRES_DB")
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        
        if all([postgres_host, postgres_db, postgres_user, postgres_password]):
            return f"postgresql+psycopg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        
        # Check for Supabase configuration
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        if supabase_url and supabase_key:
            # Extract database info from Supabase URL
            # Supabase URL format: https://project.supabase.co
            # We need to construct the PostgreSQL connection string
            import re
            match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)
            if match:
                project_id = match.group(1)
                return f"postgresql+psycopg://postgres:[password]@db.{project_id}.supabase.co:5432/postgres"
        
        # Fallback to SQLite for local development
        db_path = os.getenv("DATABASE_PATH", "data/conversation_simulator.db")
        logger.warning(f"No PostgreSQL configuration found, falling back to SQLite: {db_path}")
        return f"sqlite:///{db_path}"
    
    def create_engine(self) -> None:
        """Create database engine."""
        try:
            # Configure engine based on database type
            if self.database_url.startswith("sqlite"):
                # SQLite configuration
                self.engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
                )
            else:
                # PostgreSQL configuration
                self.engine = create_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
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
