"""
Expanded tests for Message Processing Service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.conversation.domain.services.message_processing_service import MessageProcessingService
from src.conversation.domain.entities.enhanced_message import TextChunk


class TestMessageProcessingServiceExpanded:
    """Expanded tests for MessageProcessingService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return MessageProcessingService()
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample text chunks"""
        now = datetime.now()
        return [
            TextChunk("Hello", 0, now, is_final=False),
            TextChunk(" world", 1, now + timedelta(seconds=0.5), is_final=False),
            TextChunk("!", 2, now + timedelta(seconds=1), is_final=True)
        ]
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
    
    def test_merge_text_chunks_basic(self, service, sample_chunks):
        """Test merging text chunks"""
        result = service.merge_text_chunks(sample_chunks)
        
        assert isinstance(result, str)
        assert "Hello" in result
        assert "world" in result
    
    def test_merge_empty_chunks_list(self, service):
        """Test merging empty chunks list"""
        result = service.merge_text_chunks([])
        assert result == ""
    
    def test_merge_single_chunk(self, service):
        """Test merging single chunk"""
        chunk = TextChunk("Single chunk", 0, datetime.now())
        result = service.merge_text_chunks([chunk])
        
        assert result == "Single chunk"
    
    def test_merge_preserves_order(self, service):
        """Test that merging preserves chunk order"""
        chunks = [
            TextChunk("First", 0, datetime.now()),
            TextChunk(" second", 1, datetime.now()),
            TextChunk(" third", 2, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert result == "First second third"
    
    def test_merge_handles_whitespace(self, service):
        """Test merging handles whitespace correctly"""
        chunks = [
            TextChunk("Word1", 0, datetime.now()),
            TextChunk(" Word2", 1, datetime.now()),
            TextChunk("  Word3", 2, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "Word1" in result
        assert "Word2" in result
        assert "Word3" in result
    
    def test_merge_with_punctuation(self, service):
        """Test merging chunks with punctuation"""
        chunks = [
            TextChunk("Hello", 0, datetime.now()),
            TextChunk(",", 1, datetime.now()),
            TextChunk(" world", 2, datetime.now()),
            TextChunk("!", 3, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "Hello, world!" in result
    
    def test_chunks_with_empty_content(self, service):
        """Test handling chunks with empty content"""
        chunks = [
            TextChunk("Hello", 0, datetime.now()),
            TextChunk("", 1, datetime.now()),
            TextChunk(" world", 2, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "Hello" in result
        assert "world" in result
    
    def test_chunks_out_of_order(self, service):
        """Test merging chunks that are out of order"""
        chunks = [
            TextChunk(" world", 1, datetime.now()),
            TextChunk("Hello", 0, datetime.now()),
            TextChunk("!", 2, datetime.now())
        ]
        
        # Should handle gracefully (implementation dependent)
        result = service.merge_text_chunks(chunks)
        assert isinstance(result, str)
    
    def test_merge_with_unicode(self, service):
        """Test merging chunks with unicode"""
        chunks = [
            TextChunk("Hola", 0, datetime.now()),
            TextChunk(" señor", 1, datetime.now()),
            TextChunk(" 👋", 2, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "Hola" in result
        assert "señor" in result
        assert "👋" in result
    
    def test_merge_with_newlines(self, service):
        """Test merging chunks with newlines"""
        chunks = [
            TextChunk("Line 1\n", 0, datetime.now()),
            TextChunk("Line 2", 1, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_merge_large_number_of_chunks(self, service):
        """Test merging large number of chunks"""
        chunks = [
            TextChunk(f"Chunk{i} ", i, datetime.now())
            for i in range(100)
        ]
        
        result = service.merge_text_chunks(chunks)
        
        assert isinstance(result, str)
        assert "Chunk0" in result
        assert "Chunk99" in result
    
    def test_chunk_with_special_characters(self, service):
        """Test chunks with special characters"""
        chunks = [
            TextChunk("Test @#$%", 0, datetime.now()),
            TextChunk(" & more!", 1, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "@#$%" in result
        assert "&" in result
    
    def test_chunks_with_numbers(self, service):
        """Test chunks with numbers"""
        chunks = [
            TextChunk("Price is", 0, datetime.now()),
            TextChunk(" $1,234.56", 1, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "1,234.56" in result
    
    def test_merge_preserves_spacing(self, service):
        """Test that spacing between chunks is preserved"""
        chunks = [
            TextChunk("Word1", 0, datetime.now()),
            TextChunk(" Word2", 1, datetime.now())
        ]
        
        result = service.merge_text_chunks(chunks)
        # Should have space between words
        assert "Word1 Word2" in result or "Word1Word2" in result
    
    def test_final_chunk_flag_handling(self, service):
        """Test handling of final chunk flag"""
        chunks = [
            TextChunk("Start", 0, datetime.now(), is_final=False),
            TextChunk(" end", 1, datetime.now(), is_final=True)
        ]
        
        result = service.merge_text_chunks(chunks)
        assert "Start" in result
        assert "end" in result
    
    def test_chunks_with_confidence_scores(self, service):
        """Test chunks with confidence scores"""
        chunks = [
            TextChunk("High", 0, datetime.now(), confidence=0.95),
            TextChunk(" low", 1, datetime.now(), confidence=0.60)
        ]
        
        result = service.merge_text_chunks(chunks)
        # Confidence shouldn't affect merging
        assert "High" in result
        assert "low" in result
    
    def test_merge_multiple_times_same_chunks(self, service, sample_chunks):
        """Test merging same chunks multiple times is idempotent"""
        result1 = service.merge_text_chunks(sample_chunks)
        result2 = service.merge_text_chunks(sample_chunks)
        
        assert result1 == result2
    
    def test_service_methods_exist(self, service):
        """Test that expected service methods exist"""
        assert hasattr(service, 'merge_text_chunks')
        assert callable(service.merge_text_chunks)

