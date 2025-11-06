"""
Comprehensive tests for message entities
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.conversation.domain.entities.message import Message
from src.conversation.domain.entities.transcription import Transcription


class TestMessageEntity:
    """Comprehensive tests for Message entity"""
    
    def test_message_creation_user(self):
        """Test creating user message"""
        msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="Test message",
            timestamp=datetime.now(),
            metadata={}
        )
        
        assert msg.role == "user"
        assert msg.content == "Test message"
    
    def test_message_creation_assistant(self):
        """Test creating assistant message"""
        msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="assistant",
            content="Assistant response",
            timestamp=datetime.now(),
            metadata={}
        )
        
        assert msg.role == "assistant"
    
    def test_message_with_metadata(self):
        """Test message with metadata"""
        metadata = {"confidence": 0.95, "source": "openai"}
        msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="Test",
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        assert msg.metadata == metadata
    
    def test_message_timestamp(self):
        """Test message timestamp"""
        now = datetime.now()
        msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="Test",
            timestamp=now,
            metadata={}
        )
        
        assert msg.timestamp == now
    
    def test_message_ids_are_unique(self):
        """Test message IDs are unique"""
        msg1 = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="Msg 1",
            timestamp=datetime.now(),
            metadata={}
        )
        
        msg2 = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="Msg 2",
            timestamp=datetime.now(),
            metadata={}
        )
        
        assert msg1.message_id != msg2.message_id
    
    def test_message_with_empty_content(self):
        """Test message with empty content"""
        msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="",
            timestamp=datetime.now(),
            metadata={}
        )
        
        assert msg.content == ""
    
    def test_message_with_long_content(self):
        """Test message with very long content"""
        long_content = "Word " * 10000
        msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content=long_content,
            timestamp=datetime.now(),
            metadata={}
        )
        
        assert len(msg.content) > 50000
    
    def test_message_roles(self):
        """Test different message roles"""
        user_msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="user",
            content="User message",
            timestamp=datetime.now(),
            metadata={}
        )
        
        assistant_msg = Message(
            message_id=str(uuid4()),
            conversation_id=str(uuid4()),
            role="assistant",
            content="Assistant message",
            timestamp=datetime.now(),
            metadata={}
        )
        
        assert user_msg.role == "user"
        assert assistant_msg.role == "assistant"


class TestTranscriptionEntity:
    """Comprehensive tests for Transcription entity"""
    
    def test_transcription_creation(self):
        """Test transcription creation"""
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=[],
            metadata={},
            created_at=datetime.now()
        )
        
        assert trans is not None
        assert isinstance(trans.messages, list)
    
    def test_transcription_with_messages(self):
        """Test transcription with messages"""
        messages = [
            {"role": "user", "content": "Hello", "timestamp": "2024-01-01T10:00:00"},
            {"role": "assistant", "content": "Hi", "timestamp": "2024-01-01T10:00:05"}
        ]
        
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=messages,
            metadata={},
            created_at=datetime.now()
        )
        
        assert len(trans.messages) == 2
    
    def test_transcription_empty_messages(self):
        """Test transcription with no messages"""
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=[],
            metadata={},
            created_at=datetime.now()
        )
        
        assert len(trans.messages) == 0
    
    def test_transcription_with_metadata(self):
        """Test transcription with metadata"""
        metadata = {"duration": 120, "turn_count": 10}
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=[],
            metadata=metadata,
            created_at=datetime.now()
        )
        
        assert trans.metadata == metadata
    
    def test_transcription_timestamp(self):
        """Test transcription timestamp"""
        now = datetime.now()
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=[],
            metadata={},
            created_at=now
        )
        
        assert trans.created_at == now
    
    def test_transcription_ids_unique(self):
        """Test transcription IDs are unique"""
        trans1 = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=[],
            metadata={},
            created_at=datetime.now()
        )
        
        trans2 = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=[],
            metadata={},
            created_at=datetime.now()
        )
        
        assert trans1.transcription_id != trans2.transcription_id
    
    def test_transcription_with_many_messages(self):
        """Test transcription with many messages"""
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", 
             "content": f"Message {i}", 
             "timestamp": "2024-01-01T10:00:00"}
            for i in range(100)
        ]
        
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=str(uuid4()),
            messages=messages,
            metadata={},
            created_at=datetime.now()
        )
        
        assert len(trans.messages) == 100
    
    def test_transcription_conversation_link(self):
        """Test transcription links to conversation"""
        conv_id = str(uuid4())
        trans = Transcription(
            transcription_id=str(uuid4()),
            conversation_id=conv_id,
            messages=[],
            metadata={},
            created_at=datetime.now()
        )
        
        assert trans.conversation_id == conv_id

