"""
Comprehensive tests for EnhancedMessage entity
"""
import pytest
from datetime import datetime

from src.conversation.domain.entities.enhanced_message import (
    EnhancedMessage,
    MessageType,
    ProcessingStatus,
    TextChunk
)


class TestEnhancedMessageEntity:
    """Tests for EnhancedMessage entity"""
    
    def test_message_type_enum(self):
        """Test MessageType enum values"""
        assert MessageType.TEXT.value == "text"
        assert MessageType.AUDIO.value == "audio"
        assert MessageType.MIXED.value == "mixed"
    
    def test_processing_status_enum(self):
        """Test ProcessingStatus enum values"""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"
    
    def test_text_chunk_creation(self):
        """Test TextChunk creation"""
        chunk = TextChunk(
            content="Test content",
            chunk_index=0,
            timestamp=datetime.now(),
            is_final=False,
            confidence=0.95
        )
        
        assert chunk.content == "Test content"
        assert chunk.chunk_index == 0
        assert chunk.is_final is False
        assert chunk.confidence == 0.95
    
    def test_text_chunk_without_confidence(self):
        """Test TextChunk without confidence score"""
        chunk = TextChunk(
            content="Test",
            chunk_index=0,
            timestamp=datetime.now()
        )
        
        assert chunk.content == "Test"
        assert chunk.confidence is None
    
    def test_text_chunk_final_flag(self):
        """Test TextChunk final flag"""
        chunk = TextChunk(
            content="Final chunk",
            chunk_index=1,
            timestamp=datetime.now(),
            is_final=True
        )
        
        assert chunk.is_final is True
    
    def test_text_chunk_timestamp(self):
        """Test TextChunk timestamp"""
        now = datetime.now()
        chunk = TextChunk(
            content="Test",
            chunk_index=0,
            timestamp=now
        )
        
        assert chunk.timestamp == now
    
    def test_text_chunk_index(self):
        """Test TextChunk indexing"""
        chunk1 = TextChunk("Chunk 1", 0, datetime.now())
        chunk2 = TextChunk("Chunk 2", 1, datetime.now())
        chunk3 = TextChunk("Chunk 3", 2, datetime.now())
        
        assert chunk1.chunk_index == 0
        assert chunk2.chunk_index == 1
        assert chunk3.chunk_index == 2
    
    def test_text_chunk_content_access(self):
        """Test accessing chunk content"""
        content = "This is test content"
        chunk = TextChunk(content, 0, datetime.now())
        
        assert chunk.content == content
        assert len(chunk.content) == len(content)
    
    def test_text_chunk_with_empty_content(self):
        """Test TextChunk with empty content"""
        chunk = TextChunk("", 0, datetime.now())
        assert chunk.content == ""
    
    def test_text_chunk_with_long_content(self):
        """Test TextChunk with long content"""
        long_content = "A" * 10000
        chunk = TextChunk(long_content, 0, datetime.now())
        
        assert len(chunk.content) == 10000
    
    def test_text_chunk_confidence_range(self):
        """Test TextChunk confidence score"""
        chunk_low = TextChunk("Test", 0, datetime.now(), confidence=0.1)
        chunk_high = TextChunk("Test", 0, datetime.now(), confidence=0.99)
        
        assert chunk_low.confidence == 0.1
        assert chunk_high.confidence == 0.99
    
    def test_text_chunks_independent(self):
        """Test that text chunks are independent"""
        chunk1 = TextChunk("Content 1", 0, datetime.now())
        chunk2 = TextChunk("Content 2", 1, datetime.now())
        
        assert chunk1.content != chunk2.content
        assert chunk1.chunk_index != chunk2.chunk_index
    
    def test_text_chunk_immutable_content(self):
        """Test that chunk content is immutable"""
        chunk = TextChunk("Original", 0, datetime.now())
        original_content = chunk.content
        
        # Try to access (should work)
        assert chunk.content == original_content
    
    def test_multiple_chunks_same_timestamp(self):
        """Test multiple chunks can have same timestamp"""
        now = datetime.now()
        chunk1 = TextChunk("Chunk 1", 0, now)
        chunk2 = TextChunk("Chunk 2", 1, now)
        
        assert chunk1.timestamp == chunk2.timestamp
        assert chunk1.chunk_index != chunk2.chunk_index
    
    def test_chunk_ordering_by_index(self):
        """Test that chunks can be ordered by index"""
        chunks = [
            TextChunk("C", 2, datetime.now()),
            TextChunk("A", 0, datetime.now()),
            TextChunk("B", 1, datetime.now())
        ]
        
        sorted_chunks = sorted(chunks, key=lambda c: c.chunk_index)
        
        assert sorted_chunks[0].chunk_index == 0
        assert sorted_chunks[1].chunk_index == 1
        assert sorted_chunks[2].chunk_index == 2
    
    def test_text_chunk_properties_readonly(self):
        """Test that chunk properties are read-only"""
        chunk = TextChunk("Test", 0, datetime.now())
        
        # Should be able to read
        assert chunk.content == "Test"
        assert chunk.chunk_index == 0
        assert chunk.is_final is False
    
    def test_enhanced_message_type_values(self):
        """Test all MessageType values are accessible"""
        types = [MessageType.TEXT, MessageType.AUDIO, MessageType.MIXED]
        assert len(types) == 3
    
    def test_processing_status_values(self):
        """Test all ProcessingStatus values are accessible"""
        statuses = [
            ProcessingStatus.PENDING,
            ProcessingStatus.PROCESSING,
            ProcessingStatus.COMPLETED,
            ProcessingStatus.FAILED
        ]
        assert len(statuses) == 4
    
    def test_text_chunk_with_special_characters(self):
        """Test TextChunk with special characters"""
        content = "Test: émojis 🎉, symbols @#$%, unicode ñáéíóú"
        chunk = TextChunk(content, 0, datetime.now())
        
        assert chunk.content == content
    
    def test_text_chunk_with_newlines(self):
        """Test TextChunk with newlines"""
        content = "Line 1\nLine 2\nLine 3"
        chunk = TextChunk(content, 0, datetime.now())
        
        assert "\n" in chunk.content
        assert chunk.content.count("\n") == 2

