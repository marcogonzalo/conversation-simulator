"""
Persona ID value object.
"""
from dataclasses import dataclass
from typing import Union
import re


@dataclass(frozen=True)
class PersonaId:
    """Value object for persona IDs using slugs."""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("PersonaId value cannot be empty")
        
        # Validate slug format (lowercase letters, numbers, underscores, hyphens)
        if not re.match(r'^[a-z0-9_-]+$', self.value):
            raise ValueError("PersonaId must be a valid slug (lowercase letters, numbers, underscores, hyphens only)")
        
        if len(self.value) > 50:
            raise ValueError("PersonaId too long (max 50 characters)")
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'PersonaId':
        """Create PersonaId from string."""
        return cls(value.lower().strip())
    
    @classmethod
    def from_name(cls, name: str) -> 'PersonaId':
        """Create PersonaId from person name (converts to slug)."""
        # Convert name to slug: lowercase, replace spaces with underscores, remove special chars
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        slug = re.sub(r'\s+', '_', slug.strip())
        return cls(slug)
