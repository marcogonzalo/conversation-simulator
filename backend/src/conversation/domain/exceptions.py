"""
Domain exceptions for the conversation bounded context.
"""
from src.shared.domain.exceptions import DomainException


class ConversationException(DomainException):
    """Base class for conversation domain exceptions."""
    pass


class ConversationStateError(ConversationException):
    """Raised when conversation state operations are invalid."""
    
    def __init__(self, current_state: str, attempted_operation: str):
        self.current_state = current_state
        self.attempted_operation = attempted_operation
        super().__init__(
            f"Cannot perform '{attempted_operation}' on conversation in state '{current_state}'"
        )


class MessageValidationError(ConversationException):
    """Raised when message validation fails."""
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Message validation error in field '{field}': {reason}")


class ConversationNotFoundError(ConversationException):
    """Raised when a conversation is not found."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        super().__init__(f"Conversation with ID {conversation_id} not found")


class InvalidMessageRoleError(ConversationException):
    """Raised when an invalid message role is used."""
    
    def __init__(self, role: str):
        self.role = role
        super().__init__(f"Invalid message role: {role}")


class ConversationAlreadyCompletedError(ConversationException):
    """Raised when trying to modify a completed conversation."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        super().__init__(f"Cannot modify completed conversation {conversation_id}")
