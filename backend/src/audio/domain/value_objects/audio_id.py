"""
Audio ID value object.
"""
from dataclasses import dataclass
from typing import Union
import uuid


@dataclass(frozen=True)
class AudioId:
    """Value object for Audio ID."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Audio ID cannot be empty")
        
        # Validate UUID format
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError("Audio ID must be a valid UUID")
    
    @classmethod
    def generate(cls) -> 'AudioId':
        """Generate a new Audio ID."""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> 'AudioId':
        """Create Audio ID from string."""
        return cls(value)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AudioId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
