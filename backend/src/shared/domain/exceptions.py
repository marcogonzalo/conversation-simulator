"""
Shared domain exceptions for the conversation simulator.
"""
from typing import Optional


class DomainException(Exception):
    """Base class for domain exceptions."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    
    def __init__(self, entity_type: str, entity_id: str, message: Optional[str] = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.message = message or f"{entity_type} with ID {entity_id} not found"
        super().__init__(self.message)


class InvalidOperationError(DomainException):
    """Raised when an invalid operation is attempted."""
    
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Invalid operation '{operation}': {reason}")


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    
    def __init__(self, rule: str, details: Optional[str] = None):
        self.rule = rule
        self.details = details
        message = f"Business rule violation: {rule}"
        if details:
            message += f" - {details}"
        super().__init__(message)


class AudioProcessingError(DomainException):
    """Raised when audio processing fails."""
    
    def __init__(self, operation: str, details: Optional[str] = None):
        self.operation = operation
        self.details = details
        message = f"Audio processing error in {operation}"
        if details:
            message += f": {details}"
        super().__init__(message)


class AIServiceError(DomainException):
    """Raised when AI service operations fail."""
    
    def __init__(self, service: str, operation: str, details: Optional[str] = None):
        self.service = service
        self.operation = operation
        self.details = details
        message = f"AI service error in {service} during {operation}"
        if details:
            message += f": {details}"
        super().__init__(message)


class ConversationStateError(DomainException):
    """Raised when conversation state operations are invalid."""
    
    def __init__(self, current_state: str, attempted_operation: str):
        self.current_state = current_state
        self.attempted_operation = attempted_operation
        super().__init__(
            f"Cannot perform '{attempted_operation}' on conversation in state '{current_state}'"
        )
