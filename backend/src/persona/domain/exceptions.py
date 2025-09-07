"""
Domain exceptions for the persona bounded context.
"""
from src.shared.domain.exceptions import DomainException


class PersonaException(DomainException):
    """Base class for persona domain exceptions."""
    pass


class PersonaValidationError(PersonaException):
    """Raised when persona validation fails."""
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Persona validation error in field '{field}': {reason}")


class PersonaNotFoundError(PersonaException):
    """Raised when a persona is not found."""
    
    def __init__(self, persona_id: str):
        self.persona_id = persona_id
        super().__init__(f"Persona with ID {persona_id} not found")


class InvalidPersonalityTraitError(PersonaException):
    """Raised when an invalid personality trait is used."""
    
    def __init__(self, trait: str):
        self.trait = trait
        super().__init__(f"Invalid personality trait: {trait}")


class InvalidAccentError(PersonaException):
    """Raised when an invalid accent is used."""
    
    def __init__(self, accent: str):
        self.accent = accent
        super().__init__(f"Invalid accent: {accent}")


class PersonaAlreadyExistsError(PersonaException):
    """Raised when trying to create a persona that already exists."""
    
    def __init__(self, persona_id: str):
        self.persona_id = persona_id
        super().__init__(f"Persona with ID {persona_id} already exists")


class PersonaConfigurationError(PersonaException):
    """Raised when persona configuration is invalid."""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Persona configuration error: {reason}")
