"""
Shared domain events for the conversation simulator.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
from uuid import UUID


class DomainEvent(ABC):
    """Base class for domain events."""
    
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_id = UUID.uuid4()
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        pass


class ConversationStarted(DomainEvent):
    """Event raised when a conversation is started."""
    
    def __init__(self, conversation_id: UUID, persona_id: str):
        super().__init__()
        self.conversation_id = conversation_id
        self.persona_id = persona_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'ConversationStarted',
            'conversation_id': str(self.conversation_id),
            'persona_id': self.persona_id,
            'occurred_at': self.occurred_at.isoformat(),
            'event_id': str(self.event_id)
        }


class ConversationCompleted(DomainEvent):
    """Event raised when a conversation is completed."""
    
    def __init__(self, conversation_id: UUID, duration_seconds: int, message_count: int):
        super().__init__()
        self.conversation_id = conversation_id
        self.duration_seconds = duration_seconds
        self.message_count = message_count
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'ConversationCompleted',
            'conversation_id': str(self.conversation_id),
            'duration_seconds': self.duration_seconds,
            'message_count': self.message_count,
            'occurred_at': self.occurred_at.isoformat(),
            'event_id': str(self.event_id)
        }


class MessageAdded(DomainEvent):
    """Event raised when a message is added to a conversation."""
    
    def __init__(self, conversation_id: UUID, message_id: UUID, role: str, content: str):
        super().__init__()
        self.conversation_id = conversation_id
        self.message_id = message_id
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'MessageAdded',
            'conversation_id': str(self.conversation_id),
            'message_id': str(self.message_id),
            'role': self.role,
            'content': self.content,
            'occurred_at': self.occurred_at.isoformat(),
            'event_id': str(self.event_id)
        }


class AnalysisCompleted(DomainEvent):
    """Event raised when conversation analysis is completed."""
    
    def __init__(self, analysis_id: UUID, conversation_id: UUID, overall_score: float):
        super().__init__()
        self.analysis_id = analysis_id
        self.conversation_id = conversation_id
        self.overall_score = overall_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': 'AnalysisCompleted',
            'analysis_id': str(self.analysis_id),
            'conversation_id': str(self.conversation_id),
            'overall_score': self.overall_score,
            'occurred_at': self.occurred_at.isoformat(),
            'event_id': str(self.event_id)
        }
