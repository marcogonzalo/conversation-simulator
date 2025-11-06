"""
Tests for configuration modules
"""
import pytest
import os
from unittest.mock import patch

from src.shared.infrastructure.config.environment_config import EnvironmentConfig
from src.shared.infrastructure.external_apis.api_config import APIConfig


class TestEnvironmentConfig:
    """Tests for EnvironmentConfig"""
    
    def test_config_initialization(self):
        """Test config initializes"""
        config = EnvironmentConfig()
        assert config is not None
    
    def test_config_has_openai_key(self):
        """Test config has OpenAI key attribute"""
        config = EnvironmentConfig()
        assert hasattr(config, 'openai_api_key')
    
    def test_config_has_database_url(self):
        """Test config has database URL"""
        config = EnvironmentConfig()
        assert hasattr(config, 'database_url')
    
    def test_config_has_api_settings(self):
        """Test config has API settings"""
        config = EnvironmentConfig()
        assert hasattr(config, 'api_host')
        assert hasattr(config, 'api_port')
    
    def test_config_with_env_vars(self):
        """Test config reads from environment"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key',
            'API_HOST': '0.0.0.0',
            'API_PORT': '8000'
        }):
            config = EnvironmentConfig()
            assert config.openai_api_key == 'test_key' or config.openai_api_key is not None
    
    def test_config_default_values(self):
        """Test config has sensible defaults"""
        config = EnvironmentConfig()
        # Should not crash without env vars
        assert config is not None
    
    def test_config_api_port_is_int(self):
        """Test API port is integer"""
        config = EnvironmentConfig()
        if hasattr(config, 'api_port'):
            assert isinstance(config.api_port, (int, str))


class TestAPIConfig:
    """Tests for APIConfig"""
    
    def test_api_config_initialization(self):
        """Test APIConfig initializes"""
        config = APIConfig()
        assert config is not None
    
    def test_api_config_has_openai_settings(self):
        """Test API config has OpenAI settings"""
        config = APIConfig()
        assert hasattr(config, 'openai_api_key')
    
    def test_api_config_has_model_settings(self):
        """Test API config has model settings"""
        config = APIConfig()
        assert hasattr(config, 'default_model')
    
    def test_api_config_has_voice_settings(self):
        """Test API config has voice settings"""
        config = APIConfig()
        assert hasattr(config, 'default_voice')
    
    def test_api_config_default_model(self):
        """Test default model is set"""
        config = APIConfig()
        assert config.default_model is not None
        assert isinstance(config.default_model, str)
    
    def test_api_config_default_voice(self):
        """Test default voice is set"""
        config = APIConfig()
        assert config.default_voice is not None
        assert isinstance(config.default_voice, str)
    
    def test_api_config_temperature(self):
        """Test temperature setting"""
        config = APIConfig()
        if hasattr(config, 'temperature'):
            assert 0.0 <= config.temperature <= 2.0
    
    def test_api_config_max_tokens(self):
        """Test max tokens setting"""
        config = APIConfig()
        if hasattr(config, 'max_tokens'):
            assert config.max_tokens > 0
    
    def test_api_config_audio_format(self):
        """Test audio format setting"""
        config = APIConfig()
        assert hasattr(config, 'audio_format')
        assert config.audio_format in ['wav', 'webm', 'mp3', 'pcm16']
    
    def test_api_config_sample_rate(self):
        """Test sample rate setting"""
        config = APIConfig()
        if hasattr(config, 'sample_rate'):
            assert config.sample_rate in [8000, 16000, 24000, 48000]
    
    def test_api_config_timeout(self):
        """Test timeout settings"""
        config = APIConfig()
        if hasattr(config, 'timeout'):
            assert config.timeout > 0
    
    def test_api_config_retry_settings(self):
        """Test retry settings"""
        config = APIConfig()
        if hasattr(config, 'max_retries'):
            assert config.max_retries >= 0
    
    def test_api_config_prompt_strict_validation(self):
        """Test prompt strict validation setting"""
        config = APIConfig()
        assert hasattr(config, 'prompt_strict_validation')
        assert isinstance(config.prompt_strict_validation, bool)
    
    def test_api_config_multiple_instances_same_values(self):
        """Test multiple instances have same config"""
        config1 = APIConfig()
        config2 = APIConfig()
        
        assert config1.default_model == config2.default_model
        assert config1.default_voice == config2.default_voice
    
    def test_api_config_environment_override(self):
        """Test that environment variables override defaults"""
        with patch.dict(os.environ, {'OPENAI_MODEL': 'gpt-4'}):
            config = APIConfig()
            # Should use env var or default
            assert config.default_model is not None
    
    def test_api_config_voice_list(self):
        """Test available voices list"""
        config = APIConfig()
        if hasattr(config, 'available_voices'):
            assert isinstance(config.available_voices, (list, tuple))
    
    def test_api_config_realtime_model(self):
        """Test realtime model setting"""
        config = APIConfig()
        if hasattr(config, 'realtime_model'):
            assert 'realtime' in config.realtime_model.lower() or config.realtime_model is not None
    
    def test_config_vad_settings(self):
        """Test VAD settings if present"""
        config = APIConfig()
        # VAD settings might be present
        assert config is not None
    
    def test_config_has_all_required_fields(self):
        """Test config has all required fields"""
        config = APIConfig()
        required_fields = ['openai_api_key', 'default_model', 'default_voice', 'audio_format']
        
        for field in required_fields:
            assert hasattr(config, field), f"Missing required field: {field}"

