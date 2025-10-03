"""
Message entity for the conversation bounded context.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from src.shared.domain.value_objects import MessageContent
from src.shared.domain.events import MessageAdded


class MessageRole(Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "ai"
    SYSTEM = "system"


class Message:
    """Message entity."""
    
    def __init__(
        self,
        message_id: UUID,
        conversation_id: UUID,
        role: MessageRole,
        content: MessageContent,
        audio_url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ):
        self._id = message_id
        self._conversation_id = conversation_id
        self._role = role
        self._content = content
        self._audio_url = audio_url
        self._timestamp = timestamp or datetime.utcnow()
        self._metadata = metadata or {}
        self._domain_events: List = []
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def conversation_id(self) -> UUID:
        return self._conversation_id
    
    @property
    def role(self) -> MessageRole:
        return self._role
    
    @property
    def content(self) -> MessageContent:
        return self._content
    
    @property
    def audio_url(self) -> Optional[str]:
        return self._audio_url
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    @property
    def metadata(self) -> dict:
        return self._metadata.copy()
    
    @property
    def domain_events(self) -> List:
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after they've been processed."""
        self._domain_events.clear()
    
    def add_audio_url(self, audio_url: str) -> None:
        """Add audio URL to the message."""
        self._audio_url = audio_url
    
    def update_metadata(self, key: str, value: any) -> None:
        """Update message metadata."""
        self._metadata[key] = value
    
    def is_user_message(self) -> bool:
        """Check if message is from user."""
        return self._role == MessageRole.USER
    
    def is_assistant_message(self) -> bool:
        """Check if message is from assistant."""
        return self._role == MessageRole.ASSISTANT
    
    def is_system_message(self) -> bool:
        """Check if message is from system."""
        return self._role == MessageRole.SYSTEM
    
    def has_audio(self) -> bool:
        """Check if message has audio."""
        return self._audio_url is not None
    
    @classmethod
    def create_user_message(
        cls,
        conversation_id: UUID,
        content: str,
        audio_url: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> 'Message':
        """Create a user message."""
        message = cls(
            message_id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=MessageContent(content),
            audio_url=audio_url,
            timestamp=timestamp
        )
        
        message._domain_events.append(
            MessageAdded(
                conversation_id=conversation_id,
                message_id=message._id,
                role=MessageRole.USER.value,
                content=content
            )
        )
        
        return message
    
    @classmethod
    def create_assistant_message(
        cls,
        conversation_id: UUID,
        content: str,
        audio_url: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> 'Message':
        """Create an assistant message."""
        message = cls(
            message_id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=MessageContent(content),
            audio_url=audio_url,
            timestamp=timestamp
        )
        
        message._domain_events.append(
            MessageAdded(
                conversation_id=conversation_id,
                message_id=message._id,
                role=MessageRole.ASSISTANT.value,
                content=content
            )
        )
        
        return message
    
    @classmethod
    def create_system_message(
        cls,
        conversation_id: UUID,
        content: str
    ) -> 'Message':
        """Create a system message."""
        message = cls(
            message_id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.SYSTEM,
            content=MessageContent(content)
        )
        
        message._domain_events.append(
            MessageAdded(
                conversation_id=conversation_id,
                message_id=message._id,
                role=MessageRole.SYSTEM.value,
                content=content
            )
        )
        
        return message
