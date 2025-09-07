"""
Conversation repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.value_objects.conversation_id import ConversationId


class ConversationRepository(ABC):
    """Abstract repository for conversation entities."""
    
    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """Save a conversation."""
        pass
    
    @abstractmethod
    async def get_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """Get conversation by ID."""
        pass
    
    @abstractmethod
    async def get_by_persona_id(self, persona_id: str, limit: int = 100, offset: int = 0) -> List[Conversation]:
        """Get conversations by persona ID."""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Conversation]:
        """Get all conversations with pagination."""
        pass
    
    @abstractmethod
    async def delete(self, conversation_id: ConversationId) -> bool:
        """Delete a conversation."""
        pass
    
    @abstractmethod
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if conversation exists."""
        pass
