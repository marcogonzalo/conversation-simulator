"""
Enhanced conversation repository with improved message storage and retrieval.
"""
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.enhanced_message import EnhancedMessage
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.domain.services.message_processing_service import MessageProcessingService


class EnhancedConversationRepository(IConversationRepository):
    """
    Enhanced conversation repository with intelligent message processing.
    """
    
    def __init__(self, conversations_dir: str = "data/conversations", enhanced_dir: str = "data/enhanced_conversations"):
        self.conversations_dir = Path(conversations_dir)
        self.enhanced_dir = Path(enhanced_dir)
        self.message_processor = MessageProcessingService()
        
        # Create directories if they don't exist
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.enhanced_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, conversation: Conversation) -> None:
        """Save a conversation with enhanced message processing."""
        # Save original conversation format for backward compatibility
        conversation_data = self._conversation_to_dict(conversation)
        conversation_file = self.conversations_dir / f"{conversation.id.value}.json"
        
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, default=str, indent=2)
        
        # Save enhanced format
        enhanced_data = self._conversation_to_enhanced_dict(conversation)
        enhanced_file = self.enhanced_dir / f"{conversation.id.value}.json"
        
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, default=str, indent=2)
    
    async def save_enhanced_conversation(self, conversation_id: ConversationId, messages: List[EnhancedMessage]) -> None:
        """Save a conversation with enhanced messages."""
        enhanced_data = {
            'conversation_id': str(conversation_id.value),
            'messages': [message.to_dict() for message in messages],
            'summary': self.message_processor.get_conversation_summary(messages),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        enhanced_file = self.enhanced_dir / f"{conversation_id.value}.json"
        
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, default=str, indent=2)
    
    async def get_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """Get conversation by ID (original format)."""
        conversation_file = self.conversations_dir / f"{conversation_id.value}.json"
        
        if not conversation_file.exists():
            return None
        
        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
                return self._dict_to_conversation(conversation_data)
        except Exception as e:
            # Log error but don't print to console
            return None
    
    async def get_enhanced_conversation(self, conversation_id: ConversationId) -> Optional[Dict[str, Any]]:
        """Get conversation with enhanced messages."""
        enhanced_file = self.enhanced_dir / f"{conversation_id.value}.json"
        
        if not enhanced_file.exists():
            return None
        
        try:
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # Log error but don't print to console
            return None
    
    async def get_enhanced_messages(self, conversation_id: ConversationId) -> List[EnhancedMessage]:
        """Get enhanced messages for a conversation."""
        enhanced_data = await self.get_enhanced_conversation(conversation_id)
        
        if not enhanced_data or 'messages' not in enhanced_data:
            return []
        
        messages = []
        for message_data in enhanced_data['messages']:
            try:
                message = EnhancedMessage.from_dict(message_data)
                messages.append(message)
            except Exception as e:
                # Log error but don't print to console
                continue
        
        return messages
    
    async def add_enhanced_message(self, conversation_id: ConversationId, message: EnhancedMessage) -> None:
        """Add an enhanced message to a conversation."""
        # Get existing messages
        existing_messages = await self.get_enhanced_messages(conversation_id)
        
        # Add new message
        existing_messages.append(message)
        
        # Save updated conversation
        await self.save_enhanced_conversation(conversation_id, existing_messages)
    
    async def update_message_content(self, conversation_id: ConversationId, message_id: UUID, content: str) -> bool:
        """Update the content of a specific message."""
        messages = await self.get_enhanced_messages(conversation_id)
        
        for message in messages:
            if message.id == message_id:
                message.set_processed_content(content, is_final=True)
                await self.save_enhanced_conversation(conversation_id, messages)
                return True
        
        return False
    
    async def merge_message_chunks(self, conversation_id: ConversationId) -> None:
        """Merge message chunks in a conversation for better readability."""
        messages = await self.get_enhanced_messages(conversation_id)
        
        if not messages:
            return
        
        # Use message processor to merge chunks
        merged_messages = self.message_processor.merge_messages(messages)
        
        # Save merged messages
        await self.save_enhanced_conversation(conversation_id, merged_messages)
    
    async def get_conversation_statistics(self, conversation_id: ConversationId) -> Optional[Dict[str, Any]]:
        """Get conversation statistics."""
        enhanced_data = await self.get_enhanced_conversation(conversation_id)
        
        if not enhanced_data:
            return None
        
        return enhanced_data.get('summary', {})
    
    async def get_by_persona_id(self, persona_id: str, limit: int = 100, offset: int = 0) -> List[Conversation]:
        """Get conversations by persona ID (original format)."""
        conversations = []
        
        for conversation_file in self.conversations_dir.glob("*.json"):
            try:
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                    
                    if conversation_data.get('persona_id') == persona_id:
                        conversation = self._dict_to_conversation(conversation_data)
                        if conversation:
                            conversations.append(conversation)
            except Exception as e:
                # Log error but don't print to console
                continue
        
        # Sort by started_at timestamp
        conversations.sort(key=lambda c: c.started_at or datetime.min, reverse=True)
        
        # Apply pagination
        return conversations[offset:offset + limit]
    
    async def get_enhanced_conversations_by_persona(self, persona_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get enhanced conversations by persona ID."""
        conversations = []
        
        for enhanced_file in self.enhanced_dir.glob("*.json"):
            try:
                with open(enhanced_file, 'r', encoding='utf-8') as f:
                    enhanced_data = json.load(f)
                    
                    # Check if this conversation belongs to the persona
                    # We need to get the original conversation to check persona_id
                    conversation_id = ConversationId(UUID(enhanced_data['conversation_id']))
                    original_conversation = await self.get_by_id(conversation_id)
                    
                    if original_conversation and original_conversation.persona_id == persona_id:
                        conversations.append(enhanced_data)
            except Exception as e:
                # Log error but don't print to console
                continue
        
        # Sort by created_at timestamp
        conversations.sort(key=lambda c: c.get('created_at', ''), reverse=True)
        
        # Apply pagination
        return conversations[offset:offset + limit]
    
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if conversation exists."""
        conversation_file = self.conversations_dir / f"{conversation_id.value}.json"
        return conversation_file.exists()
    
    async def delete(self, conversation_id: ConversationId) -> bool:
        """Delete a conversation and its enhanced version."""
        deleted = False
        
        # Delete original conversation
        conversation_file = self.conversations_dir / f"{conversation_id.value}.json"
        if conversation_file.exists():
            conversation_file.unlink()
            deleted = True
        
        # Delete enhanced conversation
        enhanced_file = self.enhanced_dir / f"{conversation_id.value}.json"
        if enhanced_file.exists():
            enhanced_file.unlink()
            deleted = True
        
        return deleted
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Conversation]:
        """Get all conversations (original format)."""
        conversations = []
        
        for conversation_file in self.conversations_dir.glob("*.json"):
            try:
                with open(conversation_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                    conversation = self._dict_to_conversation(conversation_data)
                    if conversation:
                        conversations.append(conversation)
            except Exception as e:
                # Log error but don't print to console
                continue
        
        # Sort by started_at timestamp
        conversations.sort(key=lambda c: c.started_at or datetime.min, reverse=True)
        
        # Apply pagination
        return conversations[offset:offset + limit]
    
    def _conversation_to_dict(self, conversation: Conversation) -> Dict[str, Any]:
        """Convert conversation entity to dictionary (original format)."""
        return {
            'id': str(conversation.id.value),
            'persona_id': conversation.persona_id,
            'status': conversation.status.value,
            'started_at': conversation.started_at.isoformat() if conversation.started_at else None,
            'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None,
            'messages': [
                {
                    'id': str(message.id),
                    'conversation_id': str(message.conversation_id),
                    'role': message.role.value,
                    'content': message.content.text,
                    'audio_url': message.audio_url,
                    'timestamp': message.timestamp.isoformat(),
                    'metadata': message.metadata
                }
                for message in conversation.messages
            ],
            'metadata': conversation.metadata
        }
    
    def _conversation_to_enhanced_dict(self, conversation: Conversation) -> Dict[str, Any]:
        """Convert conversation to enhanced dictionary format."""
        # Convert original messages to enhanced format
        enhanced_messages = []
        
        for message in conversation.messages:
            enhanced_message = EnhancedMessage(
                message_id=message.id,
                conversation_id=message.conversation_id,
                role=message.role.value,
                timestamp=message.timestamp
            )
            
            # Set content
            enhanced_message.set_processed_content(message.content.text, is_final=True)
            
            # Set audio URL if available
            if message.audio_url:
                enhanced_message.add_audio_url(message.audio_url)
            
            # Copy metadata
            for key, value in message.metadata.items():
                enhanced_message.update_metadata(key, value)
            
            enhanced_messages.append(enhanced_message)
        
        return {
            'conversation_id': str(conversation.id.value),
            'persona_id': conversation.persona_id,
            'status': conversation.status.value,
            'started_at': conversation.started_at.isoformat() if conversation.started_at else None,
            'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None,
            'messages': [message.to_dict() for message in enhanced_messages],
            'summary': self.message_processor.get_conversation_summary(enhanced_messages),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'metadata': conversation.metadata
        }
    
    def _dict_to_conversation(self, data: Dict[str, Any]) -> Optional[Conversation]:
        """Convert dictionary to conversation entity (original format)."""
        try:
            from src.conversation.domain.entities.message import Message, MessageRole
            from src.conversation.domain.value_objects.message_content import MessageContent
            
            conversation_id = ConversationId(UUID(data['id']))
            
            conversation = Conversation(
                conversation_id=conversation_id,
                persona_id=data['persona_id'],
                status=ConversationStatus(data['status']),
                started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
                ended_at=datetime.fromisoformat(data['ended_at']) if data.get('ended_at') else None,
                metadata=data.get('metadata', {})
            )
            
            # Add messages
            for message_data in data.get('messages', []):
                message = Message(
                    message_id=UUID(message_data['id']),
                    conversation_id=UUID(message_data['conversation_id']),
                    role=MessageRole(message_data['role']),
                    content=MessageContent(message_data['content']),
                    audio_url=message_data.get('audio_url'),
                    timestamp=datetime.fromisoformat(message_data['timestamp']),
                    metadata=message_data.get('metadata', {})
                )
                conversation._messages.append(message)
            
            return conversation
            
        except Exception as e:
            # Log error but don't print to console
            return None
    
    async def update_status(
        self, 
        conversation_id: ConversationId, 
        status: ConversationStatus, 
        transcription_id: Optional[str] = None, 
        analysis_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """Update conversation status and related fields."""
        try:
            # Get existing conversation
            conversation = await self.get_by_id(conversation_id)
            if not conversation:
                return False
            
            # Update fields
            if transcription_id:
                conversation._transcription_id = transcription_id
            if analysis_id:
                conversation._analysis_id = analysis_id
            if metadata:
                conversation._metadata.update(metadata)
            
            # Update status
            conversation._status = status
            
            # Save updated conversation
            await self.save(conversation)
            return True
            
        except Exception as e:
            return False
