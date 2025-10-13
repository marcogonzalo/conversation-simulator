"""
Conversation domain service.
"""
from typing import List, Optional
from uuid import UUID

from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.transcription import Transcription, TranscriptionStatus
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
        if not conversation.has_transcription():
            return False
        
        transcription = conversation.transcription
        if not transcription.can_add_message():
            return False
        
        # Business rule: Cannot add system messages to completed conversations
        if conversation.is_completed() and role == MessageRole.SYSTEM:
            return False
        
        return True
    
    def can_complete_conversation(self, conversation: Conversation) -> bool:
        """Check if a conversation can be completed."""
        if not conversation.has_transcription():
            return False
        
        transcription = conversation.transcription
        # Business rule: Must have at least one message to complete
        if len(transcription.messages) == 0:
            return False
        
        # Business rule: Must be in active state and transcription completed
        return conversation.status == ConversationStatus.ACTIVE and transcription.is_completed()
    
    def should_auto_complete(self, conversation: Conversation, max_duration_minutes: int = 20) -> bool:
        """Check if conversation should be auto-completed."""
        if not conversation.has_transcription() or not conversation.transcription.started_at:
            return False
        
        duration_minutes = (conversation.transcription.started_at - conversation.transcription.started_at).total_seconds() / 60
        return duration_minutes >= max_duration_minutes
    
    def get_conversation_summary(self, conversation: Conversation) -> dict:
        """Get a summary of the conversation."""
        if not conversation.has_transcription():
            return {
                'total_messages': 0,
                'user_messages': 0,
                'ai_messages': 0,
                'duration_seconds': 0,
                'status': conversation.status.value,
                'has_audio': False
            }
        
        transcription = conversation.transcription
        user_messages = [m for m in transcription.messages if m.role == MessageRole.USER]
        ai_messages = [m for m in transcription.messages if m.role == MessageRole.ASSISTANT]
        
        return {
            'total_messages': len(transcription.messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'duration_seconds': conversation.duration_seconds,
            'status': conversation.status.value,
            'has_audio': any(m.has_audio() for m in transcription.messages)
        }
    
    def validate_message_content(self, content: str) -> bool:
        """Validate message content."""
        if not content or not content.strip():
            return False
        
        if len(content) > 10000:
            return False
        
        return True
    
    def get_conversation_metrics(self, conversation: Conversation, messages: Optional[List[dict]] = None) -> dict:
        """Get conversation metrics for analysis."""
        if not conversation.has_transcription():
            return {}
        
        # If no messages provided, return basic metrics
        if not messages:
            return {
                'message_count': 0,
                'user_message_count': 0,
                'ai_message_count': 0,
                'total_words': 0,
                'user_words': 0,
                'ai_words': 0,
                'average_message_length': 0,
                'user_speak_ratio': 0,
                'duration_seconds': conversation.duration_seconds or 0,
                'messages_per_minute': 0
            }
        
        # Process messages from dictionary format
        user_messages = [m for m in messages if m.get('role') == 'user']
        ai_messages = [m for m in messages if m.get('role') == 'assistant']
        
        total_words = sum(len(m.get('content', '').split()) for m in messages)
        user_words = sum(len(m.get('content', '').split()) for m in user_messages)
        ai_words = sum(len(m.get('content', '').split()) for m in ai_messages)
        
        return {
            'message_count': len(messages),
            'user_message_count': len(user_messages),
            'ai_message_count': len(ai_messages),
            'total_words': total_words,
            'user_words': user_words,
            'ai_words': ai_words,
            'average_message_length': total_words / len(messages) if messages else 0,
            'user_speak_ratio': user_words / total_words if total_words > 0 else 0,
            'duration_seconds': conversation.duration_seconds or 0,
            'messages_per_minute': len(messages) / (conversation.duration_seconds / 60) if conversation.duration_seconds and conversation.duration_seconds > 0 else 0
        }
