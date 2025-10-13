"""
Unit tests for TranscriptionFileService.
Tests file operations and message ordering.
"""
import pytest
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

from src.conversation.infrastructure.services.transcription_file_service import TranscriptionFileService


class TestTranscriptionFileService:
    """Test cases for TranscriptionFileService."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def service(self, temp_dir):
        """Create service instance with temporary directory."""
        return TranscriptionFileService(conversations_dir=temp_dir)

    @pytest.fixture
    def sample_messages(self):
        """Create sample messages for testing."""
        return [
            {
                "id": "msg1",
                "conversation_id": "test-conversation-id",
                "role": "user",
                "content": "Hello",
                "timestamp": "2025-01-01T10:00:00",
                "metadata": {}
            },
            {
                "id": "msg2",
                "conversation_id": "test-conversation-id",
                "role": "assistant",
                "content": "Hi there!",
                "timestamp": "2025-01-01T10:00:05",
                "metadata": {}
            }
        ]

    @pytest.mark.asyncio
    async def test_save_transcription_creates_file(self, service, sample_messages):
        """Test that save_transcription creates a file with correct content."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        persona_id = "test-persona-id"
        context_id = "default"
        metadata = {"test": "data"}
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=sample_messages,
            persona_id=persona_id,
            context_id=context_id,
            metadata=metadata
        )
        
        # Assert
        assert file_path.endswith(f"{transcription_id}.json")
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["transcription_id"] == transcription_id
        assert data["conversation_id"] == conversation_id
        assert data["persona_id"] == persona_id
        assert data["context_id"] == context_id
        assert data["messages"] == sample_messages
        assert data["metadata"] == metadata
        assert data["message_count"] == len(sample_messages)

    @pytest.mark.asyncio
    async def test_get_transcription_loads_file(self, service, sample_messages):
        """Test that get_transcription loads file content correctly."""
        # Arrange
        transcription_id = "test-transcription-id"
        conversation_id = "test-conversation-id"
        
        # Create a test file
        test_data = {
            "transcription_id": transcription_id,
            "conversation_id": conversation_id,
            "persona_id": "test-persona-id",
            "context_id": "default",
            "messages": sample_messages,
            "metadata": {"test": "data"},
            "message_count": len(sample_messages)
        }
        
        file_path = Path(service.conversations_dir) / f"{transcription_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Act
        result = await service.get_transcription(transcription_id)
        
        # Assert
        assert result is not None
        assert result["transcription_id"] == transcription_id
        assert result["conversation_id"] == conversation_id
        assert result["messages"] == sample_messages
        assert result["message_count"] == len(sample_messages)

    @pytest.mark.asyncio
    async def test_get_transcription_returns_none_for_missing_file(self, service):
        """Test that get_transcription returns None for non-existent file."""
        # Arrange
        transcription_id = "non-existent-transcription-id"
        
        # Act
        result = await service.get_transcription(transcription_id)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_transcription_handles_invalid_json(self, service):
        """Test that get_transcription handles invalid JSON gracefully."""
        # Arrange
        transcription_id = "invalid-json-transcription-id"
        
        # Create a file with invalid JSON
        file_path = Path(service.conversations_dir) / f"{transcription_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json content")
        
        # Act
        result = await service.get_transcription(transcription_id)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_save_transcription_handles_empty_messages(self, service):
        """Test that save_transcription handles empty messages list."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        persona_id = "test-persona-id"
        context_id = "default"
        messages = []
        metadata = {}
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=messages,
            persona_id=persona_id,
            context_id=context_id,
            metadata=metadata
        )
        
        # Assert
        assert os.path.exists(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["messages"] == []
        assert data["message_count"] == 0
        # created_at and completed_at are set to current time, not None
        assert data["created_at"] is not None
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_save_transcription_sets_timestamps_to_current_time(self, service, sample_messages):
        """Test that save_transcription sets created_at and completed_at to current time."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        persona_id = "test-persona-id"
        context_id = "default"
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=sample_messages,
            persona_id=persona_id,
            context_id=context_id,
            metadata={}
        )
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # created_at and completed_at should be set to current time (not message timestamps)
        assert data["created_at"] is not None
        assert data["completed_at"] is not None
        # They should be ISO format timestamps
        assert "T" in data["created_at"]
        assert "T" in data["completed_at"]

    @pytest.mark.asyncio
    async def test_save_transcription_handles_unicode_content(self, service):
        """Test that save_transcription handles Unicode content correctly."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        persona_id = "test-persona-id"
        context_id = "default"
        messages = [
            {
                "id": "msg1",
                "conversation_id": conversation_id,
                "role": "user",
                "content": "¡Hola! ¿Cómo estás? 🌟",
                "timestamp": "2025-01-01T10:00:00",
                "metadata": {}
            },
            {
                "id": "msg2",
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": "¡Muy bien, gracias! 😊",
                "timestamp": "2025-01-01T10:00:05",
                "metadata": {}
            }
        ]
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=messages,
            persona_id=persona_id,
            context_id=context_id,
            metadata={}
        )
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["messages"][0]["content"] == "¡Hola! ¿Cómo estás? 🌟"
        assert data["messages"][1]["content"] == "¡Muy bien, gracias! 😊"

    @pytest.mark.asyncio
    async def test_save_transcription_creates_directory_if_not_exists(self, temp_dir):
        """Test that save_transcription creates directory if it doesn't exist."""
        # Arrange
        non_existent_dir = Path(temp_dir) / "non_existent_subdir"
        service = TranscriptionFileService(conversations_dir=str(non_existent_dir))
        
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        messages = [
            {
                "id": "msg1",
                "conversation_id": conversation_id,
                "role": "user",
                "content": "Test",
                "timestamp": "2025-01-01T10:00:00",
                "metadata": {}
            }
        ]
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=messages,
            persona_id="test-persona-id",
            context_id="default",
            metadata={}
        )
        
        # Assert
        assert os.path.exists(file_path)
        assert non_existent_dir.exists()

    @pytest.mark.asyncio
    async def test_save_transcription_handles_large_message_list(self, service):
        """Test that save_transcription handles large message lists."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        
        # Create a large list of messages
        messages = []
        for i in range(100):
            messages.append({
                "id": f"msg{i}",
                "conversation_id": conversation_id,
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i} with some content to make it substantial",
                "timestamp": f"2025-01-01T10:{i//60:02d}:{i%60:02d}",
                "metadata": {"message_number": i}
            })
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=messages,
            persona_id="test-persona-id",
            context_id="default",
            metadata={}
        )
        
        # Assert
        assert os.path.exists(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data["messages"]) == 100
        assert data["message_count"] == 100

    @pytest.mark.asyncio
    async def test_save_transcription_handles_none_metadata(self, service, sample_messages):
        """Test that save_transcription handles None metadata."""
        # Arrange
        conversation_id = "test-conversation-id"
        transcription_id = "test-transcription-id"
        
        # Act
        file_path = await service.save_transcription(
            conversation_id=conversation_id,
            transcription_id=transcription_id,
            messages=sample_messages,
            persona_id="test-persona-id",
            context_id="default",
            metadata=None
        )
        
        # Assert
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["metadata"] == {}

    def test_service_initialization(self, temp_dir):
        """Test that service initializes correctly."""
        # Act
        service = TranscriptionFileService(conversations_dir=temp_dir)
        
        # Assert
        assert service.conversations_dir == Path(temp_dir)
        assert service.conversations_dir.exists()

    def test_service_initialization_with_default_dir(self):
        """Test that service initializes with default directory."""
        # Act
        service = TranscriptionFileService()
        
        # Assert
        assert service.conversations_dir == Path("data/conversations")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
