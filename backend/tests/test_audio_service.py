import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
from src.shared.infrastructure.external_apis.api_config import api_config


@pytest.mark.unit
class TestOpenAIVoiceService:
    """Test cases for OpenAI Voice Service."""

    @pytest.fixture
    def voice_service(self):
        """Create a voice service instance for testing."""
        with patch('src.audio.infrastructure.services.openai_voice_service.websockets.connect'):
            service = OpenAIVoiceService(api_config)
            service.websocket = Mock()
            return service

    @pytest.mark.asyncio
    async def test_connect_success(self, voice_service):
        """Test successful connection to OpenAI."""
        voice_service.websocket.recv = AsyncMock(return_value='{"type": "session.created"}')
        
        result = await voice_service.connect()
        
        assert result is True
        assert voice_service.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, voice_service):
        """Test connection failure handling."""
        voice_service.websocket.recv = AsyncMock(side_effect=Exception("Connection failed"))
        
        result = await voice_service.connect()
        
        assert result is False
        assert voice_service.is_connected is False

    @pytest.mark.asyncio
    async def test_send_audio_success(self, voice_service):
        """Test successful audio sending."""
        voice_service.is_connected = True
        voice_service.websocket.send = AsyncMock()
        
        audio_data = b"mock audio data"
        result = await voice_service.send_audio(audio_data)
        
        assert result is True
        voice_service.websocket.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_audio_not_connected(self, voice_service):
        """Test audio sending when not connected."""
        voice_service.is_connected = False
        
        audio_data = b"mock audio data"
        result = await voice_service.send_audio(audio_data)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect(self, voice_service):
        """Test disconnection."""
        voice_service.is_connected = True
        voice_service.websocket.close = AsyncMock()
        
        await voice_service.disconnect()
        
        assert voice_service.is_connected is False
        voice_service.websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_audio_chunk(self, voice_service):
        """Test handling audio chunk events."""
        mock_callback = Mock()
        voice_service.on_audio_chunk = mock_callback
        
        event_data = {
            "type": "conversation.output_audio.delta",
            "delta": {
                "type": "audio.delta",
                "audio": "base64_audio_data"
            }
        }
        
        await voice_service._handle_event(event_data)
        
        mock_callback.assert_called_once_with("base64_audio_data")

    @pytest.mark.asyncio
    async def test_handle_event_transcript(self, voice_service):
        """Test handling transcript events."""
        mock_callback = Mock()
        voice_service.on_transcript = mock_callback
        
        event_data = {
            "type": "conversation.output_audio.delta",
            "delta": {
                "type": "transcript.delta",
                "transcript": "Hello world"
            }
        }
        
        await voice_service._handle_event(event_data)
        
        mock_callback.assert_called_once_with("Hello world")

    @pytest.mark.asyncio
    async def test_handle_event_error(self, voice_service):
        """Test handling error events."""
        mock_callback = Mock()
        voice_service.on_error = mock_callback
        
        event_data = {
            "type": "error",
            "error": {
                "type": "invalid_request_error",
                "message": "Invalid request"
            }
        }
        
        await voice_service._handle_event(event_data)
        
        mock_callback.assert_called_once_with("Invalid request")

    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_convert_audio_format(self, mock_subprocess, voice_service):
        """Test audio format conversion."""
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout=b"converted audio data"
        )
        
        audio_data = b"webm audio data"
        result = await voice_service._convert_audio_format(audio_data)
        
        assert result == b"converted audio data"
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_convert_audio_format_failure(self, mock_subprocess, voice_service):
        """Test audio format conversion failure."""
        mock_subprocess.return_value = Mock(
            returncode=1,
            stderr=b"Conversion failed"
        )
        
        audio_data = b"webm audio data"
        result = await voice_service._convert_audio_format(audio_data)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_listen_for_events_stop(self, voice_service):
        """Test stopping event listening."""
        voice_service.websocket.recv = AsyncMock(side_effect=Exception("Connection closed"))
        voice_service.is_connected = True
        
        # Should not raise exception
        await voice_service._listen_for_events()
        
        assert voice_service.is_connected is False
