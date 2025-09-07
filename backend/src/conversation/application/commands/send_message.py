"""
Send message command.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from uuid import UUID

from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.entities.message import MessageRole


@dataclass
class SendMessageCommand:
    """Command to send a message in a conversation."""
    conversation_id: ConversationId
    role: MessageRole
    content: str
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("Message content is required")
        
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SendMessageResult:
    """Result of sending a message."""
    message_id: UUID
    success: bool
    message: Optional[str] = None
