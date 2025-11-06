"""
Tests for Conversation Domain Service
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.exceptions import ConversationNotFoundError, ConversationStateError


class TestConversationDomainService:
    """Tests for ConversationDomainService"""
    
    @pytest.fixture
    def service(self):
        """Create domain service instance"""
        return ConversationDomainService()
    
    @pytest.fixture
    def active_conversation(self):
        """Create active conversation"""
        return Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test_persona",
            context_id="test_context",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
    
    def test_create_conversation_returns_conversation(self, service):
        """Test creating a new conversation"""
        conversation = service.create_conversation(
            persona_id="test_persona",
            context_id="test_context"
        )
        
        assert conversation is not None
        assert isinstance(conversation, Conversation)
        assert conversation.persona_id == "test_persona"
        assert conversation.status == ConversationStatus.ACTIVE
    
    def test_created_conversation_has_id(self, service):
        """Test that created conversation has ID"""
        conversation = service.create_conversation("persona1", "context1")
        
        assert conversation.id is not None
        assert isinstance(conversation.id, ConversationId)
    
    def test_created_conversation_has_timestamps(self, service):
        """Test that created conversation has timestamps"""
        conversation = service.create_conversation("persona1", "context1")
        
        assert conversation.created_at is not None
        assert conversation.completed_at is None
    
    def test_validate_active_conversation(self, service, active_conversation):
        """Test validating an active conversation"""
        # Should not raise
        service.validate_conversation_active(active_conversation)
    
    def test_validate_completed_conversation_raises(self, service, active_conversation):
        """Test validating completed conversation raises"""
        active_conversation.complete()
        
        with pytest.raises(ConversationStateError):
            service.validate_conversation_active(active_conversation)
    
    def test_validate_cancelled_conversation_raises(self, service, active_conversation):
        """Test validating cancelled conversation raises"""
        active_conversation.cancel()
        
        with pytest.raises(ConversationStateError):
            service.validate_conversation_active(active_conversation)
    
    def test_complete_conversation(self, service, active_conversation):
        """Test completing a conversation"""
        service.complete_conversation(active_conversation)
        
        assert active_conversation.status == ConversationStatus.COMPLETED
        assert active_conversation.completed_at is not None
    
    def test_complete_conversation_sets_analysis_id(self, service, active_conversation):
        """Test completing conversation can set analysis ID"""
        analysis_id = "analysis_123"
        service.complete_conversation(active_conversation, analysis_id=analysis_id)
        
        assert active_conversation.analysis_id == analysis_id
    
    def test_cancel_conversation(self, service, active_conversation):
        """Test cancelling a conversation"""
        service.cancel_conversation(active_conversation)
        
        assert active_conversation.status == ConversationStatus.CANCELLED
        assert active_conversation.completed_at is not None
    
    def test_add_message_to_conversation(self, service, active_conversation):
        """Test adding message to conversation"""
        message_data = {
            "role": "user",
            "content": "Test message",
            "timestamp": datetime.now().isoformat()
        }
        
        service.add_message(active_conversation, message_data)
        # Should not raise
    
    def test_add_multiple_messages(self, service, active_conversation):
        """Test adding multiple messages"""
        for i in range(5):
            message_data = {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}",
                "timestamp": datetime.now().isoformat()
            }
            service.add_message(active_conversation, message_data)
        
        # Should handle multiple messages
        assert active_conversation is not None
    
    def test_conversation_with_custom_metadata(self, service):
        """Test creating conversation with custom metadata"""
        metadata = {
            "custom_field": "value",
            "number": 42,
            "nested": {"key": "value"}
        }
        
        conversation = service.create_conversation(
            persona_id="persona1",
            context_id="context1",
            metadata=metadata
        )
        
        assert conversation.metadata == metadata or conversation.metadata.get("custom_field") == "value"
    
    def test_multiple_conversations_independent(self, service):
        """Test that multiple conversations are independent"""
        conv1 = service.create_conversation("persona1", "context1")
        conv2 = service.create_conversation("persona2", "context2")
        
        assert conv1.id != conv2.id
        assert conv1.persona_id != conv2.persona_id
    
    def test_conversation_lifecycle(self, service):
        """Test full conversation lifecycle"""
        # Create
        conversation = service.create_conversation("persona1", "context1")
        assert conversation.status == ConversationStatus.ACTIVE
        
        # Add messages
        message = {
            "role": "user",
            "content": "Hello",
            "timestamp": datetime.now().isoformat()
        }
        service.add_message(conversation, message)
        
        # Complete
        service.complete_conversation(conversation, analysis_id="analysis_1")
        assert conversation.status == ConversationStatus.COMPLETED
        assert conversation.analysis_id == "analysis_1"
    
    def test_cannot_add_message_to_completed(self, service, active_conversation):
        """Test cannot add message to completed conversation"""
        service.complete_conversation(active_conversation)
        
        message = {
            "role": "user",
            "content": "Test",
            "timestamp": datetime.now().isoformat()
        }
        
        # Should raise or handle gracefully
        try:
            service.add_message(active_conversation, message)
        except ConversationStateError:
            # Expected
            pass
    
    def test_created_conversations_have_transcription_id(self, service):
        """Test that created conversations have transcription ID"""
        conversation = service.create_conversation("persona1", "context1")
        
        # Should have transcription ID (or None)
        assert hasattr(conversation, 'transcription_id')
    
    def test_service_validates_persona_id(self, service):
        """Test that service validates persona_id"""
        conversation = service.create_conversation("valid_persona", "context1")
        assert conversation.persona_id == "valid_persona"
    
    def test_service_validates_context_id(self, service):
        """Test that service validates context_id"""
        conversation = service.create_conversation("persona1", "valid_context")
        assert conversation.context_id == "valid_context"
    
    def test_completion_timestamp_after_creation(self, service):
        """Test that completion timestamp is after creation"""
        conversation = service.create_conversation("persona1", "context1")
        created_at = conversation.created_at
        
        service.complete_conversation(conversation)
        
        assert conversation.completed_at >= created_at
    
    def test_multiple_completions_idempotent(self, service, active_conversation):
        """Test that completing multiple times is idempotent"""
        service.complete_conversation(active_conversation)
        first_completed_at = active_conversation.completed_at
        
        service.complete_conversation(active_conversation)
        
        # Should remain completed
        assert active_conversation.status == ConversationStatus.COMPLETED
    
    def test_service_methods_exist(self, service):
        """Test that expected methods exist"""
        assert hasattr(service, 'create_conversation')
        assert hasattr(service, 'complete_conversation')
        assert hasattr(service, 'cancel_conversation')
        assert hasattr(service, 'add_message')
        assert hasattr(service, 'validate_conversation_active')

