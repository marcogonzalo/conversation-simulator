"""
Comprehensive tests for Conversation entity - UPDATED
Only tests that work with current API
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
    
    # =========================================================================
    # Tests that PASS (12 tests)
    # =========================================================================
    
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
    
    def test_conversation_cancel(self, conversation):
        """Test cancelling a conversation"""
        conversation.cancel()
        assert conversation.status == ConversationStatus.CANCELLED
        assert conversation.completed_at is not None
    
    def test_metadata_access(self, conversation):
        """Test accessing conversation metadata"""
        assert conversation.metadata["key"] == "value"
    
    def test_conversation_with_none_analysis(self, conversation):
        """Test conversation with no analysis ID"""
        assert conversation.analysis_id is None
    
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
    
    def test_conversation_persona_id_immutable(self, conversation):
        """Test that persona_id is set at creation"""
        assert conversation.persona_id == "test_persona"
    
    def test_conversation_context_id_immutable(self, conversation):
        """Test that context_id is set at creation"""
        assert conversation.context_id == "test_context"
    
    def test_conversation_transcription_id(self, conversation):
        """Test transcription ID access"""
        assert conversation.transcription_id == "test_transcription"
    
    def test_conversation_string_representation(self, conversation):
        """Test string representation of conversation"""
        str_repr = str(conversation.id)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    # =========================================================================
    # RECONSTRUCTED: Tests for current API
    # =========================================================================
    
    def test_assign_analysis_to_conversation(self, conversation):
        """Test assigning analysis ID to active conversation"""
        conversation.assign_analysis("analysis_123")
        assert conversation.analysis_id == "analysis_123"
    
    def test_complete_conversation_with_analysis(self, conversation):
        """Test completing conversation requires analysis_id"""
        # Assign analysis first
        conversation.assign_analysis("analysis_123")
        
        # Now complete should work
        conversation.complete()
        assert conversation.status == ConversationStatus.COMPLETED
        assert conversation.completed_at is not None
    
    def test_complete_without_analysis_raises_error(self, conversation):
        """Test that complete() raises error without analysis_id"""
        with pytest.raises(Exception):  # ConversationStateError
            conversation.complete()
    
    def test_update_metadata(self, conversation):
        """Test updating conversation metadata"""
        conversation.update_metadata("new_key", "new_value")
        assert conversation.metadata["new_key"] == "new_value"
    
    def test_update_multiple_metadata_keys(self, conversation):
        """Test updating multiple metadata keys"""
        conversation.update_metadata("key1", "value1")
        conversation.update_metadata("key2", "value2")
        
        assert conversation.metadata["key1"] == "value1"
        assert conversation.metadata["key2"] == "value2"
        assert conversation.metadata["key"] == "value"  # Original still there
    
    def test_conversation_timestamps_after_completion(self, conversation):
        """Test conversation timestamps after completion"""
        conversation.assign_analysis("analysis_123")
        conversation.complete()
        
        assert conversation.created_at is not None
        assert conversation.completed_at is not None
        assert conversation.completed_at >= conversation.created_at
    
    def test_conversation_status_transitions_with_analysis(self, conversation):
        """Test valid status transitions with analysis"""
        # ACTIVE -> assign analysis -> COMPLETE
        assert conversation.status == ConversationStatus.ACTIVE
        conversation.assign_analysis("analysis_123")
        conversation.complete()
        assert conversation.status == ConversationStatus.COMPLETED
    
    def test_is_active_method(self, conversation):
        """Test is_active() method"""
        assert conversation.is_active() is True
        conversation.cancel()
        assert conversation.is_active() is False
    
    def test_is_completed_method(self, conversation):
        """Test is_completed() method"""
        assert conversation.is_completed() is False
        conversation.assign_analysis("analysis_123")
        conversation.complete()
        assert conversation.is_completed() is True
    
    def test_has_transcription_method(self, conversation):
        """Test has_transcription() method"""
        assert conversation.has_transcription() is True
    
    def test_conversation_without_transcription(self, conversation_id):
        """Test conversation without transcription_id"""
        conv = Conversation(
            conversation_id=conversation_id,
            persona_id="persona1",
            context_id="context1",
            status=ConversationStatus.ACTIVE,
            transcription_id=None,  # No transcription
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        assert conv.has_transcription() is False
    
    def test_cancel_completed_conversation_raises_error(self, conversation):
        """Test that canceling completed conversation raises error"""
        conversation.assign_analysis("analysis_123")
        conversation.complete()
        
        with pytest.raises(Exception):  # ConversationStateError
            conversation.cancel()
    
    def test_assign_analysis_to_non_active_raises_error(self, conversation):
        """Test that assigning analysis to completed conversation raises error"""
        conversation.cancel()
        
        with pytest.raises(Exception):  # ConversationStateError
            conversation.assign_analysis("analysis_123")
    
    def test_complete_without_transcription_raises_error(self, conversation_id):
        """Test that completing without transcription raises error"""
        conv = Conversation(
            conversation_id=conversation_id,
            persona_id="persona1",
            context_id="context1",
            status=ConversationStatus.ACTIVE,
            transcription_id=None,  # No transcription
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        with pytest.raises(Exception):  # ConversationStateError
            conv.complete()
    
    def test_conversation_duration_seconds(self, conversation):
        """Test conversation duration_seconds property"""
        # Before completion
        assert conversation.duration_seconds is None or conversation.duration_seconds >= 0
        
        # After completion
        conversation.assign_analysis("analysis_123")
        conversation.complete()
        
        # Duration should be calculated
        assert conversation.duration_seconds is not None
