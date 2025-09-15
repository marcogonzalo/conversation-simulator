import pytest
import asyncio
import json
import base64
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
from src.persona.domain.entities.persona import Persona, AccentType
from src.persona.domain.value_objects.personality_traits import PersonalityTraits


@pytest.mark.integration
class TestVoiceConversationIntegration:
    """Integration tests for voice conversation flow."""

    @pytest.fixture
    def mock_persona(self):
        """Create a mock persona for testing."""
        return Persona(
            id="test-persona-id",
            name="Test Persona",
            description="A test persona for integration testing",
            background="Test background",
            personality_traits=PersonalityTraits(["friendly", "analytical"]),
            accent=AccentType.CARIBBEAN_SPANISH,
            conversation_goals=["Test goal"],
            pain_points=["Test pain"],
            objections=["Test objection"],
            decision_factors=["Test factor"],
            budget_range="Test budget",
            timeline="Test timeline",
            company_size="Test size",
            industry="Test industry",
            prompt_template="Test template"
        )

    @pytest.fixture
    def conversation_service(self):
        """Create conversation service for integration testing."""
        with patch('src.conversation.application.services.openai_voice_conversation_service.OpenAIVoiceApplicationService'):
            service = OpenAIVoiceConversationService()
            service.voice_service = Mock()
            service.persona_repository = Mock()
            return service

    @pytest.mark.asyncio
    async def test_complete_voice_conversation_flow(self, conversation_service, mock_persona):
        """Test complete voice conversation flow from start to end."""
        # Setup mocks
        conversation_service.persona_repository.get_by_id = AsyncMock(return_value=mock_persona)
        conversation_service.voice_service.connect = AsyncMock(return_value=True)
        conversation_service.voice_service.configure_session = AsyncMock()
        conversation_service.voice_service.send_audio = AsyncMock(return_value=True)
        conversation_service.voice_service.disconnect = AsyncMock()
        
        # Mock audio response
        mock_audio_chunks = ["chunk1", "chunk2", "chunk3"]
        conversation_service._on_audio_chunk = Mock()
        conversation_service._on_transcript = Mock()
        conversation_service._send_complete_audio_response = AsyncMock()
        
        conversation_id = "test-conversation-id"
        persona_id = "test-persona-id"
        
        # Step 1: Start conversation
        result = await conversation_service.start_voice_conversation(conversation_id, persona_id)
        assert result is True
        
        # Step 2: Send audio
        audio_data = b"test audio data"
        result = await conversation_service.send_audio(conversation_id, audio_data)
        assert result is True
        
        # Step 3: Simulate audio chunks received
        for chunk in mock_audio_chunks:
            conversation_service._on_audio_chunk(conversation_id, chunk)
        
        # Step 4: Simulate transcript received
        conversation_service._on_transcript(conversation_id, "Hello, how can I help you?")
        
        # Step 5: End conversation
        result = await conversation_service.end_voice_conversation(conversation_id)
        assert result is True
        
        # Verify all methods were called
        conversation_service.voice_service.connect.assert_called_once()
        conversation_service.voice_service.send_audio.assert_called_once_with(audio_data)
        conversation_service.voice_service.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_audio_processing_pipeline(self, conversation_service):
        """Test audio processing pipeline with real data flow."""
        conversation_id = "test-conversation-id"
        
        # Mock audio data
        mock_audio_data = b"mock webm audio data"
        mock_pcm_data = b"mock pcm audio data"
        
        # Mock FFmpeg conversion
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(
                returncode=0,
                stdout=mock_pcm_data
            )
            
            # Test audio conversion
            result = await conversation_service._convert_audio_format(mock_audio_data)
            assert result == mock_pcm_data

    @pytest.mark.asyncio
    async def test_error_handling_in_conversation_flow(self, conversation_service, mock_persona):
        """Test error handling throughout conversation flow."""
        conversation_id = "test-conversation-id"
        persona_id = "test-persona-id"
        
        # Test 1: Persona not found
        conversation_service.persona_repository.get_by_id = AsyncMock(return_value=None)
        result = await conversation_service.start_voice_conversation(conversation_id, persona_id)
        assert result is False
        
        # Test 2: Connection failure
        conversation_service.persona_repository.get_by_id = AsyncMock(return_value=mock_persona)
        conversation_service.voice_service.connect = AsyncMock(return_value=False)
        result = await conversation_service.start_voice_conversation(conversation_id, persona_id)
        assert result is False
        
        # Test 3: Audio sending failure
        conversation_service.voice_service.connect = AsyncMock(return_value=True)
        conversation_service.voice_service.configure_session = AsyncMock()
        conversation_service.voice_service.send_audio = AsyncMock(return_value=False)
        
        await conversation_service.start_voice_conversation(conversation_id, persona_id)
        result = await conversation_service.send_audio(conversation_id, b"test audio")
        assert result is False

    @pytest.mark.asyncio
    async def test_websocket_message_handling(self):
        """Test WebSocket message handling integration."""
        from src.api.routes.websocket import handle_websocket_message
        
        # Mock WebSocket and conversation service
        mock_websocket = Mock()
        mock_conversation_service = Mock()
        mock_conversation_service.start_voice_conversation = AsyncMock(return_value=True)
        mock_conversation_service.send_audio = AsyncMock(return_value=True)
        mock_conversation_service.end_voice_conversation = AsyncMock(return_value=True)
        
        # Test start conversation message
        message = {
            "type": "start_voice_conversation",
            "persona_id": "test-persona-id"
        }
        
        await handle_websocket_message(
            websocket=mock_websocket,
            message=message,
            conversation_id="test-conversation-id",
            conversation_service=mock_conversation_service
        )
        
        mock_conversation_service.start_voice_conversation.assert_called_once()
        
        # Test audio message
        message = {
            "type": "audio_message",
            "audio_data": "base64_audio_data"
        }
        
        await handle_websocket_message(
            websocket=mock_websocket,
            message=message,
            conversation_id="test-conversation-id",
            conversation_service=mock_conversation_service
        )
        
        mock_conversation_service.send_audio.assert_called_once()
        
        # Test end conversation message
        message = {
            "type": "end_voice_conversation"
        }
        
        await handle_websocket_message(
            websocket=mock_websocket,
            message=message,
            conversation_id="test-conversation-id",
            conversation_service=mock_conversation_service
        )
        
        mock_conversation_service.end_voice_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_audio_chunk_accumulation(self, conversation_service):
        """Test audio chunk accumulation and WAV creation."""
        conversation_id = "test-conversation-id"
        
        # Initialize audio chunks
        conversation_service.audio_chunks = {}
        
        # Simulate receiving multiple audio chunks
        chunks = ["chunk1", "chunk2", "chunk3", "chunk4"]
        for chunk in chunks:
            conversation_service._on_audio_chunk(conversation_id, chunk)
        
        # Verify chunks are accumulated
        assert conversation_id in conversation_service.audio_chunks
        assert conversation_service.audio_chunks[conversation_id] == chunks
        
        # Test WAV creation
        with patch('src.conversation.application.services.openai_voice_conversation_service.struct') as mock_struct:
            mock_struct.pack.return_value = b"wav_header"
            
            pcm_data = b"combined_pcm_data"
            sample_rate = 24000
            
            result = conversation_service._create_wav_from_pcm(pcm_data, sample_rate)
            
            assert result.startswith(b"wav_header")
            assert pcm_data in result

    @pytest.mark.asyncio
    async def test_conversation_cleanup(self, conversation_service):
        """Test conversation cleanup after end."""
        conversation_id = "test-conversation-id"
        
        # Setup conversation state
        conversation_service.audio_chunks = {conversation_id: ["chunk1", "chunk2"]}
        conversation_service.voice_service = Mock()
        conversation_service.voice_service.disconnect = AsyncMock()
        
        # End conversation
        result = await conversation_service.end_voice_conversation(conversation_id)
        
        assert result is True
        conversation_service.voice_service.disconnect.assert_called_once()
        
        # Verify cleanup
        conversation_service._cleanup_conversation(conversation_id)
        assert conversation_id not in conversation_service.audio_chunks

    @pytest.mark.asyncio
    async def test_concurrent_conversations(self, conversation_service, mock_persona):
        """Test handling multiple concurrent conversations."""
        conversation_service.persona_repository.get_by_id = AsyncMock(return_value=mock_persona)
        conversation_service.voice_service.connect = AsyncMock(return_value=True)
        conversation_service.voice_service.configure_session = AsyncMock()
        conversation_service.voice_service.send_audio = AsyncMock(return_value=True)
        conversation_service.voice_service.disconnect = AsyncMock()
        
        # Start multiple conversations
        conversation_ids = ["conv1", "conv2", "conv3"]
        tasks = []
        
        for conv_id in conversation_ids:
            task = conversation_service.start_voice_conversation(conv_id, "test-persona-id")
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results)
        
        # Test sending audio to different conversations
        for conv_id in conversation_ids:
            result = await conversation_service.send_audio(conv_id, b"test audio")
            assert result is True
        
        # Test ending all conversations
        for conv_id in conversation_ids:
            result = await conversation_service.end_voice_conversation(conv_id)
            assert result is True
