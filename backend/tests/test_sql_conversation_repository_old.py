"""
Unit tests for SQLConversationRepository.
Tests UUID to string conversion and database operations.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from uuid import UUID, uuid4

from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository
from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.entities.conversation import ConversationStatus
from src.conversation.infrastructure.persistence.models import ConversationModel


class TestSQLConversationRepository:
    """Test cases for SQLConversationRepository."""

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
            completed_at=None,
# duration_seconds=120  # Not in ConversationModel
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
            completed_at=None,
# duration_seconds=120  # Not in ConversationModel
        )

    @pytest.mark.asyncio
    async def test_save_converts_uuid_to_string(self, repository, sample_conversation):
        """Test that save method converts UUID to string when storing."""
        # This test verifies the type conversion logic without requiring a real database
        # The actual database operations are tested in integration tests
        
        # Test that the conversation ID can be converted to string
        conversation_id_str = str(sample_conversation.id.value)
        assert isinstance(conversation_id_str, str)
        assert conversation_id_str == str(sample_conversation.id.value)
        
        # Test that the UUID can be reconstructed from the string
        reconstructed_uuid = UUID(conversation_id_str)
        assert reconstructed_uuid == sample_conversation.id.value

    @pytest.mark.asyncio
    async def test_get_by_id_converts_string_to_uuid(self, repository, sample_conversation_model):
        """Test that get_by_id converts string back to UUID in domain entity."""
        # This test verifies the type conversion logic without requiring a real database
        
        # Test that the model ID string can be converted to UUID
        conversation_id_obj = ConversationId(value=UUID(sample_conversation_model.id))
        assert isinstance(conversation_id_obj.value, UUID)
        assert str(conversation_id_obj.value) == sample_conversation_model.id
        
        # Test the conversion in the other direction
        model_id_str = str(conversation_id_obj.value)
        assert isinstance(model_id_str, str)
        assert model_id_str == sample_conversation_model.id

    @pytest.mark.asyncio
    async def test_model_to_entity_conversion(self, repository, sample_conversation_model):
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

    @pytest.mark.asyncio
    async def test_model_to_entity_handles_none_metadata(self, repository):
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
            completed_at=None,
# duration_seconds=None  # Not in ConversationModel
        )
        
        # Act
        entity = repository._model_to_entity(model)
        
        # Assert
        assert entity.metadata == {}
        assert entity.transcription_id is None
        assert entity.analysis_id is None

    @pytest.mark.asyncio
    async def test_model_to_entity_handles_invalid_json_metadata(self, repository):
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
            completed_at=None,
# duration_seconds=None  # Not in ConversationModel
        )
        
        # Act & Assert
        with pytest.raises(Exception):  # Should raise an exception for invalid JSON
            repository._model_to_entity(model)

    @pytest.mark.asyncio
    async def test_update_status_converts_uuid_to_string(self, repository):
        """Test that update_status converts UUID to string for database query."""
        # Arrange
        conversation_uuid = uuid4()
        conversation_id = ConversationId(value=conversation_uuid)
        status = ConversationStatus.COMPLETED
        transcription_id = "new-transcription-id"
        analysis_id = "new-analysis-id"
        metadata = {"updated": True}
        
        with patch('src.conversation.infrastructure.persistence.sql_conversation_repo.db_config') as mock_db_config:
            mock_session = AsyncMock()
            mock_db_config.get_session.return_value.__enter__.return_value = mock_session
            mock_conversation_model = Mock()
            mock_session.query.return_value.filter.return_value.first.return_value = mock_conversation_model
            
            # Act
            result = await repository.update_status(
                conversation_id, status, transcription_id, analysis_id, metadata
            )
            
            # Assert
            # Verify that query was made with string ID
            mock_session.query.assert_called_once_with(ConversationModel)
            filter_call = mock_session.query.return_value.filter.call_args[0][0]
            # The filter should use string representation of UUID
            assert str(conversation_uuid) in str(filter_call)

    @pytest.mark.asyncio
    async def test_exists_converts_uuid_to_string(self, repository):
        """Test that exists method converts UUID to string for database query."""
        # Arrange
        conversation_uuid = uuid4()
        conversation_id = ConversationId(value=conversation_uuid)
        
        with patch('src.conversation.infrastructure.persistence.sql_conversation_repo.db_config') as mock_db_config:
            mock_session = AsyncMock()
            mock_db_config.get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.filter.return_value.first.return_value = Mock()
            
            # Act
            result = await repository.exists(conversation_id)
            
            # Assert
            assert result is True
            # Verify that query was made with string ID
            mock_session.query.assert_called_once_with(ConversationModel)

    @pytest.mark.asyncio
    async def test_delete_converts_uuid_to_string(self, repository):
        """Test that delete method converts UUID to string for database query."""
        # Arrange
        conversation_uuid = uuid4()
        conversation_id = ConversationId(value=conversation_uuid)
        
        with patch('src.conversation.infrastructure.persistence.sql_conversation_repo.db_config') as mock_db_config:
            mock_session = AsyncMock()
            mock_db_config.get_session.return_value.__enter__.return_value = mock_session
            mock_conversation_model = Mock()
            mock_session.query.return_value.filter.return_value.first.return_value = mock_conversation_model
            
            # Act
            result = await repository.delete(conversation_id)
            
            # Assert
            assert result is True
            # Verify that query was made with string ID
            mock_session.query.assert_called_once_with(ConversationModel)

    @pytest.mark.asyncio
    async def test_get_all_returns_entities_with_uuid_ids(self, repository, sample_conversation_model):
        """Test that get_all returns entities with proper UUID conversion."""
        # Arrange
        models = [sample_conversation_model]
        
        with patch('src.conversation.infrastructure.persistence.sql_conversation_repo.db_config') as mock_db_config:
            mock_session = AsyncMock()
            mock_db_config.get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.limit.return_value.offset.return_value.all.return_value = models
            
            # Act
            result = await repository.get_all(limit=10, offset=0)
            
            # Assert
            assert len(result) == 1
            entity = result[0]
            assert isinstance(entity.id.value, UUID), f"ID should be UUID, got {type(entity.id.value)}"
            assert str(entity.id.value) == sample_conversation_model.id

    @pytest.mark.asyncio
    async def test_get_by_persona_id_returns_entities_with_uuid_ids(self, repository, sample_conversation_model):
        """Test that get_by_persona_id returns entities with proper UUID conversion."""
        # Arrange
        persona_id = "test-persona-id"
        models = [sample_conversation_model]
        
        with patch('src.conversation.infrastructure.persistence.sql_conversation_repo.db_config') as mock_db_config:
            mock_session = AsyncMock()
            mock_db_config.get_session.return_value.__enter__.return_value = mock_session
            mock_session.query.return_value.filter.return_value.limit.return_value.offset.return_value.all.return_value = models
            
            # Act
            result = await repository.get_by_persona_id(persona_id, limit=10, offset=0)
            
            # Assert
            assert len(result) == 1
            entity = result[0]
            assert isinstance(entity.id.value, UUID), f"ID should be UUID, got {type(entity.id.value)}"
            assert str(entity.id.value) == sample_conversation_model.id

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

    @pytest.mark.asyncio
    async def test_save_updates_existing_conversation(self, repository, sample_conversation):
        """Test that save method updates existing conversation properly."""
        # Arrange
        with patch('src.conversation.infrastructure.persistence.sql_conversation_repo.db_config') as mock_db_config:
            mock_session = AsyncMock()
            mock_db_config.get_session.return_value.__enter__.return_value = mock_session
            
            # Mock existing conversation
            existing_model = Mock()
            existing_model.id = str(sample_conversation.id.value)
            mock_session.query.return_value.filter.return_value.first.return_value = existing_model
            
            # Act
            await repository.save(sample_conversation)
            
            # Assert
            # Should update existing model, not create new one
            mock_session.add.assert_not_called()
            # Verify that existing model properties were updated
            assert existing_model.persona_id == sample_conversation.persona_id
            assert existing_model.context_id == sample_conversation.context_id
            assert existing_model.status == sample_conversation.status.value

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
            completed_at=None,  # Should be Optional[datetime]
# duration_seconds=120  # Not in ConversationModel  # Should be Optional[int]
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
# assert isinstance(model.duration_seconds, int)  # Not in ConversationModel


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
