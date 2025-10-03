"""
Conversation application service.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.conversation.application.commands.start_conversation import StartConversationCommand, StartConversationResult
from src.conversation.application.commands.send_message import SendMessageCommand, SendMessageResult
from src.conversation.application.queries.get_conversation import GetConversationQuery, GetConversationResult, ConversationDto
from src.conversation.application.handlers.command_handlers import StartConversationCommandHandler, SendMessageCommandHandler
from src.conversation.application.handlers.query_handlers import GetConversationQueryHandler
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.entities.message import MessageRole
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.domain.repositories.conversation_repository import ConversationRepository


class ConversationApplicationService:
    """Application service for conversation operations."""
    
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        domain_service: ConversationDomainService
    ):
        self._conversation_repository = conversation_repository
        self._domain_service = domain_service
        
        # Initialize handlers
        self._start_conversation_handler = StartConversationCommandHandler(
            conversation_repository, domain_service
        )
        self._send_message_handler = SendMessageCommandHandler(
            conversation_repository, domain_service
        )
        self._get_conversation_handler = GetConversationQueryHandler(
            conversation_repository
        )
    
    async def start_conversation(
        self, 
        persona_id: str, 
        metadata: Optional[dict] = None
    ) -> StartConversationResult:
        """Start a new conversation."""
        command = StartConversationCommand(
            persona_id=persona_id,
            metadata=metadata
        )
        return await self._start_conversation_handler.handle(command)
    
    async def send_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        audio_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        message_timestamp: Optional[datetime] = None
    ) -> SendMessageResult:
        """Send a message in a conversation."""
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
            message_role = MessageRole(role)
        except (ValueError, TypeError):
            return SendMessageResult(
                message_id=None,
                success=False,
                message="Invalid conversation ID or message role"
            )
        
        command = SendMessageCommand(
            conversation_id=conversation_id_obj,
            role=message_role,
            content=content,
            audio_url=audio_url,
            metadata=metadata,
            message_timestamp=message_timestamp
        )
        return await self._send_message_handler.handle(command)
    
    async def get_conversation(self, conversation_id: str) -> GetConversationResult:
        """Get a conversation by ID."""
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
        except (ValueError, TypeError):
            return GetConversationResult(
                conversation=None,
                success=False,
                message="Invalid conversation ID"
            )
        
        query = GetConversationQuery(conversation_id=conversation_id_obj)
        return await self._get_conversation_handler.handle(query)
    
    async def get_conversations_by_persona(
        self, 
        persona_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[ConversationDto]:
        """Get conversations by persona ID."""
        conversations = await self._conversation_repository.get_by_persona_id(
            persona_id, limit, offset
        )
        
        return [
            ConversationDto(
                id=str(conv.id.value),
                persona_id=conv.persona_id,
                status=conv.status.value,
                started_at=conv.started_at,
                ended_at=conv.ended_at,
                duration_seconds=conv.duration_seconds,
                messages=[
                    MessageDto(
                        id=str(msg.id),
                        conversation_id=str(msg.conversation_id),
                        role=msg.role.value,
                        content=msg.content.text,
                        audio_url=msg.audio_url,
                        timestamp=msg.timestamp,
                        metadata=msg.metadata
                    )
                    for msg in conv.messages
                ],
                metadata=conv.metadata,
                created_at=conv.started_at or conv.started_at,
                updated_at=conv.ended_at or conv.started_at
            )
            for conv in conversations
        ]
    
    async def complete_conversation(self, conversation_id: str) -> bool:
        """Complete a conversation."""
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
            conversation = await self._conversation_repository.get_by_id(conversation_id_obj)
            
            if not conversation:
                return False
            
            if not self._domain_service.can_complete_conversation(conversation):
                return False
            
            conversation.complete()
            await self._conversation_repository.save(conversation)
            return True
        
        except Exception:
            return False
    
    async def get_conversation_metrics(self, conversation_id: str) -> Optional[dict]:
        """Get conversation metrics."""
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
            conversation = await self._conversation_repository.get_by_id(conversation_id_obj)
            
            if not conversation:
                return None
            
            return self._domain_service.get_conversation_metrics(conversation)
        
        except Exception:
            return None
