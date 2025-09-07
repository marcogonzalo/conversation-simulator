"""
Start conversation command.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from src.conversation.domain.value_objects.conversation_id import ConversationId


@dataclass
class StartConversationCommand:
    """Command to start a new conversation."""
    persona_id: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.persona_id or not self.persona_id.strip():
            raise ValueError("Persona ID is required")
        
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StartConversationResult:
    """Result of starting a conversation."""
    conversation_id: ConversationId
    success: bool
    message: Optional[str] = None
