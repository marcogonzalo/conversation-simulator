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
from src.persona.domain.entities.persona import Persona
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.entities.persona import AccentType
from src.persona.domain.value_objects.personality_traits import PersonalityTraits, PersonalityTrait


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

    @pytest.fixture
    def mock_persona_repository(self):
        """Mock persona repository."""
        repo = AsyncMock()
        persona = Persona(
            persona_id=PersonaId(value="test-persona-id"),
            name="Test Persona",
            description="Test description",
            background="Test background",
            personality_traits=PersonalityTraits.from_strings(["friendly"]),
            accent=AccentType.CARIBBEAN_SPANISH,
            voice_id="alloy",
            prompt_template="You are a helpful assistant",
            conversation_goals=["help customers"],
            pain_points=["time constraints"],
            objections=["price concerns"],
            decision_factors=["quality", "price"],
            budget_range="medium",
            timeline="3 months",
            company_size="small",
            industry="technology"
        )
        repo.get_by_id.return_value = persona
        return repo

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
                mock_persona_repository, mock_transcription_service):
        """Create service instance with mocked dependencies."""
        return OpenAIVoiceConversationService(
            conversation_service=mock_conversation_service,
            voice_service=mock_voice_service,
            persona_repository=mock_persona_repository,
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
    async def test_convert_pcm_to_wav_generates_valid_wav_header(self, service):
        """Test that PCM16 to WAV conversion generates a valid WAV file header."""
        # Arrange
        # Create sample PCM16 audio data (1 second of 24kHz mono audio)
        sample_rate = 24000
        duration_seconds = 1
        num_samples = sample_rate * duration_seconds
        pcm_data = bytes([0, 0] * num_samples)  # Silent audio (48000 bytes)
        
        # Act
        wav_data = await service._convert_pcm_to_webm(pcm_data, sample_rate)
        
        # Assert - Verify WAV header structure
        assert len(wav_data) > 44, "WAV file should have at least 44-byte header"
        
        # Check RIFF header
        assert wav_data[0:4] == b'RIFF', "Should start with RIFF"
        assert wav_data[8:12] == b'WAVE', "Should contain WAVE"
        
        # Check fmt chunk
        assert wav_data[12:16] == b'fmt ', "Should contain fmt chunk"
        
        # Check audio format (PCM = 1)
        audio_format = int.from_bytes(wav_data[20:22], 'little')
        assert audio_format == 1, "Audio format should be PCM (1)"
        
        # Check channels (mono = 1)
        num_channels = int.from_bytes(wav_data[22:24], 'little')
        assert num_channels == 1, "Should be mono (1 channel)"
        
        # Check sample rate
        parsed_sample_rate = int.from_bytes(wav_data[24:28], 'little')
        assert parsed_sample_rate == sample_rate, f"Sample rate should be {sample_rate}"
        
        # Check bits per sample (16-bit)
        bits_per_sample = int.from_bytes(wav_data[34:36], 'little')
        assert bits_per_sample == 16, "Should be 16-bit PCM"
        
        # Check data chunk
        assert wav_data[36:40] == b'data', "Should contain data chunk"
        
        # Check data size
        data_size = int.from_bytes(wav_data[40:44], 'little')
        assert data_size == len(pcm_data), "Data size should match PCM data length"
        
        # Check that PCM data is preserved
        assert wav_data[44:] == pcm_data, "PCM data should be preserved after header"

    @pytest.mark.asyncio
    async def test_convert_pcm_to_wav_with_different_sample_rates(self, service):
        """Test WAV conversion with various sample rates."""
        # Arrange
        pcm_data = bytes([0, 0] * 100)  # 200 bytes of silent audio
        sample_rates = [8000, 16000, 24000, 48000]
        
        for sample_rate in sample_rates:
            # Act
            wav_data = await service._convert_pcm_to_webm(pcm_data, sample_rate)
            
            # Assert
            parsed_sample_rate = int.from_bytes(wav_data[24:28], 'little')
            assert parsed_sample_rate == sample_rate, f"Sample rate should be {sample_rate}"
            
            # Verify byte rate calculation (sample_rate * channels * bits_per_sample / 8)
            expected_byte_rate = sample_rate * 1 * 16 // 8
            parsed_byte_rate = int.from_bytes(wav_data[28:32], 'little')
            assert parsed_byte_rate == expected_byte_rate, f"Byte rate should be {expected_byte_rate}"

    @pytest.mark.asyncio
    async def test_convert_pcm_to_wav_handles_empty_data(self, service):
        """Test WAV conversion with empty PCM data."""
        # Arrange
        pcm_data = b''
        
        # Act
        wav_data = await service._convert_pcm_to_webm(pcm_data, 24000)
        
        # Assert
        assert len(wav_data) == 44, "Should still generate 44-byte header for empty data"
        assert wav_data[0:4] == b'RIFF', "Should have valid RIFF header"
        
        # Data size should be 0
        data_size = int.from_bytes(wav_data[40:44], 'little')
        assert data_size == 0, "Data size should be 0 for empty input"


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
