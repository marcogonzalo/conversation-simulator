"""
Tests for Gemini Voice Service.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from src.audio.infrastructure.services.gemini_voice_service import GeminiVoiceService
from src.shared.infrastructure.external_apis.api_config import APIConfig
from src.conversation.domain.entities.message import MessageRole


@pytest.fixture
def mock_api_config():
    """Create a mock API config for testing."""
    config = Mock(spec=APIConfig)
    config.gemini_api_key = "test-gemini-api-key"
    config.gemini_voice_model = "gemini-2.5-flash"
    config.voice_detection_threshold = 0.5
    config.voice_detection_prefix_padding_ms = 300
    config.voice_detection_silence_duration_ms = 500
    config.prompt_strict_validation = False
    config.audio_min_bytes_pcm = 4800
    config.audio_min_duration_ms = 100
    return config


@pytest.fixture
def gemini_service(mock_api_config):
    """Create a GeminiVoiceService instance."""
    return GeminiVoiceService(api_config=mock_api_config)


class TestGeminiVoiceServiceInitialization:
    """Test suite for GeminiVoiceService initialization."""
    
    def test_service_initialization(self, gemini_service, mock_api_config):
        """Test that service initializes correctly."""
        assert gemini_service.api_config == mock_api_config
        assert gemini_service.client is None
        assert gemini_service.session is None
        assert gemini_service._session_cm is None
        assert not gemini_service.is_connected
        assert gemini_service.conversation_id is None
    
    def test_provider_property(self, gemini_service):
        """Test that provider property returns 'gemini'."""
        assert gemini_service.provider == "gemini"
    
    def test_is_connected_initially_false(self, gemini_service):
        """Test that is_connected is False initially."""
        assert not gemini_service.is_connected
    
    @pytest.mark.asyncio
    async def test_async_context_manager_entry_success(self, gemini_service):
        """Test async context manager entry with valid API key."""
        with patch('src.audio.infrastructure.services.gemini_voice_service.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            service = await gemini_service.__aenter__()
            
            assert service.client is not None
            assert service == gemini_service
            mock_client_class.assert_called_once_with(api_key="test-gemini-api-key")
    
    @pytest.mark.asyncio
    async def test_async_context_manager_entry_no_api_key(self, mock_api_config):
        """Test async context manager entry fails without API key."""
        mock_api_config.gemini_api_key = None
        service = GeminiVoiceService(api_config=mock_api_config)
        
        with pytest.raises(ValueError, match="Gemini API key not configured"):
            await service.__aenter__()


class TestGeminiVoiceServiceConnection:
    """Test suite for connection functionality."""
    
    @pytest.mark.asyncio
    async def test_connect_without_initialization(self, gemini_service):
        """Test that connect fails if service not initialized."""
        on_audio_chunk = AsyncMock()
        on_transcript = AsyncMock()
        on_error = AsyncMock()
        
        with pytest.raises(RuntimeError, match="Service not initialized"):
            await gemini_service.connect(
                conversation_id="test-123",
                instructions="Test instructions",
                voice_id="Puck",
                on_audio_chunk=on_audio_chunk,
                on_transcript=on_transcript,
                on_error=on_error
            )
    
    @pytest.mark.asyncio
    async def test_connect_success(self, gemini_service):
        """Test successful connection to Gemini Live API."""
        # Setup mocks
        mock_client = Mock()
        mock_aio = Mock()
        mock_live = Mock()
        mock_session = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        
        mock_client.aio = mock_aio
        mock_aio.live = mock_live
        mock_live.connect = Mock(return_value=mock_cm)
        mock_session.send_client_content = AsyncMock()
        
        gemini_service.client = mock_client
        
        on_audio_chunk = AsyncMock()
        on_transcript = AsyncMock()
        on_error = AsyncMock()
        
        # Mock the listen task to prevent it from running
        with patch.object(gemini_service, '_listen_for_events', new=AsyncMock()):
            result = await gemini_service.connect(
                conversation_id="test-123",
                instructions="Test instructions",
                voice_id="Puck",
                on_audio_chunk=on_audio_chunk,
                on_transcript=on_transcript,
                on_error=on_error
            )
        
        assert result is True
        assert gemini_service.is_connected
        assert gemini_service.conversation_id == "test-123"
        mock_session.send_client_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, gemini_service):
        """Test connection failure handling."""
        mock_client = Mock()
        mock_aio = Mock()
        mock_live = Mock()
        
        mock_client.aio = mock_aio
        mock_aio.live = mock_live
        mock_live.connect = AsyncMock(side_effect=Exception("Connection failed"))
        
        gemini_service.client = mock_client
        
        on_audio_chunk = AsyncMock()
        on_transcript = AsyncMock()
        on_error = AsyncMock()
        
        result = await gemini_service.connect(
            conversation_id="test-123",
            instructions="Test instructions",
            voice_id="Puck",
            on_audio_chunk=on_audio_chunk,
            on_transcript=on_transcript,
            on_error=on_error
        )
        
        assert result is False
        assert not gemini_service.is_connected
        on_error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect(self, gemini_service):
        """Test disconnection from Gemini Live API."""
        # Setup connected state
        gemini_service._is_connected = True
        gemini_service.session = Mock()
        mock_cm = AsyncMock()
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        gemini_service._session_cm = mock_cm
        
        # Create a real asyncio task that can be cancelled
        async def dummy_listen():
            await asyncio.sleep(10)
        
        gemini_service._listen_task = asyncio.create_task(dummy_listen())
        gemini_service._audio_timer = None
        
        await gemini_service.disconnect()
        
        assert not gemini_service.is_connected
        assert gemini_service.session is None
        assert gemini_service._session_cm is None
        assert gemini_service._listen_task is None
        mock_cm.__aexit__.assert_called_once_with(None, None, None)


class TestGeminiVoiceServiceAudio:
    """Test suite for audio functionality."""
    
    @pytest.mark.asyncio
    async def test_send_audio_not_connected(self, gemini_service):
        """Test that send_audio fails when not connected."""
        audio_data = b"test audio data"
        result = await gemini_service.send_audio(audio_data)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_audio_success(self, gemini_service):
        """Test successful audio sending."""
        gemini_service._is_connected = True
        gemini_service.session = Mock()
        
        audio_data = b"test audio data"
        
        with patch.object(gemini_service, '_convert_audio_to_pcm16', new=AsyncMock(return_value=b"pcm audio")):
            with patch.object(gemini_service, '_process_accumulated_audio', new=AsyncMock()):
                result = await gemini_service.send_audio(audio_data)
        
        assert result is True
        assert len(gemini_service._audio_buffer) == 1
    
    @pytest.mark.asyncio
    async def test_send_audio_conversion_failure(self, gemini_service):
        """Test audio sending when conversion fails."""
        gemini_service._is_connected = True
        gemini_service.session = Mock()
        
        audio_data = b"test audio data"
        
        with patch.object(gemini_service, '_convert_audio_to_pcm16', new=AsyncMock(return_value=None)):
            result = await gemini_service.send_audio(audio_data)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_process_accumulated_audio_success(self, gemini_service, mock_api_config):
        """Test processing accumulated audio successfully."""
        gemini_service._is_connected = True
        mock_session = AsyncMock()
        gemini_service.session = mock_session
        
        # Add audio to buffer (large enough to pass validation)
        test_audio = b"x" * 5000  # 5000 bytes (> 4800 minimum)
        gemini_service._audio_buffer = [test_audio]
        
        await gemini_service._process_accumulated_audio()
        
        # Verify session.send was called with correct parameters
        assert mock_session.send_realtime_input.call_count == 2
        first_call_kwargs = mock_session.send_realtime_input.call_args_list[0].kwargs
        from google.genai import types  # import inside test to avoid global dependency
        assert isinstance(first_call_kwargs["audio"], types.Blob)
        assert first_call_kwargs["audio"].mime_type == "audio/pcm;rate=16000"
        assert first_call_kwargs["audio"].data == test_audio
        second_call_kwargs = mock_session.send_realtime_input.call_args_list[1].kwargs
        assert second_call_kwargs.get("audio_stream_end") is True
    
    @pytest.mark.asyncio
    async def test_process_accumulated_audio_too_short(self, gemini_service, mock_api_config):
        """Test that too-short audio is rejected."""
        gemini_service._is_connected = True
        mock_session = AsyncMock()
        gemini_service.session = mock_session
        
        # Add audio that's too short
        test_audio = b"x" * 100  # Only 100 bytes (< 4800 minimum)
        gemini_service._audio_buffer = [test_audio]
        
        await gemini_service._process_accumulated_audio()
        
        # Verify session.send_realtime_input was NOT called
        mock_session.send_realtime_input.assert_not_called()


class TestGeminiVoiceServiceVoiceMapping:
    """Test suite for voice accent mapping."""
    
    def test_get_voice_for_accent_mexicano(self, gemini_service):
        """Test mapping for Mexican accent."""
        voice_id = gemini_service.get_voice_for_accent("mexicano")
        assert voice_id == "Puck"
    
    def test_get_voice_for_accent_peruano(self, gemini_service):
        """Test mapping for Peruvian accent."""
        voice_id = gemini_service.get_voice_for_accent("peruano")
        assert voice_id == "Charon"
    
    def test_get_voice_for_accent_venezuelan(self, gemini_service):
        """Test mapping for Venezuelan accent."""
        voice_id = gemini_service.get_voice_for_accent("venezolano")
        assert voice_id == "Kore"
    
    def test_get_voice_for_accent_neutral(self, gemini_service):
        """Test mapping for neutral accent."""
        voice_id = gemini_service.get_voice_for_accent("neutral")
        assert voice_id == "Puck"
    
    def test_get_voice_for_accent_unknown(self, gemini_service):
        """Test mapping for unknown accent defaults to Puck."""
        voice_id = gemini_service.get_voice_for_accent("unknown_accent")
        assert voice_id == "Puck"
    
    def test_get_voice_for_accent_case_insensitive(self, gemini_service):
        """Test that accent mapping is case insensitive."""
        voice_id_lower = gemini_service.get_voice_for_accent("mexicano")
        voice_id_upper = gemini_service.get_voice_for_accent("MEXICANO")
        voice_id_mixed = gemini_service.get_voice_for_accent("MeXiCaNo")
        
        assert voice_id_lower == voice_id_upper == voice_id_mixed == "Puck"


class TestGeminiVoiceServiceFactory:
    """Test suite for VoiceServiceFactory integration."""
    
    def test_factory_creates_gemini_service(self, mock_api_config):
        """Test that factory creates Gemini service correctly."""
        from src.shared.infrastructure.external_apis.voice_service_factory import VoiceServiceFactory
        
        service = VoiceServiceFactory.create_voice_service(
            voice_provider="gemini",
            api_config_instance=mock_api_config
        )
        
        assert service is not None
        assert isinstance(service, GeminiVoiceService)
        assert service.provider == "gemini"
    
    def test_factory_fails_without_api_key(self):
        """Test that factory fails to create service without API key."""
        from src.shared.infrastructure.external_apis.voice_service_factory import VoiceServiceFactory
        
        config = Mock(spec=APIConfig)
        config.gemini_api_key = None
        
        service = VoiceServiceFactory.create_voice_service(
            voice_provider="gemini",
            api_config_instance=config
        )
        
        assert service is None
    
    def test_factory_available_providers_includes_gemini(self):
        """Test that available providers includes Gemini."""
        from src.shared.infrastructure.external_apis.voice_service_factory import VoiceServiceFactory
        
        providers = VoiceServiceFactory.get_available_voice_providers()
        
        assert "gemini" in providers
        assert "openai" in providers
    
    def test_factory_validates_gemini_provider(self):
        """Test that factory validates Gemini as supported provider."""
        from src.shared.infrastructure.external_apis.voice_service_factory import VoiceServiceFactory
        
        is_valid = VoiceServiceFactory.validate_voice_provider("gemini")
        
        assert is_valid is True


class TestGeminiVoiceServiceConfiguration:
    """Test suite for configuration handling."""
    
    def test_api_config_has_gemini_settings(self):
        """Test that APIConfig includes Gemini configuration."""
        from src.shared.infrastructure.external_apis.api_config import APIConfig
        import os
        
        # Set test environment variables
        os.environ["GEMINI_API_KEY"] = "test-key"
        os.environ["GEMINI_VOICE_MODEL"] = "gemini-2.5-flash"
        
        config = APIConfig()
        
        assert config.gemini_api_key == "test-key"
        assert config.gemini_voice_model == "gemini-2.5-flash"
        
        # Clean up
        del os.environ["GEMINI_API_KEY"]
        del os.environ["GEMINI_VOICE_MODEL"]
    
    def test_api_config_gemini_defaults(self):
        """Test that APIConfig uses correct defaults for Gemini."""
        from src.shared.infrastructure.external_apis.api_config import APIConfig
        import os
        
        # Ensure no Gemini env vars are set
        gemini_vars = ["GEMINI_API_KEY", "GEMINI_VOICE_MODEL"]
        for var in gemini_vars:
            if var in os.environ:
                del os.environ[var]
        
        config = APIConfig()
        
        assert config.gemini_voice_model == "gemini-2.0-flash-exp"
    
    def test_api_config_get_gemini_voice_config(self):
        """Test getting Gemini voice configuration."""
        from src.shared.infrastructure.external_apis.api_config import APIConfig
        from src.shared.infrastructure.config.ai_defaults import GEMINI_VOICE_DEFAULTS
        import os
        
        # Set test environment variables
        os.environ["GEMINI_API_KEY"] = "test-gemini-api-key"
        os.environ["GEMINI_VOICE_MODEL"] = "gemini-2.5-flash"
        
        config = APIConfig()
        config_dict = config.get_gemini_voice_config()
        
        assert config_dict["api_key"] == "test-gemini-api-key"
        assert config_dict["model"] == "gemini-2.5-flash"
        assert config_dict["temperature"] == GEMINI_VOICE_DEFAULTS.temperature
        assert config_dict["max_tokens"] == GEMINI_VOICE_DEFAULTS.max_tokens
        assert config_dict["default_voice"] == GEMINI_VOICE_DEFAULTS.default_voice
        
        # Clean up
        del os.environ["GEMINI_API_KEY"]
        del os.environ["GEMINI_VOICE_MODEL"]
    
    def test_gemini_voice_defaults(self):
        """Test that Gemini voice defaults are correctly configured."""
        from src.shared.infrastructure.config.ai_defaults import GEMINI_VOICE_DEFAULTS
        
        assert GEMINI_VOICE_DEFAULTS.temperature == 0.8
        assert GEMINI_VOICE_DEFAULTS.max_tokens == 4096
        assert GEMINI_VOICE_DEFAULTS.default_voice == "Puck"


@pytest.mark.integration
class TestGeminiVoiceServiceIntegration:
    """Integration tests for GeminiVoiceService (requires API key)."""
    
    @pytest.mark.skip(reason="Requires actual Gemini API key")
    @pytest.mark.asyncio
    async def test_real_connection(self):
        """Test real connection to Gemini Live API."""
        # This test would require a real API key and should be run manually
        pass

