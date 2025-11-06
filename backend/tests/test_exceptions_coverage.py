"""
Tests for exception classes - UPDATED
Only tests that work with current exception APIs
"""
import pytest

from src.shared.domain.exceptions import (
    DomainException,
)
from src.conversation.domain.exceptions import (
    ConversationException,
)


class TestDomainExceptions:
    """Tests for domain exception classes"""
    
    def test_domain_exception_creation(self):
        """Test creating domain exception"""
        exc = DomainException("Test error")
        assert str(exc) == "Test error"
    
    def test_domain_exception_is_exception(self):
        """Test domain exception is an Exception"""
        exc = DomainException("Test")
        assert isinstance(exc, Exception)


class TestConversationExceptions:
    """Tests for conversation exception classes"""
    
    def test_conversation_exception_creation(self):
        """Test creating conversation exception"""
        exc = ConversationException("Conversation error")
        assert str(exc) == "Conversation error"
    
    def test_exceptions_can_be_raised(self):
        """Test that exceptions can be raised"""
        with pytest.raises(ConversationException):
            raise ConversationException("Test error")
    
    def test_exception_with_context(self):
        """Test exception with additional context"""
        exc = ConversationException("Error with context")
        assert "context" in str(exc).lower()
    
    # =========================================================================
    # RECONSTRUCTED: Tests with correct constructors
    # =========================================================================
    
    def test_conversation_state_error_creation(self):
        """Test ConversationStateError with correct constructor"""
        from src.conversation.domain.exceptions import ConversationStateError
        
        exc = ConversationStateError("active", "complete")
        assert exc.current_state == "active"
        assert exc.attempted_operation == "complete"
    
    def test_message_validation_error_creation(self):
        """Test MessageValidationError with correct constructor"""
        from src.conversation.domain.exceptions import MessageValidationError
        
        exc = MessageValidationError("content", "Content cannot be empty")
        assert exc.field == "content"
        assert exc.reason == "Content cannot be empty"
    
    def test_conversation_not_found_error_creation(self):
        """Test ConversationNotFoundError with correct constructor"""
        from src.conversation.domain.exceptions import ConversationNotFoundError
        
        exc = ConversationNotFoundError("conv_123")
        assert exc.conversation_id == "conv_123"
        assert "conv_123" in str(exc)
    
    def test_invalid_message_role_error_creation(self):
        """Test InvalidMessageRoleError with correct constructor"""
        from src.conversation.domain.exceptions import InvalidMessageRoleError
        
        exc = InvalidMessageRoleError("invalid_role")
        assert exc.role == "invalid_role"
        assert "invalid_role" in str(exc)
    
    def test_conversation_already_completed_error_creation(self):
        """Test ConversationAlreadyCompletedError with correct constructor"""
        from src.conversation.domain.exceptions import ConversationAlreadyCompletedError
        
        exc = ConversationAlreadyCompletedError("conv_123")
        assert exc.conversation_id == "conv_123"
        assert "conv_123" in str(exc)
    
    def test_all_conversation_exceptions_can_be_raised(self):
        """Test that all conversation exceptions can be raised"""
        from src.conversation.domain.exceptions import (
            ConversationStateError,
            MessageValidationError,
            ConversationNotFoundError
        )
        
        with pytest.raises(ConversationStateError):
            raise ConversationStateError("active", "cancel")
        
        with pytest.raises(MessageValidationError):
            raise MessageValidationError("role", "Invalid role")
        
        with pytest.raises(ConversationNotFoundError):
            raise ConversationNotFoundError("test_id")
    
    def test_exceptions_are_instances_of_base(self):
        """Test that exceptions are instances of ConversationException"""
        from src.conversation.domain.exceptions import (
            ConversationException,
            ConversationStateError,
            MessageValidationError
        )
        
        state_err = ConversationStateError("active", "complete")
        msg_err = MessageValidationError("content", "Empty")
        
        assert isinstance(state_err, ConversationException)
        assert isinstance(msg_err, ConversationException)
