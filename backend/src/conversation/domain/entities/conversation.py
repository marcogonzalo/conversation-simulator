"""
Conversation entity for the conversation bounded context.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from src.shared.domain.value_objects import ConversationId
from src.shared.domain.events import ConversationStarted, ConversationCompleted
from src.conversation.domain.entities.message import Message
from src.conversation.domain.exceptions import ConversationStateError


class ConversationStatus(Enum):
    """Conversation status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Conversation:
    """Conversation aggregate root."""
    
    def __init__(
        self,
        conversation_id: ConversationId,
        persona_id: str,
        status: ConversationStatus = ConversationStatus.PENDING,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
        messages: Optional[List[Message]] = None,
        metadata: Optional[dict] = None
    ):
        self._id = conversation_id
        self._persona_id = persona_id
        self._status = status
        self._started_at = started_at
        self._ended_at = ended_at
        self._messages = messages or []
        self._metadata = metadata or {}
        self._domain_events: List = []
    
    @property
    def id(self) -> ConversationId:
        return self._id
    
    @property
    def persona_id(self) -> str:
        return self._persona_id
    
    @property
    def status(self) -> ConversationStatus:
        return self._status
    
    @property
    def started_at(self) -> Optional[datetime]:
        return self._started_at
    
    @property
    def ended_at(self) -> Optional[datetime]:
        return self._ended_at
    
    @property
    def messages(self) -> List[Message]:
        return self._messages.copy()
    
    @property
    def metadata(self) -> dict:
        return self._metadata.copy()
    
    @property
    def duration_seconds(self) -> Optional[int]:
        if self._started_at and self._ended_at:
            return int((self._ended_at - self._started_at).total_seconds())
        return None
    
    @property
    def domain_events(self) -> List:
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after they've been processed."""
        self._domain_events.clear()
    
    def start(self) -> None:
        """Start the conversation."""
        if self._status != ConversationStatus.PENDING:
            raise ConversationStateError(
                self._status.value,
                "start"
            )
        
        self._status = ConversationStatus.ACTIVE
        self._started_at = datetime.utcnow()
        
        self._domain_events.append(
            ConversationStarted(
                conversation_id=self._id.value,
                persona_id=self._persona_id
            )
        )
    
    def pause(self) -> None:
        """Pause the conversation."""
        if self._status != ConversationStatus.ACTIVE:
            raise ConversationStateError(
                self._status.value,
                "pause"
            )
        
        self._status = ConversationStatus.PAUSED
    
    def resume(self) -> None:
        """Resume the conversation."""
        if self._status != ConversationStatus.PAUSED:
            raise ConversationStateError(
                self._status.value,
                "resume"
            )
        
        self._status = ConversationStatus.ACTIVE
    
    def complete(self) -> None:
        """Complete the conversation."""
        if self._status not in [ConversationStatus.ACTIVE, ConversationStatus.PAUSED]:
            raise ConversationStateError(
                self._status.value,
                "complete"
            )
        
        self._status = ConversationStatus.COMPLETED
        self._ended_at = datetime.utcnow()
        
        self._domain_events.append(
            ConversationCompleted(
                conversation_id=self._id.value,
                duration_seconds=self.duration_seconds or 0,
                message_count=len(self._messages)
            )
        )
    
    def cancel(self) -> None:
        """Cancel the conversation."""
        if self._status == ConversationStatus.COMPLETED:
            raise ConversationStateError(
                self._status.value,
                "cancel"
            )
        
        self._status = ConversationStatus.CANCELLED
        self._ended_at = datetime.utcnow()
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        if self._status not in [ConversationStatus.ACTIVE, ConversationStatus.PAUSED]:
            raise ConversationStateError(
                self._status.value,
                "add_message"
            )
        
        self._messages.append(message)
    
    def update_metadata(self, key: str, value: any) -> None:
        """Update conversation metadata."""
        self._metadata[key] = value
    
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self._status == ConversationStatus.ACTIVE
    
    def is_completed(self) -> bool:
        """Check if conversation is completed."""
        return self._status == ConversationStatus.COMPLETED
    
    def can_add_message(self) -> bool:
        """Check if a message can be added."""
        return self._status in [ConversationStatus.ACTIVE, ConversationStatus.PAUSED]
