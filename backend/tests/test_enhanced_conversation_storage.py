"""
Tests for enhanced conversation storage functionality.
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from uuid import UUID
from datetime import datetime

from src.conversation.domain.entities.enhanced_message import (
    EnhancedMessage, 
    MessageType, 
    ProcessingStatus,
    AudioMetadata
)
from src.conversation.domain.services.message_processing_service import MessageProcessingService
from src.conversation.infrastructure.repositories.enhanced_conversation_repository import EnhancedConversationRepository
from src.conversation.application.services.enhanced_conversation_service import EnhancedConversationService
from src.conversation.infrastructure.repositories.sql_conversation_repository import SQLConversationRepository
from src.conversation.domain.value_objects.conversation_id import ConversationId


class TestEnhancedMessage:
    """Test enhanced message functionality."""
    
    def test_create_user_message(self):
        """Test creating a user message."""
        conversation_id = UUID("12345678-1234-1234-1234-123456789012")
        
        message = EnhancedMessage.create_user_message(
            conversation_id=conversation_id,
            content="Hello, how are you?",
            message_type=MessageType.TEXT
        )
        
        assert message.role == "user"
        assert message.message_type == MessageType.TEXT
        assert message.get_display_content() == "Hello, how are you?"
        assert message.has_final_content()
        assert message.processing_status == ProcessingStatus.COMPLETED
    
    def test_add_text_chunks(self):
        """Test adding text chunks and processing."""
        conversation_id = UUID("12345678-1234-1234-1234-123456789012")
        
        message = EnhancedMessage.create_user_message(conversation_id)
        
        # Add chunks progressively
        message.add_text_chunk("Hello", is_final=False)
        assert not message.has_final_content()
        assert message.get_display_content() == "Hello"
        
        message.add_text_chunk(",", is_final=False)
        assert message.get_display_content() == "Hello,"
        
        message.add_text_chunk(" how", is_final=False)
        assert message.get_display_content() == "Hello, how"  # Space preserved from " how"
        
        message.add_text_chunk(" are", is_final=False)
        assert message.get_display_content() == "Hello, how are"  # Space preserved from " are"
        
        message.add_text_chunk(" you?", is_final=True)
        assert message.has_final_content()
        assert message.get_display_content() == "Hello, how are you?"  # Space preserved from " you?"
        assert message.processing_status == ProcessingStatus.COMPLETED
    
    def test_audio_message_with_transcription(self):
        """Test creating an audio message with transcription."""
        conversation_id = UUID("12345678-1234-1234-1234-123456789012")
        
        audio_metadata = AudioMetadata(
            duration_ms=5000,
            format="webm",
            sample_rate=44100
        )
        
        message = EnhancedMessage.create_user_message(
            conversation_id=conversation_id,
            content="This is a transcription",
            message_type=MessageType.MIXED
        )
        
        # Add audio URL and metadata
        message.add_audio_url("audio_url", audio_metadata)
        
        assert message.has_audio()
        assert message.audio_metadata.duration_ms == 5000
        assert message.get_display_content() == "This is a transcription"
        assert message.message_type == MessageType.MIXED
    
    def test_message_serialization(self):
        """Test message serialization and deserialization."""
        conversation_id = UUID("12345678-1234-1234-1234-123456789012")
        
        # Create message
        message = EnhancedMessage.create_user_message(
            conversation_id=conversation_id,
            content="Test message"
        )
        
        message.add_text_chunk("Partial", is_final=False)
        message.add_text_chunk(" content", is_final=True)
        
        # Serialize
        message_dict = message.to_dict()
        
        # Deserialize
        restored_message = EnhancedMessage.from_dict(message_dict)
        
        assert restored_message.id == message.id
        assert restored_message.role == message.role
        assert restored_message.get_display_content() == message.get_display_content()
        assert len(restored_message.text_chunks) == len(message.text_chunks)


class TestMessageProcessingService:
    """Test message processing service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = MessageProcessingService()
        self.conversation_id = UUID("12345678-1234-1234-1234-123456789012")
    
    def test_process_text_chunks(self):
        """Test processing text chunks."""
        # Process first chunk
        message1 = self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="user",
            content="Hello",
            is_final=False,
            message_group_id="group1"
        )
        
        assert message1.get_display_content() == "Hello"
        assert not message1.has_final_content()
        
        # Process additional chunks
        message2 = self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="user",
            content=" world",
            is_final=False,
            message_group_id="group1"
        )
        
        # Should be the same message instance
        assert message2.id == message1.id
        assert message2.get_display_content() == "Hello world"
        
        # Finalize
        message3 = self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="user",
            content="!",
            is_final=True,
            message_group_id="group1"
        )
        
        assert message3.id == message1.id
        assert message3.get_display_content() == "Hello world!"
        assert message3.has_final_content()
    
    def test_process_audio_message(self):
        """Test processing audio message."""
        message = self.service.process_audio_message(
            conversation_id=self.conversation_id,
            role="user",
            audio_data="base64_audio_data",
            audio_format="webm",
            duration_ms=3000,
            transcription="Audio transcription",
            confidence=0.95
        )
        
        assert message.role == "user"
        assert message.message_type == MessageType.MIXED
        assert message.get_display_content() == "Audio transcription"
        assert message.audio_metadata.duration_ms == 3000
        assert message.metadata['audio_data'] == "base64_audio_data"
    
    def test_merge_messages(self):
        """Test merging consecutive messages."""
        # Create messages with short time gaps
        base_time = datetime.utcnow()
        
        messages = []
        for i in range(3):
            message = EnhancedMessage.create_user_message(self.conversation_id)
            message._timestamp = base_time.replace(second=base_time.second + i)
            message.add_text_chunk(f"Chunk {i}", is_final=False)
            messages.append(message)
        
        # Merge messages
        merged = self.service.merge_messages(messages)
        
        assert len(merged) == 1
        assert merged[0].get_display_content() == "Chunk 0Chunk 1Chunk 2"
    
    def test_conversation_summary(self):
        """Test conversation summary generation."""
        messages = [
            EnhancedMessage.create_user_message(self.conversation_id, "Hello"),
            EnhancedMessage.create_assistant_message(self.conversation_id, "Hi there!")
        ]
        
        summary = self.service.get_conversation_summary(messages)
        
        assert summary['total_messages'] == 2
        assert summary['user_messages'] == 1
        assert summary['assistant_messages'] == 1
        assert summary['audio_messages'] == 0


