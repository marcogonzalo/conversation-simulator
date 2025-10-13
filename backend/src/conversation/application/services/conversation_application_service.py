"""
Conversation application service following Hexagonal Architecture.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.application.dtos.conversation_dto import (
    ConversationDTO, StartConversationDTO, ConversationResultDTO
)


class ConversationApplicationService:
    """Application service for conversation operations.
    
    This follows Hexagonal Architecture - it depends only on domain ports,
    not on concrete infrastructure implementations.
    """
    
    def __init__(
        self,
        conversation_repository: IConversationRepository,
        domain_service: ConversationDomainService
    ):
        self._conversation_repository = conversation_repository
        self._domain_service = domain_service
    
    async def start_conversation(
        self, 
        persona_id: str, 
        context_id: str = "default",
        metadata: Optional[dict] = None
    ) -> StartConversationDTO:
        """Start a new conversation."""
        try:
            # Validate inputs using domain service
            if not self._domain_service.can_start_conversation(persona_id):
                return StartConversationDTO(
                    conversation_id=None,
                    transcription_id=None,
                    success=False,
                    message="Invalid persona ID"
                )
            
            # Create conversation domain entity
            conversation_id = ConversationId.generate()
            conversation = Conversation(
                conversation_id=conversation_id,
                persona_id=persona_id,
                context_id=context_id,
                metadata=metadata
            )
            
            # Start transcription
            transcription_id = conversation.start_transcription()
            
            # Save using repository port (dependency inversion)
            await self._conversation_repository.save(conversation)
            
            return StartConversationDTO(
                conversation_id=str(conversation_id.value),
                transcription_id=transcription_id,
                success=True,
                message="Conversation started successfully"
            )
            
        except Exception as e:
            return StartConversationDTO(
                conversation_id=None,
                transcription_id=None,
                success=False,
                message=f"Failed to start conversation: {str(e)}"
            )
    
    async def get_conversation(self, conversation_id: str) -> ConversationResultDTO:
        """Get a conversation by ID."""
        try:
            conversation_id_obj = ConversationId(value=UUID(conversation_id))
        except (ValueError, TypeError):
            return ConversationResultDTO(
                conversation=None,
                success=False,
                message="Invalid conversation ID"
            )
        
        try:
            # Use repository port (dependency inversion)
            conversation = await self._conversation_repository.get_by_id(conversation_id_obj)
            
            if not conversation:
                return ConversationResultDTO(
                    conversation=None,
                    success=False,
                    message="Conversation not found"
                )
            
            # Convert domain entity to DTO
            conversation_dto = ConversationDTO(
                id=str(conversation.id.value),
                persona_id=conversation.persona_id,
                context_id=conversation.context_id,
                status=conversation.status.value,
                created_at=conversation.created_at,
                completed_at=conversation.completed_at,
                transcription_id=conversation.transcription_id,
                analysis_id=conversation.analysis_id,
                metadata=conversation.metadata,
                duration_seconds=conversation.duration_seconds
            )
            
            return ConversationResultDTO(
                conversation=conversation_dto,
                success=True,
                message="Conversation retrieved successfully"
            )
            
        except Exception as e:
            return ConversationResultDTO(
                conversation=None,
                success=False,
                message=f"Failed to get conversation: {str(e)}"
            )
    
    async def get_conversations(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[ConversationDTO]:
        """Get all conversations (for history view)."""
        try:
            # Use repository port (dependency inversion)
            conversations = await self._conversation_repository.get_all(limit, offset)
            
            return [
                ConversationDTO(
                    id=str(conv.id.value),
                    persona_id=conv.persona_id,
                    context_id=conv.context_id,
                    status=conv.status.value,
                    created_at=conv.created_at,
                    completed_at=conv.completed_at,
                    transcription_id=conv.transcription_id,
                    analysis_id=conv.analysis_id,
                    metadata=conv.metadata,
                    duration_seconds=conv.duration_seconds
                )
                for conv in conversations
            ]
            
        except Exception as e:
            return []
    
    async def get_conversations_by_persona(
        self, 
        persona_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[ConversationDTO]:
        """Get conversations by persona ID."""
        try:
            # Use repository port (dependency inversion)
            conversations = await self._conversation_repository.get_by_persona_id(
                persona_id, limit, offset
            )
            
            return [
                ConversationDTO(
                    id=str(conv.id.value),
                    persona_id=conv.persona_id,
                    context_id=conv.context_id,
                    status=conv.status.value,
                    created_at=conv.created_at,
                    completed_at=conv.completed_at,
                    transcription_id=conv.transcription_id,
                    analysis_id=conv.analysis_id,
                    metadata=conv.metadata,
                    duration_seconds=conv.duration_seconds
                )
                for conv in conversations
            ]
            
        except Exception as e:
            return []
    
    async def complete_conversation(self, conversation_id: str, analysis_id: Optional[str] = None) -> bool:
        """Complete a conversation."""
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
            
            # Get conversation using repository port
            conversation = await self._conversation_repository.get_by_id(conversation_id_obj)
            
            if not conversation:
                return False
            
            # Validate using domain service
            if not self._domain_service.can_complete_conversation(conversation):
                return False
            
            # Complete the conversation (domain logic)
            conversation.complete()
            
            # Save using repository port
            await self._conversation_repository.save(conversation)
            
            return True
        
        except Exception:
            return False
    
    async def assign_analysis(self, conversation_id: str, analysis_id: str) -> bool:
        """Assign an analysis to a conversation."""
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
            
            # Update using repository port
            success = await self._conversation_repository.update_status(
                conversation_id=conversation_id_obj,
                status=ConversationStatus.ACTIVE.value,  # Keep current status
                analysis_id=analysis_id
            )
            
            return success
        
        except Exception:
            return False
    
    async def get_all_conversations(self, limit: int = 100, offset: int = 0) -> List[ConversationDTO]:
        """Get all conversations with pagination."""
        try:
            # Use repository port (dependency inversion)
            conversations = await self._conversation_repository.get_all(limit, offset)
            
            return [
                ConversationDTO(
                    id=str(conv.id.value),
                    persona_id=conv.persona_id,
                    context_id=conv.context_id,
                    status=conv.status.value,
                    created_at=conv.created_at,
                    completed_at=conv.completed_at,
                    transcription_id=conv.transcription_id,
                    analysis_id=conv.analysis_id,
                    metadata=conv.metadata,
                    duration_seconds=conv.duration_seconds
                )
                for conv in conversations
            ]
            
        except Exception as e:
            return []
