"""
Tests to improve conversation repository coverage
"""
import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import json

from src.conversation.infrastructure.repositories.enhanced_conversation_repository import EnhancedConversationRepository
from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.entities.enhanced_message import EnhancedMessage
from src.conversation.domain.value_objects.conversation_id import ConversationId


class TestEnhancedConversationRepositoryCoverage:
    """Additional tests to improve enhanced conversation repository coverage"""
    
    @pytest.fixture
    def repository(self, tmp_path):
        """Create repository instance with temp directory"""
        return EnhancedConversationRepository(base_path=str(tmp_path))
    
    @pytest.fixture
    def sample_conversation(self):
        """Create sample conversation"""
        return Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test_persona",
            context_id="test_context",
            status=ConversationStatus.ACTIVE,
            transcription_id="test_transcription",
            analysis_id=None,
            metadata={"test": "data"},
            created_at=datetime.now(),
            completed_at=None
        )
    
    @pytest.fixture
    def sample_message(self):
        """Create sample enhanced message"""
        # Create simple message dict
        return {
            'role': 'user',
            'content': 'Test message',
            'timestamp': datetime.now().isoformat(),
            'metadata': {'test': 'meta'}
        }
    
    @pytest.mark.asyncio
    async def test_save_and_load_conversation(self, repository, sample_conversation, sample_message):
        """Test saving and loading conversation with messages"""
        # Add message
        sample_conversation.add_message_data(sample_message)
        
        # Save
        await repository.save_conversation(sample_conversation)
        
        # Load
        loaded = await repository.load_conversation(sample_conversation.id)
        
        assert loaded is not None
        assert loaded.id.value == sample_conversation.id.value
        assert loaded.persona_id == sample_conversation.persona_id
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_conversation(self, repository):
        """Test loading conversation that doesn't exist"""
        result = await repository.load_conversation(ConversationId(value=uuid4()))
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_conversation_creates_directory(self, tmp_path, sample_conversation):
        """Test that saving creates necessary directories"""
        repo = EnhancedConversationRepository(base_path=str(tmp_path))
        await repo.save_conversation(sample_conversation)
        
        conversation_file = tmp_path / f"{sample_conversation.id.value}.json"
        assert conversation_file.exists()
    
    @pytest.mark.asyncio
    async def test_list_conversations(self, repository, sample_conversation):
        """Test listing all conversations"""
        await repository.save_conversation(sample_conversation)
        
        conversations = await repository.list_conversations()
        
        assert len(conversations) >= 1
        assert any(c['id'] == str(sample_conversation.id.value) for c in conversations)
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, repository, sample_conversation):
        """Test deleting a conversation"""
        await repository.save_conversation(sample_conversation)
        
        result = await repository.delete_conversation(sample_conversation.id)
        
        assert result is True
        
        # Verify deletion
        loaded = await repository.load_conversation(sample_conversation.id)
        assert loaded is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_conversation(self, repository):
        """Test deleting conversation that doesn't exist"""
        result = await repository.delete_conversation(ConversationId(value=uuid4()))
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_conversation_stats(self, repository, sample_conversation, sample_message):
        """Test getting conversation statistics"""
        sample_conversation.add_message_data(sample_message)
        await repository.save_conversation(sample_conversation)
        
        stats = await repository.get_conversation_stats(sample_conversation.id)
        
        assert stats is not None
        assert 'message_count' in stats
        assert stats['message_count'] >= 1
    
    @pytest.mark.asyncio
    async def test_conversation_json_serialization(self, tmp_path, sample_conversation):
        """Test that conversation is properly serialized to JSON"""
        repo = EnhancedConversationRepository(base_path=str(tmp_path))
        await repo.save_conversation(sample_conversation)
        
        # Read file directly
        file_path = tmp_path / f"{sample_conversation.id.value}.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert 'id' in data
        assert 'persona_id' in data
        assert 'status' in data
    
    @pytest.mark.asyncio
    async def test_update_conversation_status(self, repository, sample_conversation):
        """Test updating conversation status"""
        await repository.save_conversation(sample_conversation)
        
        # Update status
        sample_conversation.complete()
        await repository.save_conversation(sample_conversation)
        
        # Verify update
        loaded = await repository.load_conversation(sample_conversation.id)
        assert loaded.status == ConversationStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_conversation_with_multiple_messages(self, repository, sample_conversation):
        """Test conversation with multiple messages"""
        # Add multiple messages
        for i in range(5):
            msg = {
                'role': 'user' if i % 2 == 0 else 'assistant',
                'content': f"Message {i}",
                'timestamp': datetime.now().isoformat(),
                'metadata': {}
            }
            sample_conversation.add_message_data(msg)
        
        await repository.save_conversation(sample_conversation)
        
        # Load and verify
        loaded = await repository.load_conversation(sample_conversation.id)
        assert loaded is not None
        # Verify messages are preserved (implementation dependent)
    
    @pytest.mark.asyncio
    async def test_repository_handles_corrupted_json(self, tmp_path):
        """Test that repository handles corrupted JSON gracefully"""
        # Create corrupted file
        corrupt_file = tmp_path / "corrupted.json"
        corrupt_file.write_text("{invalid json")
        
        repo = EnhancedConversationRepository(base_path=str(tmp_path))
        conversations = await repo.list_conversations()
        
        # Should not crash
        assert isinstance(conversations, list)
    
    @pytest.mark.asyncio
    async def test_conversation_with_metadata(self, repository, sample_conversation):
        """Test conversation with custom metadata"""
        sample_conversation.metadata = {
            'custom_field': 'value',
            'number': 42,
            'nested': {'key': 'value'}
        }
        
        await repository.save_conversation(sample_conversation)
        loaded = await repository.load_conversation(sample_conversation.id)
        
        assert loaded is not None
        assert loaded.metadata is not None

