"""
Enhanced conversation application service with intelligent message processing.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.entities.enhanced_message import EnhancedMessage, MessageType
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.services.message_processing_service import MessageProcessingService
from src.conversation.infrastructure.repositories.enhanced_conversation_repository import EnhancedConversationRepository
from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository


class EnhancedConversationService:
    """
    Enhanced conversation service with intelligent message processing capabilities.
    """
    
    def __init__(
        self,
        conversation_repository: SQLConversationRepository,
        enhanced_repository: EnhancedConversationRepository
    ):
        self.conversation_repository = conversation_repository
        self.enhanced_repository = enhanced_repository
        self.message_processor = MessageProcessingService()
    
    async def process_text_chunk(
        self,
        conversation_id: ConversationId,
        role: str,
        content: str,
        is_final: bool = False,
        confidence: Optional[float] = None,
        message_group_id: Optional[str] = None
    ) -> EnhancedMessage:
        """
        Process a text chunk and store it in the conversation.
        
        Args:
            conversation_id: The conversation ID
            role: Message role ('user' or 'assistant')
            content: Text content
            is_final: Whether this is the final chunk
            confidence: Transcription confidence
            message_group_id: Optional group ID for chunk linking
        
        Returns:
            The processed message
        """
        # Process the chunk
        message = self.message_processor.process_text_chunk(
            conversation_id=conversation_id,
            role=role,
            content=content,
            is_final=is_final,
            confidence=confidence,
            message_group_id=message_group_id
        )
        
        # Save to enhanced repository
        await self.enhanced_repository.add_enhanced_message(conversation_id, message)
        
        return message
    
    async def process_audio_message(
        self,
        conversation_id: ConversationId,
        role: str,
        audio_data: str,
        audio_format: str = "webm",
        duration_ms: Optional[int] = None,
        transcription: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> EnhancedMessage:
        """
        Process an audio message with optional transcription.
        
        Args:
            conversation_id: The conversation ID
            role: Message role ('user' or 'assistant')
            audio_data: Base64 encoded audio data
            audio_format: Audio format
            duration_ms: Audio duration
            transcription: Optional transcription
            confidence: Transcription confidence
        
        Returns:
            The processed message
        """
        # Process the audio message
        message = self.message_processor.process_audio_message(
            conversation_id=conversation_id,
            role=role,
            audio_data=audio_data,
            audio_format=audio_format,
            duration_ms=duration_ms,
            transcription=transcription,
            confidence=confidence
        )
        
        # Save to enhanced repository
        await self.enhanced_repository.add_enhanced_message(conversation_id, message)
        
        return message
    
    async def finalize_message(self, conversation_id: ConversationId, message_id: UUID) -> bool:
        """
        Finalize a message and ensure all chunks are processed.
        
        Args:
            conversation_id: The conversation ID
            message_id: The message ID to finalize
        
        Returns:
            True if successful, False otherwise
        """
        # Get the message
        messages = await self.enhanced_repository.get_enhanced_messages(conversation_id)
        
        for message in messages:
            if message.id == message_id:
                # Finalize the message
                self.message_processor.finalize_message(message)
                
                # Save updated conversation
                await self.enhanced_repository.save_enhanced_conversation(conversation_id, messages)
                return True
        
        return False
    
    async def get_enhanced_conversation(self, conversation_id: ConversationId) -> Optional[Dict[str, Any]]:
        """
        Get a conversation with enhanced message processing.
        
        Args:
            conversation_id: The conversation ID
        
        Returns:
            Enhanced conversation data or None
        """
        return await self.enhanced_repository.get_enhanced_conversation(conversation_id)
    
    async def get_enhanced_messages(self, conversation_id: ConversationId) -> List[EnhancedMessage]:
        """
        Get enhanced messages for a conversation.
        
        Args:
            conversation_id: The conversation ID
        
        Returns:
            List of enhanced messages
        """
        return await self.enhanced_repository.get_enhanced_messages(conversation_id)
    
    async def merge_conversation_chunks(self, conversation_id: ConversationId) -> None:
        """
        Merge message chunks in a conversation for better readability.
        
        Args:
            conversation_id: The conversation ID
        """
        await self.enhanced_repository.merge_message_chunks(conversation_id)
    
    async def get_conversation_statistics(self, conversation_id: ConversationId) -> Optional[Dict[str, Any]]:
        """
        Get conversation statistics.
        
        Args:
            conversation_id: The conversation ID
        
        Returns:
            Statistics dictionary or None
        """
        return await self.enhanced_repository.get_conversation_statistics(conversation_id)
    
    async def update_message_content(
        self, 
        conversation_id: ConversationId, 
        message_id: UUID, 
        content: str
    ) -> bool:
        """
        Update the content of a specific message.
        
        Args:
            conversation_id: The conversation ID
            message_id: The message ID
            content: New content
        
        Returns:
            True if successful, False otherwise
        """
        return await self.enhanced_repository.update_message_content(conversation_id, message_id, content)
    
    async def get_enhanced_conversations_by_persona(
        self, 
        persona_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get enhanced conversations by persona ID.
        
        Args:
            persona_id: The persona ID
            limit: Maximum number of conversations
            offset: Number of conversations to skip
        
        Returns:
            List of enhanced conversation data
        """
        return await self.enhanced_repository.get_enhanced_conversations_by_persona(persona_id, limit, offset)
    
    async def cleanup_expired_messages(self, max_age_seconds: int = 300) -> List[EnhancedMessage]:
        """
        Clean up expired pending messages.
        
        Args:
            max_age_seconds: Maximum age for pending messages
        
        Returns:
            List of cleaned up messages
        """
        return self.message_processor.cleanup_expired_messages(max_age_seconds)
    
    async def get_conversation_summary(self, conversation_id: ConversationId) -> Optional[Dict[str, Any]]:
        """
        Get a comprehensive summary of the conversation.
        
        Args:
            conversation_id: The conversation ID
        
        Returns:
            Summary dictionary or None
        """
        messages = await self.get_enhanced_messages(conversation_id)
        
        if not messages:
            return None
        
        # Get basic statistics
        stats = self.message_processor.get_conversation_summary(messages)
        
        # Add additional analysis
        user_messages = [m for m in messages if m.is_user_message()]
        assistant_messages = [m for m in messages if m.is_assistant_message()]
        
        # Calculate response times
        response_times = []
        for i in range(len(messages) - 1):
            if (messages[i].is_user_message() and 
                messages[i + 1].is_assistant_message()):
                response_time = (messages[i + 1].timestamp - messages[i].timestamp).total_seconds()
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Get conversation duration
        conversation_duration = 0
        if messages:
            conversation_duration = (messages[-1].timestamp - messages[0].timestamp).total_seconds()
        
        return {
            **stats,
            'conversation_duration_seconds': conversation_duration,
            'average_response_time_seconds': avg_response_time,
            'total_response_times': len(response_times),
            'message_types': {
                'text_only': len([m for m in messages if m.message_type == MessageType.TEXT]),
                'audio_only': len([m for m in messages if m.message_type == MessageType.AUDIO]),
                'mixed': len([m for m in messages if m.message_type == MessageType.MIXED])
            },
            'processing_status': {
                'completed': len([m for m in messages if m.processing_status.value == 'completed']),
                'pending': len([m for m in messages if m.processing_status.value == 'pending']),
                'processing': len([m for m in messages if m.processing_status.value == 'processing']),
                'failed': len([m for m in messages if m.processing_status.value == 'failed'])
            }
        }
    
    async def export_conversation_for_analysis(self, conversation_id: ConversationId) -> Optional[Dict[str, Any]]:
        """
        Export conversation data in a format suitable for analysis.
        
        Args:
            conversation_id: The conversation ID
        
        Returns:
            Export data dictionary or None
        """
        enhanced_data = await self.get_enhanced_conversation(conversation_id)
        
        if not enhanced_data:
            return None
        
        # Get original conversation for additional context
        original_conversation = await self.conversation_repository.get_by_id(conversation_id)
        
        # Format messages for analysis
        analysis_messages = []
        for message_data in enhanced_data.get('messages', []):
            analysis_message = {
                'role': message_data['role'],
                'content': message_data.get('processed_content', ''),
                'timestamp': message_data['timestamp'],
                'message_type': message_data['message_type'],
                'has_audio': bool(message_data.get('audio_url')),
                'audio_duration_ms': None,
                'confidence_scores': []
            }
            
            # Add audio metadata
            if message_data.get('audio_metadata'):
                analysis_message['audio_duration_ms'] = message_data['audio_metadata'].get('duration_ms')
            
            # Add confidence scores from chunks
            for chunk in message_data.get('text_chunks', []):
                if chunk.get('confidence') is not None:
                    analysis_message['confidence_scores'].append(chunk['confidence'])
            
            analysis_messages.append(analysis_message)
        
        return {
            'conversation_id': str(conversation_id.value),
            'persona_id': original_conversation.persona_id if original_conversation else None,
            'status': original_conversation.status.value if original_conversation else None,
            'started_at': enhanced_data.get('created_at'),
            'ended_at': original_conversation.ended_at.isoformat() if original_conversation and original_conversation.ended_at else None,
            'messages': analysis_messages,
            'summary': enhanced_data.get('summary', {}),
            'statistics': await self.get_conversation_summary(conversation_id)
        }
