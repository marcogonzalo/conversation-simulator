"""
Persona repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.persona.domain.entities.persona import Persona
from src.persona.domain.value_objects.persona_id import PersonaId


class PersonaRepository(ABC):
    """Abstract repository for persona entities."""
    
    @abstractmethod
    async def save(self, persona: Persona) -> None:
        """Save a persona."""
        pass
    
    @abstractmethod
    async def get_by_id(self, persona_id: PersonaId) -> Optional[Persona]:
        """Get persona by ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Persona]:
        """Get all personas."""
        pass
    
    @abstractmethod
    async def get_by_accent(self, accent: str) -> List[Persona]:
        """Get personas by accent type."""
        pass
    
    @abstractmethod
    async def get_by_traits(self, traits: List[str]) -> List[Persona]:
        """Get personas by personality traits."""
        pass
    
    @abstractmethod
    async def delete(self, persona_id: PersonaId) -> bool:
        """Delete a persona."""
        pass
    
    @abstractmethod
    async def exists(self, persona_id: PersonaId) -> bool:
        """Check if persona exists."""
        pass
