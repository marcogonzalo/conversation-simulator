"""
Simplified unit tests for SQLConversationRepository.
Tests type conversions and model mappings without database dependencies.
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4

from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository
from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.entities.conversation import ConversationStatus
from src.conversation.infrastructure.persistence.models import ConversationModel


class TestSQLConversationRepositorySimple:
    """Test cases for SQLConversationRepository type conversions."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return SQLConversationRepository()

    @pytest.fixture
    def sample_conversation(self):
        """Create a sample conversation entity."""
        conversation_uuid = uuid4()
        return Conversation(
            conversation_id=ConversationId(value=conversation_uuid),
            persona_id="test-persona-id",
            context_id="default",
            status=ConversationStatus.ACTIVE,
            transcription_id="test-transcription-id",
            analysis_id="test-analysis-id",
            metadata={"test": "data"},
            created_at=datetime.now(),
            completed_at=None
        )

    @pytest.fixture
    def sample_conversation_model(self):
        """Create a sample conversation model."""
        conversation_uuid = uuid4()
        return ConversationModel(
            id=str(conversation_uuid),
            persona_id="test-persona-id",
            context_id="default",
            status="active",
            transcription_id="test-transcription-id",
            analysis_id="test-analysis-id",
            conversation_metadata='{"test": "data"}',
            created_at=datetime.now(),
            completed_at=None
        )

    def test_uuid_to_string_conversion(self, sample_conversation):
        """Test that UUID is properly converted to string."""
        # Test that the conversation ID can be converted to string
        conversation_id_str = str(sample_conversation.id.value)
        assert isinstance(conversation_id_str, str)
        assert conversation_id_str == str(sample_conversation.id.value)
        
        # Test that the UUID can be reconstructed from the string
        reconstructed_uuid = UUID(conversation_id_str)
        assert reconstructed_uuid == sample_conversation.id.value

    def test_string_to_uuid_conversion(self, sample_conversation_model):
        """Test that string is properly converted to UUID."""
        # Test that the model ID string can be converted to UUID
        conversation_id_obj = ConversationId(value=UUID(sample_conversation_model.id))
        assert isinstance(conversation_id_obj.value, UUID)
        assert str(conversation_id_obj.value) == sample_conversation_model.id
        
        # Test the conversion in the other direction
        model_id_str = str(conversation_id_obj.value)
        assert isinstance(model_id_str, str)
        assert model_id_str == sample_conversation_model.id

    def test_model_to_entity_conversion(self, repository, sample_conversation_model):
        """Test that _model_to_entity properly converts model to domain entity."""
        # Act
        entity = repository._model_to_entity(sample_conversation_model)
        
        # Assert
        assert isinstance(entity, Conversation)
        assert isinstance(entity.id.value, UUID), f"ID should be UUID, got {type(entity.id.value)}"
        assert str(entity.id.value) == sample_conversation_model.id
        assert entity.persona_id == sample_conversation_model.persona_id
        assert entity.context_id == sample_conversation_model.context_id
        assert entity.status == ConversationStatus(sample_conversation_model.status)
        assert entity.transcription_id == sample_conversation_model.transcription_id
        assert entity.analysis_id == sample_conversation_model.analysis_id
        assert entity.metadata == {"test": "data"}

    def test_model_to_entity_handles_none_metadata(self, repository):
        """Test that _model_to_entity handles None metadata correctly."""
        # Arrange
        model = ConversationModel(
            id=str(uuid4()),
            persona_id="test-persona-id",
            context_id="default",
            status="active",
            transcription_id=None,
            analysis_id=None,
            conversation_metadata=None,
            created_at=datetime.now(),
            completed_at=None
        )
        
        # Act
        entity = repository._model_to_entity(model)
        
        # Assert
        assert entity.metadata == {}
        assert entity.transcription_id is None
        assert entity.analysis_id is None

    def test_model_to_entity_handles_invalid_json_metadata(self, repository):
        """Test that _model_to_entity handles invalid JSON metadata gracefully."""
        # Arrange
        model = ConversationModel(
            id=str(uuid4()),
            persona_id="test-persona-id",
            context_id="default",
            status="active",
            transcription_id=None,
            analysis_id=None,
            conversation_metadata='{"invalid": json}',  # Invalid JSON
            created_at=datetime.now(),
            completed_at=None
        )
        
        # Act & Assert
        with pytest.raises(Exception):  # Should raise an exception for invalid JSON
            repository._model_to_entity(model)

    def test_conversation_model_field_types(self):
        """Test that ConversationModel fields have correct types."""
        # Arrange
        conversation_uuid = uuid4()
        
        # Act
        model = ConversationModel(
            id=str(conversation_uuid),  # Should be string
            persona_id="test-persona-id",  # Should be string
            context_id="default",  # Should be string
            status="active",  # Should be string
            transcription_id="transcription-123",  # Should be Optional[str]
            analysis_id="analysis-123",  # Should be Optional[str]
            conversation_metadata='{"test": "data"}',  # Should be Optional[str] (JSON)
            created_at=datetime.now(),  # Should be Optional[datetime]
            completed_at=None  # Should be Optional[datetime]
        )
        
        # Assert
        assert isinstance(model.id, str)
        assert isinstance(model.persona_id, str)
        assert isinstance(model.context_id, str)
        assert isinstance(model.status, str)
        assert isinstance(model.transcription_id, str)
        assert isinstance(model.analysis_id, str)
        assert isinstance(model.conversation_metadata, str)
        assert isinstance(model.created_at, datetime)
        assert model.completed_at is None or isinstance(model.completed_at, datetime)

    def test_uuid_string_roundtrip_conversion(self, repository):
        """Test that UUID to string to UUID conversion is consistent."""
        # Arrange
        original_uuid = uuid4()
        
        # Act - Convert to string and back
        uuid_string = str(original_uuid)
        converted_uuid = UUID(uuid_string)
        
        # Assert
        assert original_uuid == converted_uuid
        assert isinstance(uuid_string, str)
        assert isinstance(converted_uuid, UUID)

    def test_conversation_status_enum_conversion(self):
        """Test that ConversationStatus enum values are properly converted."""
        # Test string to enum conversion
        status_str = "active"
        status_enum = ConversationStatus(status_str)
        assert status_enum == ConversationStatus.ACTIVE
        
        # Test enum to string conversion
        enum_value = ConversationStatus.ACTIVE
        string_value = enum_value.value
        assert string_value == "active"

    def test_metadata_json_serialization(self):
        """Test that metadata is properly serialized/deserialized as JSON."""
        import json
        
        # Test serialization
        metadata = {"test": "data", "number": 123, "boolean": True}
        json_str = json.dumps(metadata)
        assert isinstance(json_str, str)
        
        # Test deserialization
        deserialized_metadata = json.loads(json_str)
        assert deserialized_metadata == metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


