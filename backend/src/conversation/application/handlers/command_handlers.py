"""
Command handlers for conversation bounded context.
"""
from typing import List
from uuid import uuid4

from src.conversation.application.commands.start_conversation import StartConversationCommand, StartConversationResult
from src.conversation.application.commands.send_message import SendMessageCommand, SendMessageResult
from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.message import Message, MessageRole
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.value_objects.message_content import MessageContent
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.domain.exceptions import ConversationNotFoundError, ConversationStateError


class StartConversationCommandHandler:
    """Handler for start conversation command."""
    
    def __init__(
        self,
        conversation_repository: IConversationRepository,
        domain_service: ConversationDomainService
    ):
        self._conversation_repository = conversation_repository
        self._domain_service = domain_service
    
    async def handle(self, command: StartConversationCommand) -> StartConversationResult:
        """Handle start conversation command."""
        try:
            # Validate business rules
            if not self._domain_service.can_start_conversation(command.persona_id):
                return StartConversationResult(
                    conversation_id=None,
                    success=False,
                    message="Cannot start conversation for this persona"
                )
            
            # Create conversation
            conversation_id = ConversationId.generate()
            conversation = Conversation(
                conversation_id=conversation_id,
                persona_id=command.persona_id,
                status=ConversationStatus.PENDING,
                metadata=command.metadata
            )
            
            # Start conversation
            conversation.start()
            
            # Save conversation
            await self._conversation_repository.save(conversation)
            
            return StartConversationResult(
                conversation_id=conversation_id,
                success=True,
                message="Conversation started successfully"
            )
        
        except Exception as e:
            return StartConversationResult(
                conversation_id=None,
                success=False,
                message=f"Failed to start conversation: {str(e)}"
            )


class SendMessageCommandHandler:
    """Handler for send message command."""
    
    def __init__(
        self,
        conversation_repository: IConversationRepository,
        domain_service: ConversationDomainService
    ):
        self._conversation_repository = conversation_repository
        self._domain_service = domain_service
    
    async def handle(self, command: SendMessageCommand) -> SendMessageResult:
        """Handle send message command."""
        try:
            # Get conversation
            conversation = await self._conversation_repository.get_by_id(command.conversation_id)
            if not conversation:
                return SendMessageResult(
                    message_id=None,
                    success=False,
                    message="Conversation not found"
                )
            
            # Validate business rules
            if not self._domain_service.can_add_message(conversation, command.role):
                return SendMessageResult(
                    message_id=None,
                    success=False,
                    message="Cannot add message to this conversation"
                )
            
            # Validate content
            if not self._domain_service.validate_message_content(command.content):
                return SendMessageResult(
                    message_id=None,
                    success=False,
                    message="Invalid message content"
                )
            
            # Create message
            message = Message.create_user_message(
                conversation_id=command.conversation_id.value,
                content=command.content,
                audio_url=command.audio_url,
                timestamp=command.message_timestamp
            ) if command.role.value == MessageRole.USER.value else Message.create_assistant_message(
                conversation_id=command.conversation_id.value,
                content=command.content,
                audio_url=command.audio_url,
                timestamp=command.message_timestamp
            )
            
            # Add message to conversation
            conversation.add_message(message)
            
            # Save conversation
            await self._conversation_repository.save(conversation)
            
            return SendMessageResult(
                message_id=message.id,
                success=True,
                message="Message sent successfully"
            )
        
        except Exception as e:
            return SendMessageResult(
                message_id=None,
                success=False,
                message=f"Failed to send message: {str(e)}"
            )
