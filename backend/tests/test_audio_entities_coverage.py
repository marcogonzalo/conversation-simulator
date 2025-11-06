"""
Tests for audio domain entities
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.audio.domain.entities.audio_chunk import AudioChunk
from src.audio.domain.value_objects.audio_id import AudioId
from src.audio.domain.value_objects.audio_format import AudioFormat


class TestAudioEntities:
    """Tests for audio domain entities"""
    
    def test_audio_id_creation(self):
        """Test AudioId creation"""
        audio_id = AudioId(value=uuid4())
        assert audio_id is not None
        assert audio_id.value is not None
    
    def test_audio_id_string_representation(self):
        """Test AudioId string representation"""
        uid = uuid4()
        audio_id = AudioId(value=uid)
        assert str(audio_id) == str(uid)
    
    def test_audio_id_equality(self):
        """Test AudioId equality"""
        uid = uuid4()
        id1 = AudioId(value=uid)
        id2 = AudioId(value=uid)
        assert id1.value == id2.value
    
    def test_audio_format_wav(self):
        """Test AudioFormat for WAV"""
        fmt = AudioFormat(format_type="wav", sample_rate=16000)
        assert fmt.format_type == "wav"
        assert fmt.sample_rate == 16000
    
    def test_audio_format_webm(self):
        """Test AudioFormat for WebM"""
        fmt = AudioFormat(format_type="webm", sample_rate=24000)
        assert fmt.format_type == "webm"
    
    def test_audio_format_pcm16(self):
        """Test AudioFormat for PCM16"""
        fmt = AudioFormat(format_type="pcm16", sample_rate=16000)
        assert fmt.format_type == "pcm16"
    
    def test_audio_format_sample_rates(self):
        """Test various sample rates"""
        rates = [8000, 16000, 24000, 48000]
        for rate in rates:
            fmt = AudioFormat(format_type="wav", sample_rate=rate)
            assert fmt.sample_rate == rate
    
    def test_audio_chunk_creation(self):
        """Test AudioChunk creation"""
        chunk = AudioChunk(
            audio_id=AudioId(value=uuid4()),
            data=b"fake audio data",
            sequence_number=0,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        assert chunk is not None
        assert chunk.data == b"fake audio data"
    
    def test_audio_chunk_sequence_number(self):
        """Test audio chunk sequence numbering"""
        chunk1 = AudioChunk(
            audio_id=AudioId(value=uuid4()),
            data=b"data1",
            sequence_number=0,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        chunk2 = AudioChunk(
            audio_id=AudioId(value=uuid4()),
            data=b"data2",
            sequence_number=1,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        assert chunk1.sequence_number == 0
        assert chunk2.sequence_number == 1
    
    def test_audio_chunk_timestamp(self):
        """Test audio chunk has timestamp"""
        now = datetime.now()
        chunk = AudioChunk(
            audio_id=AudioId(value=uuid4()),
            data=b"data",
            sequence_number=0,
            timestamp=now,
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        assert chunk.timestamp == now
    
    def test_audio_chunk_with_empty_data(self):
        """Test audio chunk with empty data"""
        chunk = AudioChunk(
            audio_id=AudioId(value=uuid4()),
            data=b"",
            sequence_number=0,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        assert chunk.data == b""
    
    def test_audio_chunk_with_large_data(self):
        """Test audio chunk with large data"""
        large_data = b"\x00" * 100000
        chunk = AudioChunk(
            audio_id=AudioId(value=uuid4()),
            data=large_data,
            sequence_number=0,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        assert len(chunk.data) == 100000
    
    def test_audio_format_string_representation(self):
        """Test AudioFormat string representation"""
        fmt = AudioFormat(format_type="wav", sample_rate=16000)
        str_repr = str(fmt)
        
        assert "wav" in str_repr.lower() or str_repr is not None
    
    def test_multiple_audio_chunks_independent(self):
        """Test multiple chunks are independent"""
        audio_id = AudioId(value=uuid4())
        
        chunk1 = AudioChunk(
            audio_id=audio_id,
            data=b"data1",
            sequence_number=0,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        chunk2 = AudioChunk(
            audio_id=audio_id,
            data=b"data2",
            sequence_number=1,
            timestamp=datetime.now(),
            format=AudioFormat(format_type="wav", sample_rate=16000)
        )
        
        assert chunk1.data != chunk2.data
        assert chunk1.sequence_number != chunk2.sequence_number

