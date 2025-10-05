"""
Conversation aggregate root for the conversation bounded context.
This is the main aggregate that relates Transcription, Analysis, Persona, and Context.
References are made by file IDs since these entities are stored as files.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from src.shared.domain.value_objects import ConversationId
from src.shared.domain.events import ConversationStarted, ConversationCompleted
from src.conversation.domain.exceptions import ConversationStateError


class ConversationStatus(Enum):
    """Conversation status enumeration."""
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Conversation:
    """Conversation aggregate root that manages the complete conversation lifecycle."""
    
    def __init__(
        self,
        conversation_id: ConversationId,
        persona_id: str,
        context_id: str,
        status: ConversationStatus = ConversationStatus.CREATED,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        transcription_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        self._id = conversation_id
        self._persona_id = persona_id
        self._context_id = context_id
        self._status = status
        self._created_at = created_at or datetime.utcnow()
        self._completed_at = completed_at
        self._transcription_id = transcription_id  # Reference to transcription file
        self._analysis_id = analysis_id  # Reference to analysis file
        self._metadata = metadata or {}
        self._domain_events: List = []
    
    @property
    def id(self) -> ConversationId:
        return self._id
    
    @property
    def persona_id(self) -> str:
        return self._persona_id
    
    @property
    def context_id(self) -> str:
        return self._context_id
    
    @property
    def status(self) -> ConversationStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    @property
    def transcription_id(self) -> Optional[str]:
        return self._transcription_id
    
    @property
    def analysis_id(self) -> Optional[str]:
        return self._analysis_id
    
    @property
    def transcription(self) -> Optional['Transcription']:
        """Get transcription entity if available."""
        # This would need to be loaded from the transcription file
        # For now, return None to indicate transcription needs to be loaded separately
        return None
    
    def has_transcription(self) -> bool:
        """Check if conversation has a transcription."""
        return self._transcription_id is not None
    
    @property
    def metadata(self) -> dict:
        return self._metadata.copy()
    
    @property
    def duration_seconds(self) -> Optional[int]:
        if self._completed_at:
            return int((self._completed_at - self._created_at).total_seconds())
        return None
    
    @property
    def domain_events(self) -> List:
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after they've been processed."""
        self._domain_events.clear()
    
    def start_transcription(self) -> str:
        """Start a new transcription for this conversation. Returns transcription file ID."""
        if self._status != ConversationStatus.CREATED:
            raise ConversationStateError(
                self._status.value,
                "start_transcription"
            )
        
        if self._transcription_id is not None:
            raise ConversationStateError(
                "transcription_already_exists",
                "start_transcription"
            )
        
        # Generate transcription file ID
        transcription_id = str(ConversationId.generate())
        self._transcription_id = transcription_id
        self._status = ConversationStatus.ACTIVE
        
        self._domain_events.append(
            ConversationStarted(
                conversation_id=self._id.value,
                persona_id=self._persona_id
            )
        )
        
        return transcription_id
    
    def complete_transcription(self) -> None:
        """Complete the transcription and mark conversation as ready for analysis."""
        if self._transcription_id is None:
            raise ConversationStateError(
                "no_transcription",
                "complete_transcription"
            )
        
        # Conversation remains active until analysis is completed
        # The conversation will be marked as completed when analysis is finished
        # The actual transcription completion is handled by the transcription service
    
    def assign_analysis(self, analysis_id: str) -> None:
        """Assign an analysis to this conversation."""
        if self._status not in [ConversationStatus.ACTIVE]:
            raise ConversationStateError(
                self._status.value,
                "assign_analysis"
            )
        
        self._analysis_id = analysis_id
    
    def complete(self) -> None:
        """Complete the conversation (after analysis is finished)."""
        if self._status != ConversationStatus.ACTIVE:
            raise ConversationStateError(
                self._status.value,
                "complete"
            )
        
        if self._transcription_id is None:
            raise ConversationStateError(
                "transcription_not_assigned",
                "complete"
            )
        
        if self._analysis_id is None:
            raise ConversationStateError(
                "analysis_not_assigned",
                "complete"
            )
        
        self._status = ConversationStatus.COMPLETED
        self._completed_at = datetime.utcnow()
        
        self._domain_events.append(
            ConversationCompleted(
                conversation_id=self._id.value,
                duration_seconds=self.duration_seconds or 0,
                message_count=0  # Will be populated by the service when loading transcription
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
        self._completed_at = datetime.utcnow()
        
        # Transcription cancellation is handled by the transcription service
    
    def update_metadata(self, key: str, value: any) -> None:
        """Update conversation metadata."""
        self._metadata[key] = value
    
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self._status == ConversationStatus.ACTIVE
    
    def is_completed(self) -> bool:
        """Check if conversation is completed."""
        return self._status == ConversationStatus.COMPLETED
    
    def has_transcription(self) -> bool:
        """Check if conversation has a transcription."""
        return self._transcription_id is not None
    
    def has_analysis(self) -> bool:
        """Check if conversation has an analysis."""
        return self._analysis_id is not None
    
    def can_start_transcription(self) -> bool:
        """Check if transcription can be started."""
        return self._status == ConversationStatus.CREATED and self._transcription_id is None
    
    def can_complete(self) -> bool:
        """Check if conversation can be completed."""
        return (
            self._status == ConversationStatus.ACTIVE and
            self._transcription_id is not None and
            self._analysis_id is not None
        )