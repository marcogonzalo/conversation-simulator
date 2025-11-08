"""
Tests for chunk aggregation functionality.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from src.conversation.application.services.voice_conversation_service import VoiceConversationService
from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.audio.application.services.openai_voice_application_service import OpenAIVoiceApplicationService
# Legacy persona import removed
from src.shared.infrastructure.external_apis.api_config import APIConfig


@pytest.mark.unit
@pytest.mark.skip(reason="Async timing issues - needs refactoring with proper async mocking")
class TestChunkAggregation:
    """Tests for chunk aggregation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.conversation_service = AsyncMock(spec=ConversationApplicationService)
        self.conversation_service.send_message = AsyncMock()
        self.voice_service = AsyncMock(spec=OpenAIVoiceApplicationService)
        # Legacy persona_repo removed
        self.api_config = APIConfig()
        
        self.service = VoiceConversationService(
            conversation_service=self.conversation_service,
            voice_service=self.voice_service,
            api_config=self.api_config
        )
    
    @pytest.mark.asyncio
    async def test_chunk_aggregation_same_message(self):
        """Test that chunks within 3 seconds are aggregated into same message."""
        conversation_id = "test-conversation"
        role = "user"
        timestamp1 = datetime.utcnow()
        timestamp2 = timestamp1 + timedelta(seconds=1)  # 1 second later
        
        # Mock send_transcribed_text
        with patch('src.conversation.application.services.openai_voice_conversation_service.send_transcribed_text') as mock_send:
            # First chunk
            await self.service._handle_chunk_with_aggregation(
                conversation_id, "Hello", role, timestamp1
            )
            
            # Second chunk (within 3 seconds)
            await self.service._handle_chunk_with_aggregation(
                conversation_id, " world", role, timestamp2
            )
            
            # Should send individual chunks to frontend
            assert mock_send.call_count == 2
            mock_send.assert_any_call(conversation_id, "Hello", role)
            mock_send.assert_any_call(conversation_id, " world", role)
            
            # Wait for message save (2 seconds + buffer)
            await asyncio.sleep(2.5)
            
            # Should save one aggregated message
            self.conversation_service.send_message.assert_called_once()
            call_args = self.conversation_service.send_message.call_args
            assert call_args[1]['conversation_id'] == conversation_id
            assert call_args[1]['role'] == role
            assert call_args[1]['content'] == "Hello world"
    
    @pytest.mark.asyncio
    async def test_chunk_aggregation_new_message(self):
        """Test that chunks with gap > 3 seconds create separate messages."""
        conversation_id = "test-conversation"
        role = "user"
        timestamp1 = datetime.utcnow()
        timestamp2 = timestamp1 + timedelta(seconds=4)  # 4 seconds later
        
        # Mock send_transcribed_text
        with patch('src.conversation.application.services.openai_voice_conversation_service.send_transcribed_text') as mock_send:
            # First chunk
            await self.service._handle_chunk_with_aggregation(
                conversation_id, "Hello", role, timestamp1
            )
            
            # Wait for first message to be saved
            await asyncio.sleep(2.5)
            
            # Second chunk (after 4 seconds - should be new message)
            await self.service._handle_chunk_with_aggregation(
                conversation_id, "Goodbye", role, timestamp2
            )
            
            # Should send individual chunks to frontend
            assert mock_send.call_count == 2
            mock_send.assert_any_call(conversation_id, "Hello", role)
            mock_send.assert_any_call(conversation_id, "Goodbye", role)
            
            # Wait for second message to be saved
            await asyncio.sleep(2.5)
            
            # Should save two separate messages
            assert self.conversation_service.send_message.call_count == 2
            
            # First message
            first_call = self.conversation_service.send_message.call_args_list[0]
            assert first_call[1]['content'] == "Hello"
            
            # Second message
            second_call = self.conversation_service.send_message.call_args_list[1]
            assert second_call[1]['content'] == "Goodbye"
    
    @pytest.mark.asyncio
    async def test_save_pending_chunks_on_end(self):
        """Test that pending chunks are saved when conversation ends."""
        conversation_id = "test-conversation"
        role = "user"
        timestamp = datetime.utcnow()
        
        # Mock send_transcribed_text
        with patch('src.conversation.application.services.openai_voice_conversation_service.send_transcribed_text'):
            # Add a chunk
            await self.service._handle_chunk_with_aggregation(
                conversation_id, "Hello", role, timestamp
            )
            
            # End conversation immediately (before 2 second delay)
            await self.service._save_pending_chunks(conversation_id)
            
            # Should save the pending chunk
            self.conversation_service.send_message.assert_called_once()
            call_args = self.conversation_service.send_message.call_args
            assert call_args[1]['conversation_id'] == conversation_id
            assert call_args[1]['role'] == role
            assert call_args[1]['content'] == "Hello"
    
    @pytest.mark.asyncio
    async def test_chunk_aggregation_different_roles(self):
        """Test that chunks from different roles are handled separately."""
        conversation_id = "test-conversation"
        timestamp = datetime.utcnow()
        
        # Mock send_transcribed_text
        with patch('src.conversation.application.services.openai_voice_conversation_service.send_transcribed_text'):
            # User chunk
            await self.service._handle_chunk_with_aggregation(
                conversation_id, "Hello", "user", timestamp
            )
            
            # AI chunk (different role)
            await self.service._handle_chunk_with_aggregation(
                conversation_id, "Hi there", "ai", timestamp
            )
            
            # Wait for messages to be saved
            await asyncio.sleep(2.5)
            
            # Should save two separate messages (one per role)
            assert self.conversation_service.send_message.call_count == 2
            
            # Check user message
            user_call = next(call for call in self.conversation_service.send_message.call_args_list 
                           if call[1]['role'] == 'user')
            assert user_call[1]['content'] == "Hello"
            
            # Check AI message
            ai_call = next(call for call in self.conversation_service.send_message.call_args_list 
                         if call[1]['role'] == 'ai')
            assert ai_call[1]['content'] == "Hi there"
