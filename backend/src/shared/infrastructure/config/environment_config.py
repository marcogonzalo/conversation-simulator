"""
Environment configuration loader.
"""
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Environment configuration manager."""
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.config_dir = Path(__file__).parent.parent.parent.parent.parent / "config"
        self._load_environment_config()
    
    def _load_environment_config(self) -> None:
        """Load environment-specific configuration."""
        config_file = self.config_dir / f"{self.environment}.env"
        
        if config_file.exists():
            self._load_env_file(config_file)
            logger.info(f"Loaded configuration from {config_file}")
        else:
            logger.warning(f"Configuration file not found: {config_file}")
            logger.info("Using system environment variables")
    
    def _load_env_file(self, file_path: Path) -> None:
        """Load environment variables from file."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Don't override existing environment variables
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            logger.error(f"Failed to load environment file {file_path}: {e}")
            raise
    
    def get_database_type(self) -> str:
        """Get the database type being used."""
        database_url = os.getenv("DATABASE_URL", "")
        if database_url.startswith("postgresql"):
            return "postgresql"
        elif database_url.startswith("sqlite"):
            return "sqlite"
        
        # Check individual PostgreSQL settings
        if all([
            os.getenv("POSTGRES_HOST"),
            os.getenv("POSTGRES_DB"),
            os.getenv("POSTGRES_USER"),
            os.getenv("POSTGRES_PASSWORD")
        ]):
            return "postgresql"
        
        # Check Supabase settings
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"):
            return "supabase"
        
        return "sqlite"  # Default fallback
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"


# Global environment configuration
env_config = EnvironmentConfig()
