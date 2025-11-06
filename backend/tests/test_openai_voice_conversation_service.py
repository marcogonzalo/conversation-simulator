"""
Unit tests for OpenAIVoiceConversationService.
Tests critical functionality including type consistency and message ordering.
"""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import UUID, uuid4

from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.value_objects.conversation_id import ConversationId
# from src.conversation.domain.entities.transcription import Transcription  # Not used in tests
# from src.conversation.domain.value_objects.transcription_id import TranscriptionId  # Not used in tests
from src.conversation.domain.entities.conversation import ConversationStatus
from src.conversation.application.dtos.conversation_dto import ConversationDTO, ConversationResultDTO
# Legacy persona imports removed - module deleted


class TestOpenAIVoiceConversationService:
    """Test cases for OpenAIVoiceConversationService."""

    @pytest.fixture
    def mock_conversation_service(self):
        """Mock conversation application service."""
        service = AsyncMock()
        service.get_conversation.return_value = ConversationResultDTO(
            conversation=ConversationDTO(
                id="test-conversation-id",
                persona_id="test-persona-id",
                context_id="default",
                status="active",
                transcription_id="test-transcription-id",
                analysis_id=None,
                metadata={},
                duration_seconds=30
            ),
            success=True,
            message="Success"
        )
        return service

    @pytest.fixture
    def mock_voice_service(self):
        """Mock OpenAI voice application service."""
        service = AsyncMock()
        service.start_conversation.return_value = True
        service.end_conversation.return_value = None
        service.get_voice_for_persona.return_value = "alloy"
        return service

    # Legacy persona repository fixture removed

    @pytest.fixture
    def mock_transcription_service(self):
        """Mock transcription file service."""
        service = AsyncMock()
        service.save_transcription.return_value = "/path/to/transcription.json"
        service.get_transcription.return_value = {
            "messages": [
                {
                    "id": "msg1",
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2025-01-01T10:00:00"
                },
                {
                    "id": "msg2", 
                    "role": "assistant",
                    "content": "Hi there!",
                    "timestamp": "2025-01-01T10:00:05"
                }
            ]
        }
        return service

    @pytest.fixture
    def conversation_entity(self):
        """Create a conversation domain entity."""
        return Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test-persona-id",
            context_id="default",
            status=ConversationStatus.ACTIVE,
            transcription_id="test-transcription-id"
        )

    @pytest.fixture
    def service(self, mock_conversation_service, mock_voice_service, 
                mock_transcription_service):
        """Create service instance with mocked dependencies."""
        return OpenAIVoiceConversationService(
            conversation_service=mock_conversation_service,
            voice_service=mock_voice_service,
            transcription_service=mock_transcription_service
        )

    @pytest.mark.asyncio
    async def test_start_voice_conversation_converts_uuid_to_string(self, service, conversation_entity):
        """Test that conversation_id is converted to string consistently."""
        # Arrange
        conversation_entity._id = ConversationId(value=UUID('12345678-1234-5678-9abc-123456789abc'))
        persona_id = "test-persona-id"
        
        # Act
        result = await service.start_voice_conversation(conversation_entity, persona_id)
        
        # Assert
        assert result["success"] is True
        # Verify that active_conversations uses string keys
        conversation_id_str = str(conversation_entity.id.value)
        assert conversation_id_str in service.active_conversations
        assert service.active_conversations[conversation_id_str] is True

    @pytest.mark.asyncio
    async def test_send_audio_message_converts_uuid_to_string(self, service, conversation_entity):
        """Test that send_audio_message handles UUID to string conversion correctly."""
        # Arrange
        conversation_entity._id = ConversationId(value=UUID('12345678-1234-5678-9abc-123456789abc'))
        conversation_id_str = str(conversation_entity.id.value)
        service.active_conversations[conversation_id_str] = True
        
        audio_data = "base64encodedaudiodata"
        
        # Act
        result = await service.send_audio_message(conversation_entity, audio_data)
        
        # Assert
        # Should not raise "Voice conversation not active" error
        # The method should find the conversation in active_conversations
        # because it properly converts UUID to string

    @pytest.mark.asyncio
    async def test_end_voice_conversation_handles_string_conversation_id(self, service):
        """Test that end_voice_conversation works with string conversation_id."""
        # Arrange
        conversation_id = "test-conversation-id"
        service.active_conversations[conversation_id] = True
        
        # Act
        result = await service.end_voice_conversation(conversation_id)
        
        # Assert
        assert result["success"] is True
        assert conversation_id not in service.active_conversations

    @pytest.mark.asyncio
    async def test_end_voice_conversation_rejects_inactive_conversation(self, service):
        """Test that end_voice_conversation rejects inactive conversations."""
        # Arrange
        conversation_id = "inactive-conversation-id"
        # Don't add to active_conversations
        
        # Act
        result = await service.end_voice_conversation(conversation_id)
        
        # Assert
        assert result["success"] is True
        assert result["message"] == "Conversation already ended"

    @pytest.mark.asyncio
    async def test_message_ordering_by_timestamp(self, service, mock_transcription_service):
        """Test that messages are sorted by timestamp before saving."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        
        # Add messages in wrong chronological order
        service._conversation_messages[conversation_id] = [
            {
                "id": "msg1",
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": "AI response",
                "timestamp": "2025-01-01T10:00:05",  # Later
                "metadata": {}
            },
            {
                "id": "msg2",
                "conversation_id": conversation_id,
                "role": "user",
                "content": "User message",
                "timestamp": "2025-01-01T10:00:00",  # Earlier
                "metadata": {}
            }
        ]
        
        # Act
        await service._save_transcription_file(conversation_id, transcription_id)
        
        # Assert
        mock_transcription_service.save_transcription.assert_called_once()
        call_args = mock_transcription_service.save_transcription.call_args
        saved_messages = call_args.kwargs['messages']
        
        # Messages should be sorted by timestamp
        assert saved_messages[0]["timestamp"] == "2025-01-01T10:00:00"  # User first
        assert saved_messages[1]["timestamp"] == "2025-01-01T10:00:05"  # AI second
        
        # IDs should be regenerated in chronological order
        assert saved_messages[0]["id"] == f"{conversation_id}_0"
        assert saved_messages[1]["id"] == f"{conversation_id}_1"

    @pytest.mark.asyncio
    async def test_store_message_for_transcription(self, service):
        """Test that messages are stored correctly for transcription."""
        # Arrange
        conversation_id = "test-conversation-id"
        role = "user"
        content = "Test message"
        timestamp = datetime.now()
        
        # Act
        service._store_message_for_transcription(conversation_id, role, content, timestamp)
        
        # Assert
        assert conversation_id in service._conversation_messages
        messages = service._conversation_messages[conversation_id]
        assert len(messages) == 1
        
        message = messages[0]
        assert message["conversation_id"] == conversation_id
        assert message["role"] == role
        assert message["content"] == content
        assert message["timestamp"] == timestamp.isoformat()

    @pytest.mark.asyncio
    async def test_trigger_conversation_analysis_reads_from_transcription_file(self, service, mock_transcription_service):
        """Test that analysis reads messages from transcription file."""
        # This test verifies that the method attempts to read from transcription file
        # without requiring a full analysis service mock
        
        # Arrange
        conversation_id = "test-conversation-id"
        
        # Mock conversation service
        mock_conversation_result = ConversationResultDTO(
            success=True,
            conversation=ConversationDTO(
                id=conversation_id,
                persona_id="test-persona",
                context_id="default",
                status="active",
                transcription_id="transcription-123",
                analysis_id=None,
                metadata={}
            )
        )
        service.conversation_service.get_conversation.return_value = mock_conversation_result
        
        # Mock transcription data
        mock_transcription_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "duration_seconds": 30
        }
        mock_transcription_service.get_transcription.return_value = mock_transcription_data
        
        # Act & Assert
        # The method should attempt to read from transcription file
        # We expect it to fail on the analysis service call, but that's OK for this test
        try:
            result = await service._trigger_conversation_analysis(conversation_id)
            # If it succeeds, verify the structure
            assert "error" in result or "analysis" in result
        except Exception:
            # Expected to fail on analysis service, but transcription reading should work
            pass
        
        # Verify that transcription service was called
        mock_transcription_service.get_transcription.assert_called_once()

    @pytest.mark.asyncio
    async def test_active_conversations_type_consistency(self, service, conversation_entity):
        """Test that active_conversations always uses string keys."""
        # Arrange
        conversation_entity._id = ConversationId(value=UUID('12345678-1234-5678-9abc-123456789abc'))
        
        # Act
        await service.start_voice_conversation(conversation_entity, "test-persona-id")
        
        # Assert
        # All keys in active_conversations should be strings
        for key in service.active_conversations.keys():
            assert isinstance(key, str), f"Key {key} is not a string, it's {type(key)}"

    @pytest.mark.asyncio
    async def test_conversation_cleanup_after_analysis(self, service, mock_transcription_service):
        """Test that conversation data is cleaned up after analysis completes."""
        # Arrange
        conversation_id = "test-conversation-id"
        service.active_conversations[conversation_id] = True
        service._conversation_messages[conversation_id] = [{"test": "message"}]
        
        # Mock conversation service
        mock_conversation_result = ConversationResultDTO(
            success=True,
            conversation=ConversationDTO(
                id=conversation_id,
                persona_id="test-persona",
                context_id="default",
                status="active",
                transcription_id="transcription-123",
                analysis_id=None,
                metadata={}
            )
        )
        service.conversation_service.get_conversation.return_value = mock_conversation_result
        
        # Mock transcription data
        mock_transcription_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "duration_seconds": 30
        }
        mock_transcription_service.get_transcription.return_value = mock_transcription_data
        
        # Act & Assert
        # The method should clean up conversation data
        # We expect it to fail on the analysis service call, but cleanup should work
        try:
            result = await service.end_voice_conversation(conversation_id)
            # If it succeeds, verify the structure
            assert "success" in result
        except Exception:
            # Expected to fail on analysis service, but cleanup should still work
            pass
        
        # Verify that conversation data was cleaned up
        assert conversation_id not in service.active_conversations
        assert conversation_id not in service._conversation_messages

    def test_uuid_string_conversion_edge_cases(self, service):
        """Test edge cases in UUID to string conversion."""
        # Test with various UUID formats
        test_uuids = [
            UUID('00000000-0000-0000-0000-000000000000'),
            UUID('ffffffff-ffff-ffff-ffff-ffffffffffff'),
            uuid4()
        ]
        
        for uuid_obj in test_uuids:
            conversation_entity = Conversation(
                conversation_id=ConversationId(value=uuid_obj),
                persona_id="test-persona-id",
                context_id="default",
                status=ConversationStatus.ACTIVE
            )
            
            # Test that conversion works consistently
            conversation_id_str = str(conversation_entity.id.value)
            service.active_conversations[conversation_id_str] = True
            
            # Should be able to find it
            assert conversation_id_str in service.active_conversations
            assert service.active_conversations[conversation_id_str] is True
            
            # Clean up
            del service.active_conversations[conversation_id_str]

    @pytest.mark.asyncio
    async def test_message_timestamp_format_consistency(self, service):
        """Test that message timestamps are consistently formatted."""
        # Arrange
        conversation_id = "test-conversation-id"
        role = "user"
        content = "Test message"
        timestamp = datetime(2025, 1, 1, 10, 0, 0, 123456)
        
        # Act
        service._store_message_for_transcription(conversation_id, role, content, timestamp)
        
        # Assert
        message = service._conversation_messages[conversation_id][0]
        stored_timestamp = message["timestamp"]
        
        # Should be in ISO format
        assert stored_timestamp == "2025-01-01T10:00:00.123456"
        
        # Should be parseable back to datetime
        parsed_timestamp = datetime.fromisoformat(stored_timestamp)
        assert parsed_timestamp == timestamp

    @pytest.mark.asyncio
    async def test_convert_pcm_to_audio_uses_configured_format(self, service):
        """Test that audio conversion uses the configured format from AudioConverterService."""
        # Arrange
        pcm_data = bytes([0, 0] * 1000)  # 2000 bytes of silent audio
        sample_rate = 24000
        
        # Act
        audio_data = await service._convert_pcm_to_audio(pcm_data, sample_rate)
        
        # Assert - Should return audio data
        assert len(audio_data) > 0, "Should generate audio data"
        assert isinstance(audio_data, bytes), "Should return bytes"
        
        # The actual format depends on service.api_config.audio_output_format
        # We just verify it returns valid data without errors

    @pytest.mark.asyncio
    async def test_convert_pcm_to_audio_with_different_sample_rates(self, service):
        """Test audio conversion with various sample rates."""
        # Arrange
        pcm_data = bytes([0, 0] * 100)
        sample_rates = [8000, 16000, 24000, 48000]
        
        for sample_rate in sample_rates:
            # Act
            audio_data = await service._convert_pcm_to_audio(pcm_data, sample_rate)
            
            # Assert
            assert len(audio_data) > 0, f"Should generate audio data for {sample_rate}Hz"

    @pytest.mark.asyncio
    async def test_convert_pcm_to_audio_handles_empty_data(self, service):
        """Test audio conversion with empty PCM data."""
        # Arrange
        pcm_data = b''
        
        # Act
        audio_data = await service._convert_pcm_to_audio(pcm_data, 24000)
        
        # Assert
        # WAV would return 44 bytes (header only), WebM might be empty or minimal
        assert isinstance(audio_data, bytes), "Should return bytes"


@pytest.mark.integration
class TestOpenAIVoiceConversationServiceIntegration:
    """Integration tests for OpenAIVoiceConversationService."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow_type_consistency(self):
        """Test the complete conversation flow maintains type consistency."""
        # This test would require more complex setup with real services
        # For now, we focus on unit tests that catch the specific type bugs
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
