"""
Get conversation query.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.entities.conversation import ConversationStatus
from src.conversation.domain.entities.message import MessageRole


@dataclass
class GetConversationQuery:
    """Query to get a conversation by ID."""
    conversation_id: ConversationId


@dataclass
class MessageDto:
    """Message data transfer object."""
    id: str
    conversation_id: str
    role: str
    content: str
    audio_url: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class ConversationDto:
    """Conversation data transfer object."""
    id: str
    persona_id: str
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    messages: List[MessageDto]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class GetConversationResult:
    """Result of getting a conversation."""
    conversation: Optional[ConversationDto]
    success: bool
    message: Optional[str] = None
