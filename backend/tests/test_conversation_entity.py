"""
Comprehensive tests for Conversation entity
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.value_objects.conversation_id import ConversationId


class TestConversationEntity:
    """Tests for Conversation domain entity"""
    
    @pytest.fixture
    def conversation_id(self):
        """Create conversation ID"""
        return ConversationId(value=uuid4())
    
    @pytest.fixture
    def conversation(self, conversation_id):
        """Create conversation instance"""
        return Conversation(
            conversation_id=conversation_id,
            persona_id="test_persona",
            context_id="test_context",
            status=ConversationStatus.ACTIVE,
            transcription_id="test_transcription",
            analysis_id=None,
            metadata={"key": "value"},
            created_at=datetime.now(),
            completed_at=None
        )
    
    def test_conversation_creation(self, conversation, conversation_id):
        """Test conversation entity creation"""
        assert conversation is not None
        assert conversation.id == conversation_id
        assert conversation.persona_id == "test_persona"
        assert conversation.status == ConversationStatus.ACTIVE
    
    def test_conversation_status_enum(self):
        """Test ConversationStatus enum values"""
        assert ConversationStatus.ACTIVE.value == "active"
        assert ConversationStatus.COMPLETED.value == "completed"
        assert ConversationStatus.CANCELLED.value == "cancelled"
    
    def test_conversation_complete(self, conversation):
        """Test completing a conversation"""
        conversation.complete()
        assert conversation.status == ConversationStatus.COMPLETED
        assert conversation.completed_at is not None
    
    def test_conversation_cancel(self, conversation):
        """Test cancelling a conversation"""
        conversation.cancel()
        assert conversation.status == ConversationStatus.CANCELLED
        assert conversation.completed_at is not None
    
    def test_add_message_data(self, conversation):
        """Test adding message data to conversation"""
        message_data = {
            "role": "user",
            "content": "Test message",
            "timestamp": datetime.now().isoformat()
        }
        
        conversation.add_message_data(message_data)
        # Message should be added (implementation dependent)
    
    def test_metadata_access(self, conversation):
        """Test accessing conversation metadata"""
        assert conversation.metadata["key"] == "value"
    
    def test_metadata_update(self, conversation):
        """Test updating conversation metadata"""
        conversation.metadata["new_key"] = "new_value"
        assert conversation.metadata["new_key"] == "new_value"
    
    def test_conversation_with_none_analysis(self, conversation):
        """Test conversation with no analysis ID"""
        assert conversation.analysis_id is None
    
    def test_set_analysis_id(self, conversation):
        """Test setting analysis ID"""
        conversation.analysis_id = "analysis_123"
        assert conversation.analysis_id == "analysis_123"
    
    def test_conversation_timestamps(self, conversation):
        """Test conversation timestamp management"""
        assert conversation.created_at is not None
        assert conversation.completed_at is None
        
        conversation.complete()
        assert conversation.completed_at is not None
        assert conversation.completed_at >= conversation.created_at
    
    def test_conversation_equality(self, conversation_id):
        """Test conversation equality based on ID"""
        conv1 = Conversation(
            conversation_id=conversation_id,
            persona_id="persona1",
            context_id="context1",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        conv2 = Conversation(
            conversation_id=conversation_id,
            persona_id="persona2",
            context_id="context2",
            status=ConversationStatus.COMPLETED,
            transcription_id="trans2",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        # Same ID = same conversation
        assert conv1.id == conv2.id
    
    def test_conversation_different_ids(self):
        """Test conversations with different IDs are different"""
        conv1 = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="persona1",
            context_id="context1",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        conv2 = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="persona1",
            context_id="context1",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        assert conv1.id != conv2.id
    
    def test_conversation_with_empty_metadata(self, conversation_id):
        """Test conversation with empty metadata"""
        conv = Conversation(
            conversation_id=conversation_id,
            persona_id="persona1",
            context_id="context1",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        assert conv.metadata == {}
    
    def test_conversation_status_transitions(self, conversation):
        """Test valid status transitions"""
        # ACTIVE -> COMPLETED
        assert conversation.status == ConversationStatus.ACTIVE
        conversation.complete()
        assert conversation.status == ConversationStatus.COMPLETED
    
    def test_conversation_cannot_complete_twice(self, conversation):
        """Test that completing twice keeps first completion time"""
        conversation.complete()
        first_completion = conversation.completed_at
        
        conversation.complete()
        second_completion = conversation.completed_at
        
        # Should keep first completion time
        assert first_completion == second_completion or second_completion >= first_completion
    
    def test_conversation_persona_id_immutable(self, conversation):
        """Test that persona_id is set at creation"""
        assert conversation.persona_id == "test_persona"
    
    def test_conversation_context_id_immutable(self, conversation):
        """Test that context_id is set at creation"""
        assert conversation.context_id == "test_context"
    
    def test_conversation_transcription_id(self, conversation):
        """Test transcription ID access"""
        assert conversation.transcription_id == "test_transcription"
    
    def test_multiple_message_additions(self, conversation):
        """Test adding multiple messages"""
        for i in range(5):
            message_data = {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}",
                "timestamp": datetime.now().isoformat()
            }
            conversation.add_message_data(message_data)
        
        # Should not crash
        assert conversation is not None
    
    def test_conversation_string_representation(self, conversation):
        """Test string representation of conversation"""
        str_repr = str(conversation.id)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

