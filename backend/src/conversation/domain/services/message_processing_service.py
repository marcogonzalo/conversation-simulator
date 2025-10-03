"""
Message processing service for intelligent text aggregation and conversation management.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.conversation.domain.entities.enhanced_message import (
    EnhancedMessage, 
    TextChunk, 
    AudioMetadata, 
    MessageType, 
    ProcessingStatus
)


class MessageProcessingService:
    """Service for processing and aggregating messages intelligently."""
    
    def __init__(self, chunk_timeout_seconds: int = 3):
        self._chunk_timeout_seconds = chunk_timeout_seconds
        self._pending_messages: Dict[str, EnhancedMessage] = {}
    
    def process_text_chunk(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        is_final: bool = False,
        confidence: Optional[float] = None,
        message_group_id: Optional[str] = None
    ) -> EnhancedMessage:
        """
        Process a text chunk and return the updated message.
        
        Args:
            conversation_id: The conversation ID
            role: Message role ('user' or 'assistant')
            content: Text content
            is_final: Whether this is the final chunk for the message
            confidence: Transcription confidence score
            message_group_id: Optional group ID to link chunks
        
        Returns:
            The updated or created message
        """
        # Create a key for grouping chunks
        message_key = self._get_message_key(conversation_id, role, message_group_id)
        
        # Use a more specific key for chunk grouping
        chunk_key = f"{conversation_id}_{role}"
        if message_group_id:
            chunk_key = f"{conversation_id}_{role}_{message_group_id}"
        
        if chunk_key in self._pending_messages:
            # Add chunk to existing message
            message = self._pending_messages[chunk_key]
            message.add_text_chunk(content, is_final, confidence)
            
            if is_final:
                # Remove from pending when final
                del self._pending_messages[chunk_key]
            
            return message
        else:
            # Create new message
            message = EnhancedMessage.create_user_message(
                conversation_id=conversation_id,
                message_type=MessageType.TEXT
            ) if role == "user" else EnhancedMessage.create_assistant_message(
                conversation_id=conversation_id,
                message_type=MessageType.TEXT
            )
            
            # Set the correct role
            message._role = role
            
            # Add the chunk
            message.add_text_chunk(content, is_final, confidence)
            
            if not is_final:
                # Keep in pending for more chunks
                self._pending_messages[chunk_key] = message
            
            return message
    
    def process_audio_message(
        self,
        conversation_id: UUID,
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
            audio_format: Audio format (webm, wav, etc.)
            duration_ms: Audio duration in milliseconds
            transcription: Optional transcription text
            confidence: Transcription confidence score
        
        Returns:
            The created message
        """
        # Create audio metadata
        audio_metadata = AudioMetadata(
            duration_ms=duration_ms,
            format=audio_format,
            processing_time_ms=None  # Could be calculated if needed
        )
        
        # Determine message type
        message_type = MessageType.AUDIO if not transcription else MessageType.MIXED
        
        # Create message
        if role == "user":
            message = EnhancedMessage.create_user_message(
                conversation_id=conversation_id,
                message_type=message_type,
                audio_url=None,  # Will be set later when file is saved
                audio_metadata=audio_metadata
            )
        else:
            message = EnhancedMessage.create_assistant_message(
                conversation_id=conversation_id,
                message_type=message_type,
                audio_url=None,  # Will be set later when file is saved
                audio_metadata=audio_metadata
            )
        
        # Set the correct role
        message._role = role
        
        # Add transcription if available
        if transcription:
            message.add_text_chunk(transcription, is_final=True, confidence=confidence)
        
        # Store audio data in metadata temporarily
        message.update_metadata('audio_data', audio_data)
        message.update_metadata('audio_format', audio_format)
        
        return message
    
    def finalize_message(self, message: EnhancedMessage) -> EnhancedMessage:
        """
        Finalize a message and ensure all chunks are processed.
        
        Args:
            message: The message to finalize
        
        Returns:
            The finalized message
        """
        if not message.has_final_content() and message.text_chunks:
            # Process remaining chunks
            message.set_processed_content(message._process_text_chunks(), is_final=True)
        
        message.set_processing_status(ProcessingStatus.COMPLETED)
        return message
    
    def get_pending_messages(self, conversation_id: UUID) -> List[EnhancedMessage]:
        """
        Get all pending messages for a conversation.
        
        Args:
            conversation_id: The conversation ID
        
        Returns:
            List of pending messages
        """
        pending = []
        conversation_key = str(conversation_id)
        
        for key, message in self._pending_messages.items():
            if key.startswith(conversation_key):
                pending.append(message)
        
        return pending
    
    def cleanup_expired_messages(self, max_age_seconds: int = 300) -> List[EnhancedMessage]:
        """
        Clean up expired pending messages.
        
        Args:
            max_age_seconds: Maximum age for pending messages
        
        Returns:
            List of cleaned up messages
        """
        expired_messages = []
        cutoff_time = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        
        expired_keys = []
        for key, message in self._pending_messages.items():
            if message.timestamp < cutoff_time:
                expired_messages.append(message)
                expired_keys.append(key)
        
        # Remove expired messages
        for key in expired_keys:
            del self._pending_messages[key]
        
        return expired_messages
    
    def merge_messages(self, messages: List[EnhancedMessage]) -> List[EnhancedMessage]:
        """
        Merge consecutive messages from the same role with short time gaps.
        
        Args:
            messages: List of messages to potentially merge
        
        Returns:
            List of merged messages
        """
        if not messages:
            return []
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda m: m.timestamp)
        merged = []
        current_message = None
        
        for message in sorted_messages:
            if current_message is None:
                current_message = message
                continue
            
            # Check if messages should be merged
            time_diff = message.timestamp - current_message.timestamp
            should_merge = (
                current_message.role == message.role and
                time_diff.total_seconds() <= self._chunk_timeout_seconds and
                not current_message.has_final_content() and
                not message.has_final_content()
            )
            
            if should_merge:
                # Merge chunks from the new message into current
                for chunk in message.text_chunks:
                    current_message.add_text_chunk(
                        chunk.content,
                        chunk.is_final,
                        chunk.confidence
                    )
                
                # Update timestamps and metadata
                if message.timestamp > current_message.timestamp:
                    current_message._timestamp = message.timestamp
                
                # Merge metadata
                for key, value in message.metadata.items():
                    current_message.update_metadata(key, value)
            else:
                # Finalize current message and start new one
                if current_message:
                    self.finalize_message(current_message)
                    merged.append(current_message)
                
                current_message = message
        
        # Add the last message
        if current_message:
            self.finalize_message(current_message)
            merged.append(current_message)
        
        return merged
    
    def _get_message_key(self, conversation_id: UUID, role: str, message_group_id: Optional[str] = None) -> str:
        """Generate a key for grouping message chunks."""
        if message_group_id:
            return f"{conversation_id}_{role}_{message_group_id}"
        else:
            return f"{conversation_id}_{role}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def get_conversation_summary(self, messages: List[EnhancedMessage]) -> Dict[str, Any]:
        """
        Generate a summary of conversation messages.
        
        Args:
            messages: List of messages in the conversation
        
        Returns:
            Summary dictionary with statistics
        """
        if not messages:
            return {
                'total_messages': 0,
                'user_messages': 0,
                'assistant_messages': 0,
                'audio_messages': 0,
                'total_duration_ms': 0,
                'average_confidence': 0.0
            }
        
        user_messages = sum(1 for m in messages if m.is_user_message())
        assistant_messages = sum(1 for m in messages if m.is_assistant_message())
        audio_messages = sum(1 for m in messages if m.has_audio())
        
        total_duration = sum(
            m.audio_metadata.duration_ms or 0 
            for m in messages 
            if m.audio_metadata and m.audio_metadata.duration_ms
        )
        
        # Calculate average confidence from chunks
        all_confidences = []
        for message in messages:
            for chunk in message.text_chunks:
                if chunk.confidence is not None:
                    all_confidences.append(chunk.confidence)
        
        average_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return {
            'total_messages': len(messages),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'audio_messages': audio_messages,
            'total_duration_ms': total_duration,
            'average_confidence': average_confidence,
            'conversation_start': messages[0].timestamp if messages else None,
            'conversation_end': messages[-1].timestamp if messages else None
        }
