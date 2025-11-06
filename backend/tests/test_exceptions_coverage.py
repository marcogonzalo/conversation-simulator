"""
Tests for exception classes to improve coverage
"""
import pytest

from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFoundError,
    InvalidOperationError,
    BusinessRuleViolationError,
    AudioProcessingError,
    AIServiceError
)
from src.conversation.domain.exceptions import (
    ConversationException,
    ConversationStateError,
    MessageValidationError,
    ConversationNotFoundError,
    InvalidMessageRoleError,
    ConversationAlreadyCompletedError
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
    
    def test_entity_not_found_error_creation(self):
        """Test creating entity not found error"""
        exc = EntityNotFoundError("Entity not found")
        assert str(exc) == "Entity not found"
    
    def test_entity_not_found_error_is_domain_exception(self):
        """Test entity not found error extends domain exception"""
        exc = EntityNotFoundError("Test")
        assert isinstance(exc, DomainException)
    
    def test_invalid_operation_error_creation(self):
        """Test creating invalid operation error"""
        exc = InvalidOperationError("Invalid operation")
        assert str(exc) == "Invalid operation"
    
    def test_business_rule_violation_error_creation(self):
        """Test creating business rule violation error"""
        exc = BusinessRuleViolationError("Rule violated")
        assert str(exc) == "Rule violated"
    
    def test_audio_processing_error_creation(self):
        """Test creating audio processing error"""
        exc = AudioProcessingError("Audio error")
        assert str(exc) == "Audio error"
    
    def test_ai_service_error_creation(self):
        """Test creating AI service error"""
        exc = AIServiceError("AI error")
        assert str(exc) == "AI error"


class TestConversationExceptions:
    """Tests for conversation exception classes"""
    
    def test_conversation_exception_creation(self):
        """Test creating conversation exception"""
        exc = ConversationException("Conversation error")
        assert str(exc) == "Conversation error"
    
    def test_conversation_state_error(self):
        """Test conversation state error"""
        exc = ConversationStateError("Invalid state")
        assert str(exc) == "Invalid state"
        assert isinstance(exc, ConversationException)
    
    def test_message_validation_error(self):
        """Test message validation error"""
        exc = MessageValidationError("Invalid message")
        assert str(exc) == "Invalid message"
    
    def test_conversation_not_found_error(self):
        """Test conversation not found error"""
        exc = ConversationNotFoundError("Conversation not found")
        assert str(exc) == "Conversation not found"
    
    def test_invalid_message_role_error(self):
        """Test invalid message role error"""
        exc = InvalidMessageRoleError("Invalid role")
        assert str(exc) == "Invalid role"
    
    def test_conversation_already_completed_error(self):
        """Test conversation already completed error"""
        exc = ConversationAlreadyCompletedError("Already completed")
        assert str(exc) == "Already completed"
    
    def test_exceptions_can_be_raised(self):
        """Test exceptions can be raised and caught"""
        with pytest.raises(ConversationException):
            raise ConversationException("Test")
    
    def test_exception_with_context(self):
        """Test exception with additional context"""
        exc = ConversationNotFoundError("Not found: abc123")
        assert "abc123" in str(exc)
    
    def test_all_exceptions_are_catchable(self):
        """Test all exceptions can be caught as base Exception"""
        exceptions = [
            DomainException("Test"),
            EntityNotFoundError("Test"),
            ConversationException("Test"),
            ConversationStateError("Test"),
            AudioProcessingError("Test"),
            AIServiceError("Test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, Exception)

