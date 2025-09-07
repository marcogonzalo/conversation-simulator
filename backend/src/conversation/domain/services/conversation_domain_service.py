"""
Conversation domain service.
"""
from typing import List, Optional
from uuid import UUID

from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.message import Message, MessageRole
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.value_objects.message_content import MessageContent
from src.conversation.domain.exceptions import ConversationNotFoundError, ConversationStateError


class ConversationDomainService:
    """Domain service for conversation business logic."""
    
    def can_start_conversation(self, persona_id: str) -> bool:
        """Check if a conversation can be started for a persona."""
        # Business rule: Persona must exist and be active
        return bool(persona_id and persona_id.strip())
    
    def can_add_message(self, conversation: Conversation, role: MessageRole) -> bool:
        """Check if a message can be added to the conversation."""
        if not conversation.can_add_message():
            return False
        
        # Business rule: Cannot add system messages to completed conversations
        if conversation.is_completed() and role == MessageRole.SYSTEM:
            return False
        
        return True
    
    def can_complete_conversation(self, conversation: Conversation) -> bool:
        """Check if a conversation can be completed."""
        # Business rule: Must have at least one message to complete
        if len(conversation.messages) == 0:
            return False
        
        # Business rule: Must be in active or paused state
        return conversation.status in [ConversationStatus.ACTIVE, ConversationStatus.PAUSED]
    
    def should_auto_complete(self, conversation: Conversation, max_duration_minutes: int = 20) -> bool:
        """Check if conversation should be auto-completed."""
        if not conversation.started_at:
            return False
        
        duration_minutes = (conversation.started_at - conversation.started_at).total_seconds() / 60
        return duration_minutes >= max_duration_minutes
    
    def get_conversation_summary(self, conversation: Conversation) -> dict:
        """Get a summary of the conversation."""
        user_messages = [m for m in conversation.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in conversation.messages if m.role == MessageRole.ASSISTANT]
        
        return {
            'total_messages': len(conversation.messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'duration_seconds': conversation.duration_seconds,
            'status': conversation.status.value,
            'has_audio': any(m.has_audio() for m in conversation.messages)
        }
    
    def validate_message_content(self, content: str) -> bool:
        """Validate message content."""
        if not content or not content.strip():
            return False
        
        if len(content) > 10000:
            return False
        
        return True
    
    def get_conversation_metrics(self, conversation: Conversation) -> dict:
        """Get conversation metrics for analysis."""
        if not conversation.messages:
            return {}
        
        user_messages = [m for m in conversation.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in conversation.messages if m.role == MessageRole.ASSISTANT]
        
        total_words = sum(len(m.content.text.split()) for m in conversation.messages)
        user_words = sum(len(m.content.text.split()) for m in user_messages)
        assistant_words = sum(len(m.content.text.split()) for m in assistant_messages)
        
        return {
            'message_count': len(conversation.messages),
            'user_message_count': len(user_messages),
            'assistant_message_count': len(assistant_messages),
            'total_words': total_words,
            'user_words': user_words,
            'assistant_words': assistant_words,
            'average_message_length': total_words / len(conversation.messages) if conversation.messages else 0,
            'user_speak_ratio': user_words / total_words if total_words > 0 else 0,
            'duration_seconds': conversation.duration_seconds or 0,
            'messages_per_minute': len(conversation.messages) / (conversation.duration_seconds / 60) if conversation.duration_seconds else 0
        }
