"""
Unit tests for AudioConverterService
Tests configurable audio format conversion (PCM16 to WAV/WebM)
"""
import pytest
from src.audio.infrastructure.services.audio_converter_service import AudioConverterService


class TestAudioConverterService:
    """Test cases for AudioConverterService."""

    @pytest.fixture
    def service_webm(self):
        """Create service instance with WebM default."""
        return AudioConverterService(default_format="webm")

    @pytest.fixture
    def service_wav(self):
        """Create service instance with WAV default."""
        return AudioConverterService(default_format="wav")

    @pytest.mark.asyncio
    async def test_wav_conversion_generates_valid_header(self, service_wav):
        """Test that WAV conversion generates a valid WAV file header."""
        # Arrange
        sample_rate = 24000
        pcm_data = bytes([0, 0] * 24000)  # 1 second of silent audio
        
        # Act
        wav_data = await service_wav.convert_pcm_to_format(pcm_data, output_format="wav", sample_rate=sample_rate)
        
        # Assert - Verify WAV header structure
        assert len(wav_data) > 44, "WAV file should have at least 44-byte header"
        assert wav_data[0:4] == b'RIFF', "Should start with RIFF"
        assert wav_data[8:12] == b'WAVE', "Should contain WAVE"
        assert wav_data[12:16] == b'fmt ', "Should contain fmt chunk"
        
        # Check audio format (PCM = 1)
        audio_format = int.from_bytes(wav_data[20:22], 'little')
        assert audio_format == 1, "Audio format should be PCM (1)"
        
        # Check sample rate
        parsed_sample_rate = int.from_bytes(wav_data[24:28], 'little')
        assert parsed_sample_rate == sample_rate, f"Sample rate should be {sample_rate}"
        
        # Check PCM data is preserved
        assert wav_data[44:] == pcm_data, "PCM data should be preserved after header"

    @pytest.mark.asyncio
    async def test_webm_conversion_generates_valid_file(self, service_webm):
        """Test that WebM conversion generates a valid WebM file."""
        # Arrange
        sample_rate = 24000
        pcm_data = bytes([0, 0] * 24000)  # 1 second of silent audio
        
        # Act
        webm_data = await service_webm.convert_pcm_to_format(pcm_data, output_format="webm", sample_rate=sample_rate)
        
        # Assert - Verify WebM header
        assert len(webm_data) > 0, "Should generate WebM data"
        # WebM starts with EBML header (1A 45 DF A3)
        assert webm_data[0:4] == bytes([0x1A, 0x45, 0xDF, 0xA3]), "Should have valid WebM/EBML header"
        # WebM should be smaller than WAV due to compression
        assert len(webm_data) < len(pcm_data), "WebM should be compressed (smaller than raw PCM)"

    @pytest.mark.asyncio
    async def test_uses_default_format_when_not_specified(self, service_webm):
        """Test that service uses default format when output_format is None."""
        # Arrange
        pcm_data = bytes([0, 0] * 1000)
        
        # Act
        result = await service_webm.convert_pcm_to_format(pcm_data, output_format=None)
        
        # Assert - Should use webm (default for this instance)
        assert result[0:4] == bytes([0x1A, 0x45, 0xDF, 0xA3]), "Should use WebM default"

    @pytest.mark.asyncio
    async def test_can_override_default_format(self, service_webm):
        """Test that explicit format overrides default."""
        # Arrange
        pcm_data = bytes([0, 0] * 1000)
        
        # Act
        result = await service_webm.convert_pcm_to_format(pcm_data, output_format="wav")
        
        # Assert - Should use WAV despite webm default
        assert result[0:4] == b'RIFF', "Should override to WAV"

    @pytest.mark.asyncio
    async def test_wav_with_different_sample_rates(self, service_wav):
        """Test WAV conversion with various sample rates."""
        # Arrange
        pcm_data = bytes([0, 0] * 100)
        sample_rates = [8000, 16000, 24000, 48000]
        
        for sample_rate in sample_rates:
            # Act
            wav_data = await service_wav.convert_pcm_to_format(pcm_data, output_format="wav", sample_rate=sample_rate)
            
            # Assert
            parsed_sample_rate = int.from_bytes(wav_data[24:28], 'little')
            assert parsed_sample_rate == sample_rate, f"Sample rate should be {sample_rate}"

    @pytest.mark.asyncio
    async def test_handles_empty_pcm_data(self, service_wav, service_webm):
        """Test conversion with empty PCM data."""
        # Arrange
        pcm_data = b''
        
        # Act
        wav_result = await service_wav.convert_pcm_to_format(pcm_data, output_format="wav")
        webm_result = await service_webm.convert_pcm_to_format(pcm_data, output_format="webm")
        
        # Assert
        # WAV should still generate header
        assert len(wav_result) == 44, "WAV should generate 44-byte header for empty data"
        # WebM might be empty or minimal
        assert isinstance(webm_result, bytes), "Should return bytes"

    @pytest.mark.asyncio
    async def test_invalid_format_returns_empty(self, service_wav):
        """Test that invalid format returns empty bytes."""
        # Arrange
        pcm_data = bytes([0, 0] * 100)
        
        # Act
        result = await service_wav.convert_pcm_to_format(pcm_data, output_format="invalid")  # type: ignore
        
        # Assert
        assert result == b'', "Should return empty bytes for invalid format"

    @pytest.mark.asyncio
    async def test_wav_preserves_pcm_alignment(self, service_wav):
        """Test that WAV conversion preserves PCM16 2-byte alignment."""
        # Arrange - Odd number of bytes (should not happen in practice)
        pcm_data = bytes([0] * 99)  # 99 bytes (not aligned to 2)
        
        # Act
        wav_data = await service_wav.convert_pcm_to_format(pcm_data, output_format="wav")
        
        # Assert
        data_size = int.from_bytes(wav_data[40:44], 'little')
        assert data_size == 99, "Should preserve original data size even if misaligned"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

