"""
Query handlers for conversation bounded context.
"""
from src.conversation.application.queries.get_conversation import (
    GetConversationQuery, 
    GetConversationResult, 
    ConversationDto, 
    MessageDto
)
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.domain.exceptions import ConversationNotFoundError


class GetConversationQueryHandler:
    """Handler for get conversation query."""
    
    def __init__(self, conversation_repository: IConversationRepository):
        self._conversation_repository = conversation_repository
    
    async def handle(self, query: GetConversationQuery) -> GetConversationResult:
        """Handle get conversation query."""
        try:
            # Get conversation
            conversation = await self._conversation_repository.get_by_id(query.conversation_id)
            if not conversation:
                return GetConversationResult(
                    conversation=None,
                    success=False,
                    message="Conversation not found"
                )
            
            # Convert to DTO
            conversation_dto = ConversationDto(
                id=str(conversation.id.value),
                persona_id=conversation.persona_id,
                status=conversation.status.value,
                started_at=conversation.started_at,
                ended_at=conversation.ended_at,
                duration_seconds=conversation.duration_seconds,
                messages=[
                    MessageDto(
                        id=str(message.id),
                        conversation_id=str(message.conversation_id),
                        role=message.role.value,
                        content=message.content.text,
                        audio_url=message.audio_url,
                        timestamp=message.timestamp,
                        metadata=message.metadata
                    )
                    for message in conversation.messages
                ],
                metadata=conversation.metadata,
                created_at=conversation.started_at or conversation.started_at,
                updated_at=conversation.ended_at or conversation.started_at
            )
            
            return GetConversationResult(
                conversation=conversation_dto,
                success=True,
                message="Conversation retrieved successfully"
            )
        
        except Exception as e:
            return GetConversationResult(
                conversation=None,
                success=False,
                message=f"Failed to get conversation: {str(e)}"
            )