class TestEnhancedConversationRepository:
    """Test enhanced conversation repository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = EnhancedConversationRepository(
            conversations_dir=f"{self.temp_dir}/conversations",
            enhanced_dir=f"{self.temp_dir}/enhanced"
        )
        self.conversation_id = ConversationId(UUID("12345678-1234-1234-1234-123456789012"))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_save_and_load_enhanced_messages(self):
        """Test saving and loading enhanced messages."""
        # Create messages
        messages = [
            EnhancedMessage.create_user_message(self.conversation_id, "Hello"),
            EnhancedMessage.create_assistant_message(self.conversation_id, "Hi there!")
        ]
        
        # Save
        await self.repo.save_enhanced_conversation(self.conversation_id, messages)
        
        # Load
        loaded_messages = await self.repo.get_enhanced_messages(self.conversation_id)
        
        assert len(loaded_messages) == 2
        assert loaded_messages[0].role == "user"
        assert loaded_messages[0].get_display_content() == "Hello"
        assert loaded_messages[1].role == "assistant"
        assert loaded_messages[1].get_display_content() == "Hi there!"
    
    @pytest.mark.asyncio
    async def test_add_enhanced_message(self):
        """Test adding enhanced messages to conversation."""
        # Add first message
        message1 = EnhancedMessage.create_user_message(self.conversation_id, "Hello")
        await self.repo.add_enhanced_message(self.conversation_id, message1)
        
        # Add second message
        message2 = EnhancedMessage.create_assistant_message(self.conversation_id, "Hi!")
        await self.repo.add_enhanced_message(self.conversation_id, message2)
        
        # Verify
        messages = await self.repo.get_enhanced_messages(self.conversation_id)
        assert len(messages) == 2
    
    @pytest.mark.asyncio
    async def test_update_message_content(self):
        """Test updating message content."""
        # Create and save message
        message = EnhancedMessage.create_user_message(self.conversation_id, "Original content")
        await self.repo.save_enhanced_conversation(self.conversation_id, [message])
        
        # Update content
        success = await self.repo.update_message_content(
            self.conversation_id, 
            message.id, 
            "Updated content"
        )
        
        assert success
        
        # Verify update
        messages = await self.repo.get_enhanced_messages(self.conversation_id)
        assert messages[0].get_display_content() == "Updated content"
    
    @pytest.mark.asyncio
    async def test_conversation_statistics(self):
        """Test conversation statistics."""
        # Create messages with different types
        messages = [
            EnhancedMessage.create_user_message(self.conversation_id, "Hello"),
            EnhancedMessage.create_assistant_message(self.conversation_id, "Hi!")
        ]
        
        # Add audio metadata to first message
        audio_metadata = AudioMetadata(duration_ms=2000)
        messages[0].add_audio_url("audio_url", audio_metadata)
        
        await self.repo.save_enhanced_conversation(self.conversation_id, messages)
        
        # Get statistics
        stats = await self.repo.get_conversation_statistics(self.conversation_id)
        
        assert stats['total_messages'] == 2
        assert stats['user_messages'] == 1
        assert stats['assistant_messages'] == 1
        assert stats['audio_messages'] == 1
        assert stats['total_duration_ms'] == 2000


class TestEnhancedConversationService:
    """Test enhanced conversation service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock conversation repository
        self.conversation_repo = SQLConversationRepository(
            conversations_dir=f"{self.temp_dir}/conversations"
        )
        
        # Create enhanced repository
        self.enhanced_repo = EnhancedConversationRepository(
            conversations_dir=f"{self.temp_dir}/conversations",
            enhanced_dir=f"{self.temp_dir}/enhanced"
        )
        
        # Create service
        self.service = EnhancedConversationService(self.conversation_repo, self.enhanced_repo)
        self.conversation_id = ConversationId(UUID("12345678-1234-1234-1234-123456789012"))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_process_text_chunks_integration(self):
        """Test processing text chunks end-to-end."""
        # Process chunks
        message = await self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="user",
            content="Hello",
            is_final=False
        )
        
        # Verify message was saved
        loaded_messages = await self.service.get_enhanced_messages(self.conversation_id)
        assert len(loaded_messages) == 1
        assert loaded_messages[0].get_display_content() == "Hello"
    
    @pytest.mark.asyncio
    async def test_conversation_summary(self):
        """Test conversation summary generation."""
        # Add messages
        await self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="user",
            content="Hello",
            is_final=True
        )
        
        await self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="assistant",
            content="Hi there!",
            is_final=True
        )
        
        # Get summary
        summary = await self.service.get_conversation_summary(self.conversation_id)
        
        assert summary['total_messages'] == 2
        assert summary['user_messages'] == 1
        assert summary['assistant_messages'] == 1
    
    @pytest.mark.asyncio
    async def test_export_for_analysis(self):
        """Test exporting conversation for analysis."""
        # Add messages
        await self.service.process_text_chunk(
            conversation_id=self.conversation_id,
            role="user",
            content="Hello",
            is_final=True
        )
        
        # Export
        export_data = await self.service.export_conversation_for_analysis(self.conversation_id)
        
        assert export_data is not None
        assert export_data['conversation_id'] == str(self.conversation_id.value)
        assert len(export_data['messages']) == 1
        assert export_data['messages'][0]['role'] == "user"
        assert export_data['messages'][0]['content'] == "Hello"
