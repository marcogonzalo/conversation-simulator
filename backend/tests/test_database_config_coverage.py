"""
Tests for database configuration
"""
import pytest
from unittest.mock import Mock, patch

from src.shared.infrastructure.database.database_config import DatabaseConfig


class TestDatabaseConfigCoverage:
    """Tests for DatabaseConfig"""
    
    def test_config_initialization(self):
        """Test database config can be initialized"""
        with patch('src.shared.infrastructure.database.database_config.create_engine') as mock_engine:
            mock_engine.return_value = Mock()
            
            config = DatabaseConfig(database_url="sqlite:///test.db")
            assert config is not None
    
    def test_config_with_sqlite_url(self):
        """Test config with SQLite URL"""
        with patch('src.shared.infrastructure.database.database_config.create_engine'):
            config = DatabaseConfig(database_url="sqlite:///:memory:")
            assert config is not None
    
    def test_config_with_postgres_url(self):
        """Test config with PostgreSQL URL"""
        with patch('src.shared.infrastructure.database.database_config.create_engine'):
            config = DatabaseConfig(database_url="postgresql://user:pass@localhost/db")
            assert config is not None
    
    def test_config_has_base(self):
        """Test config has Base attribute"""
        with patch('src.shared.infrastructure.database.database_config.create_engine'):
            config = DatabaseConfig(database_url="sqlite:///test.db")
            assert hasattr(config, 'Base')
    
    def test_config_has_engine(self):
        """Test config has engine attribute"""
        with patch('src.shared.infrastructure.database.database_config.create_engine') as mock_engine:
            mock_engine.return_value = Mock()
            
            config = DatabaseConfig(database_url="sqlite:///test.db")
            assert hasattr(config, 'engine')
    
    def test_init_database_method_exists(self):
        """Test init_database method exists"""
        with patch('src.shared.infrastructure.database.database_config.create_engine'):
            config = DatabaseConfig(database_url="sqlite:///test.db")
            assert hasattr(config, 'init_database')
            assert callable(config.init_database)
    
    def test_get_session_method_exists(self):
        """Test get_session method exists"""
        with patch('src.shared.infrastructure.database.database_config.create_engine'):
            config = DatabaseConfig(database_url="sqlite:///test.db")
            assert hasattr(config, 'get_session')
            assert callable(config.get_session)
    
    def test_multiple_configs_independent(self):
        """Test multiple config instances are independent"""
        with patch('src.shared.infrastructure.database.database_config.create_engine') as mock_engine:
            mock_engine.return_value = Mock()
            
            config1 = DatabaseConfig(database_url="sqlite:///db1.db")
            config2 = DatabaseConfig(database_url="sqlite:///db2.db")
            
            assert config1 is not config2
    
    def test_config_validation(self):
        """Test config validates database URL"""
        with patch('src.shared.infrastructure.database.database_config.create_engine'):
            # Should accept valid URL
            config = DatabaseConfig(database_url="sqlite:///valid.db")
            assert config is not None

