"""
DTOs (Data Transfer Objects) for conversation application layer.
"""
from typing import Optional, Dict, Any
from datetime import datetime


class ConversationDTO:
    """Data Transfer Object for Conversation."""
    
    def __init__(
        self,
        id: str,
        persona_id: str,
        context_id: str,
        status: str,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        transcription_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        duration_seconds: Optional[int] = None
    ):
        self.id = id
        self.persona_id = persona_id
        self.context_id = context_id
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at
        self.transcription_id = transcription_id
        self.analysis_id = analysis_id
        self.metadata = metadata or {}
        self.duration_seconds = duration_seconds


class StartConversationDTO:
    """DTO for starting a conversation."""
    
    def __init__(
        self,
        conversation_id: str,
        transcription_id: str,
        success: bool,
        message: Optional[str] = None
    ):
        self.conversation_id = conversation_id
        self.transcription_id = transcription_id
        self.success = success
        self.message = message


class ConversationResultDTO:
    """DTO for conversation operation results."""
    
    def __init__(
        self,
        conversation: Optional[ConversationDTO] = None,
        success: bool = True,
        message: Optional[str] = None
    ):
        self.conversation = conversation
        self.success = success
        self.message = message
