"""
Tests for Conversation Domain Service - UPDATED
Only tests for current API (can_X methods)
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.transcription import Transcription, TranscriptionStatus
from src.conversation.domain.entities.message import Message, MessageRole
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.value_objects.message_content import MessageContent


class TestConversationDomainService:
    """Tests for ConversationDomainService - current API only"""
    
    @pytest.fixture
    def service(self):
        """Create domain service instance"""
        return ConversationDomainService()
    
    
    # =========================================================================
    # Tests that PASS (current API)
    # =========================================================================
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
    
    def test_can_start_conversation_with_valid_persona(self, service):
        """Test can_start_conversation with valid persona_id"""
        assert service.can_start_conversation("persona1") is True
    
    def test_can_start_conversation_with_empty_persona(self, service):
        """Test can_start_conversation with empty persona_id"""
        assert service.can_start_conversation("") is False
        assert service.can_start_conversation("   ") is False
    
    def test_validate_message_content_valid(self, service):
        """Test validate_message_content with valid content"""
        assert service.validate_message_content("Hello world") is True
    
    def test_validate_message_content_empty(self, service):
        """Test validate_message_content with empty content"""
        assert service.validate_message_content("") is False
        assert service.validate_message_content("   ") is False
    
    def test_validate_message_content_too_long(self, service):
        """Test validate_message_content with too long content"""
        long_content = "a" * 10001
        assert service.validate_message_content(long_content) is False
    
    def test_get_conversation_metrics_without_transcription(self, service):
        """Test get_conversation_metrics with no transcription"""
        from uuid import uuid4
        conv = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test",
            context_id="test",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        metrics = service.get_conversation_metrics(conv)
        
        # Returns empty dict when no transcription
        assert isinstance(metrics, dict)
    
    def test_get_conversation_metrics_with_no_messages(self, service):
        """Test get_conversation_metrics with no messages provided"""
        from uuid import uuid4
        conv = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test",
            context_id="test",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        # Without transcription, returns empty dict
        metrics = service.get_conversation_metrics(conv, None)
        assert isinstance(metrics, dict)
    
    def test_validate_message_content_with_valid_lengths(self, service):
        """Test validate_message_content with various valid lengths"""
        assert service.validate_message_content("Short") is True
        assert service.validate_message_content("A" * 100) is True
        assert service.validate_message_content("A" * 1000) is True
        assert service.validate_message_content("A" * 10000) is True
    
    def test_validate_message_content_at_boundary(self, service):
        """Test validate_message_content at 10000 char boundary"""
        assert service.validate_message_content("A" * 10000) is True
        assert service.validate_message_content("A" * 10001) is False
    
    def test_can_start_conversation_with_none(self, service):
        """Test can_start_conversation with None"""
        assert service.can_start_conversation(None) is False
    
    def test_can_start_conversation_with_whitespace(self, service):
        """Test can_start_conversation with various whitespace"""
        assert service.can_start_conversation(" ") is False
        assert service.can_start_conversation("\t") is False
        assert service.can_start_conversation("\n") is False
    
    def test_validate_message_content_with_whitespace_only(self, service):
        """Test validate_message_content with whitespace only"""
        assert service.validate_message_content(" ") is False
        assert service.validate_message_content("\t\n") is False
    
    
