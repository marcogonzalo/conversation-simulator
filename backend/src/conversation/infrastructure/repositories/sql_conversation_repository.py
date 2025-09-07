"""
SQL implementation of conversation repository.
"""
import json
from typing import List, Optional
from pathlib import Path
from uuid import UUID

from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.message import Message, MessageRole
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.value_objects.message_content import MessageContent
from src.conversation.domain.repositories.conversation_repository import ConversationRepository


class SQLConversationRepository(ConversationRepository):
    """SQL implementation of conversation repository."""
    
    def __init__(self, conversations_dir: str = "data/conversations"):
        self.conversations_dir = Path(conversations_dir)
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, conversation: Conversation) -> None:
        """Save a conversation."""
        conversation_data = self._conversation_to_dict(conversation)
        conversation_file = self.conversations_dir / f"{conversation.id.value}.json"
        
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, default=str, indent=2)
    
    async def get_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """Get conversation by ID."""
        conversation_file = self.conversations_dir / f"{conversation_id.value}.json"
        
        if not conversation_file.exists():
            return None
        
        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
                return self._dict_to_conversation(conversation_data)
        except Exception as e:
            print(f"Error loading conversation {conversation_id.value}: {e}")
            return None
    
    async def get_by_persona_id(self, persona_id: str, limit: int = 100, offset: int = 0) -> List[Conversation]:
        """Get conversations by persona ID."""
        all_conversations = await self.get_all(limit=1000, offset=0)
        filtered_conversations = [c for c in all_conversations if c.persona_id == persona_id]
        
        return filtered_conversations[offset:offset + limit]
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Conversation]:
        """Get all conversations with pagination."""
        conversations = []
        
        for json_file in self.conversations_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                    conversation = self._dict_to_conversation(conversation_data)
                    if conversation:
                        conversations.append(conversation)
            except Exception as e:
                print(f"Error loading conversation from {json_file}: {e}")
                continue
        
        # Sort by started_at descending
        conversations.sort(key=lambda x: x.started_at or x.started_at, reverse=True)
        
        return conversations[offset:offset + limit]
    
    async def delete(self, conversation_id: ConversationId) -> bool:
        """Delete a conversation."""
        conversation_file = self.conversations_dir / f"{conversation_id.value}.json"
        
        if conversation_file.exists():
            conversation_file.unlink()
            return True
        return False
    
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if conversation exists."""
        conversation_file = self.conversations_dir / f"{conversation_id.value}.json"
        return conversation_file.exists()
    
    def _conversation_to_dict(self, conversation: Conversation) -> dict:
        """Convert conversation entity to dictionary."""
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
    
    def _dict_to_conversation(self, data: dict) -> Optional[Conversation]:
        """Convert dictionary to conversation entity."""
        try:
            from datetime import datetime
            
            # Create conversation
            conversation = Conversation(
                conversation_id=ConversationId(UUID(data['id'])),
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
                conversation.add_message(message)
            
            return conversation
        
        except Exception as e:
            print(f"Error converting dict to conversation: {e}")
            return None
