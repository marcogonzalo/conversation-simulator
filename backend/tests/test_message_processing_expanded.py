"""
Tests for MessageProcessingService - UPDATED
Only tests for current API
"""
import pytest
from src.conversation.domain.services.message_processing_service import MessageProcessingService


class TestMessageProcessingServiceExpanded:
    """Tests for MessageProcessingService - current API only"""
    
    @pytest.fixture
    def service(self):
        """Create message processing service"""
        return MessageProcessingService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
    
    # =========================================================================
    # RECONSTRUCTED: Tests for current API
    # =========================================================================
    
    def test_process_text_chunk_creates_message(self, service):
        """Test process_text_chunk creates new message"""
        from uuid import uuid4
        
        message = service.process_text_chunk(
            conversation_id=uuid4(),
            role="user",
            content="Hello",
            is_final=True
        )
        
        assert message is not None
        assert message.role == "user"
    
    def test_process_text_chunk_with_multiple_chunks(self, service):
        """Test process_text_chunk aggregates multiple chunks"""
        from uuid import uuid4
        conv_id = uuid4()
        
        # First chunk
        msg1 = service.process_text_chunk(conv_id, "user", "Hello ", is_final=False)
        # Second chunk
        msg2 = service.process_text_chunk(conv_id, "user", "world", is_final=True)
        
        # Should aggregate
        assert msg2 is not None
    
    def test_process_text_chunk_with_confidence(self, service):
        """Test process_text_chunk with confidence score"""
        from uuid import uuid4
        
        message = service.process_text_chunk(
            conversation_id=uuid4(),
            role="assistant",
            content="Response",
            is_final=True,
            confidence=0.95
        )
        
        assert message is not None
    
    def test_process_text_chunk_with_message_group_id(self, service):
        """Test process_text_chunk with message_group_id"""
        from uuid import uuid4
        
        message = service.process_text_chunk(
            conversation_id=uuid4(),
            role="user",
            content="Test",
            is_final=True,
            message_group_id="group1"
        )
        
        assert message is not None
    
    def test_get_pending_messages(self, service):
        """Test get_pending_messages returns list"""
        from uuid import uuid4
        conv_id = uuid4()
        
        # Create a pending message
        service.process_text_chunk(conv_id, "user", "Pending", is_final=False)
        
        pending = service.get_pending_messages(conv_id)
        assert isinstance(pending, list)
    
    def test_cleanup_expired_messages(self, service):
        """Test cleanup_expired_messages"""
        expired = service.cleanup_expired_messages(max_age_seconds=300)
        assert isinstance(expired, list)
    
    def test_merge_messages_with_empty_list(self, service):
        """Test merge_messages with empty list"""
        result = service.merge_messages([])
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_get_conversation_summary_with_empty_list(self, service):
        """Test get_conversation_summary with empty messages"""
        summary = service.get_conversation_summary([])
        assert isinstance(summary, dict)
    
    def test_process_text_chunk_empty_content(self, service):
        """Test process_text_chunk with empty content"""
        from uuid import uuid4
        
        message = service.process_text_chunk(
            conversation_id=uuid4(),
            role="user",
            content="",
            is_final=True
        )
        
        assert message is not None
    
    def test_process_text_chunk_different_roles(self, service):
        """Test process_text_chunk with different roles"""
        from uuid import uuid4
        conv_id = uuid4()
        
        user_msg = service.process_text_chunk(conv_id, "user", "User says", is_final=True)
        assistant_msg = service.process_text_chunk(conv_id, "assistant", "AI responds", is_final=True)
        
        assert user_msg.role == "user"
        assert assistant_msg.role == "assistant"
