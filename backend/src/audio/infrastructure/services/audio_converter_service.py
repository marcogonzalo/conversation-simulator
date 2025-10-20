"""
Audio Converter Service
Provides configurable audio format conversion (PCM16 to WAV or WebM)
"""
import logging
import subprocess
import tempfile
import os
import struct
from typing import Literal

logger = logging.getLogger(__name__)

AudioFormat = Literal["wav", "webm"]


class AudioConverterService:
    """Service for converting PCM16 audio to various formats."""
    
    def __init__(self, default_format: AudioFormat = "webm"):
        """
        Initialize audio converter service.
        
        Args:
            default_format: Default output format ('wav' or 'webm')
        """
        self.default_format = default_format
        logger.info(f"AudioConverterService initialized with default format: {default_format}")
    
    async def convert_pcm_to_format(
        self,
        pcm_data: bytes,
        output_format: AudioFormat | None = None,
        sample_rate: int = 24000
    ) -> bytes:
        """
        Convert PCM16 audio data to specified format.
        
        Args:
            pcm_data: Raw PCM16 audio data
            output_format: Target format ('wav' or 'webm'), uses default if None
            sample_rate: Sample rate in Hz (default: 24000)
            
        Returns:
            Converted audio data as bytes
        """
        format_to_use = output_format or self.default_format
        
        if format_to_use == "wav":
            return await self._convert_to_wav(pcm_data, sample_rate)
        elif format_to_use == "webm":
            return await self._convert_to_webm(pcm_data, sample_rate)
        else:
            logger.error(f"Unsupported audio format: {format_to_use}")
            return b''
    
    async def _convert_to_wav(self, pcm_data: bytes, sample_rate: int = 24000) -> bytes:
        """
        Convert PCM16 to WAV format.
        
        WAV characteristics:
        - Simple format (header + raw PCM data)
        - No encoding latency
        - Larger file size
        - Better for single large files
        - Can have decode issues with many small chunks in Chrome
        
        Args:
            pcm_data: Raw PCM16 audio data
            sample_rate: Sample rate in Hz
            
        Returns:
            WAV file data (header + PCM)
        """
        try:
            # WAV file header configuration
            num_channels = 1  # Mono
            bits_per_sample = 16  # PCM16
            byte_rate = sample_rate * num_channels * bits_per_sample // 8
            block_align = num_channels * bits_per_sample // 8
            data_size = len(pcm_data)
            
            # Build WAV header (44 bytes)
            wav_header = struct.pack(
                '<4sI4s4sIHHIIHH4sI',
                b'RIFF',
                36 + data_size,  # File size - 8
                b'WAVE',
                b'fmt ',
                16,  # fmt chunk size
                1,   # Audio format (1 = PCM)
                num_channels,
                sample_rate,
                byte_rate,
                block_align,
                bits_per_sample,
                b'data',
                data_size
            )
            
            logger.debug(f"Converted {len(pcm_data)} bytes PCM to WAV (sample_rate={sample_rate}Hz)")
            return wav_header + pcm_data
                    
        except Exception as e:
            logger.error(f"Error converting PCM to WAV: {e}")
            return b''
    
    async def _convert_to_webm(self, pcm_data: bytes, sample_rate: int = 24000) -> bytes:
        """
        Convert PCM16 to WebM/Opus format using ffmpeg.
        
        WebM characteristics:
        - Compressed format (smaller files)
        - Better for streaming multiple chunks
        - Chrome handles it better over time
        - Slight quality loss due to compression
        - Requires ffmpeg processing
        
        Args:
            pcm_data: Raw PCM16 audio data
            sample_rate: Sample rate in Hz
            
        Returns:
            WebM file data
        """
        try:
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(suffix='.pcm', delete=False) as pcm_file:
                pcm_file.write(pcm_data)
                pcm_path = pcm_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                webm_path = webm_file.name
            
            try:
                # Use ffmpeg to convert PCM16 to WebM with Opus codec
                cmd = [
                    'ffmpeg',
                    '-f', 's16le',  # Input format: signed 16-bit little-endian PCM
                    '-ar', str(sample_rate),  # Sample rate
                    '-ac', '1',  # Mono channel
                    '-i', pcm_path,  # Input file
                    '-c:a', 'libopus',  # Audio codec: Opus
                    '-b:a', '32k',  # Bitrate for good quality
                    '-application', 'voip',  # Optimize for voice
                    '-f', 'webm',  # Output format
                    '-y',  # Overwrite output file
                    webm_path  # Output file
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    return b''
                
                # Read the converted WebM file
                with open(webm_path, 'rb') as f:
                    webm_data = f.read()
                
                logger.debug(f"Converted {len(pcm_data)} bytes PCM to {len(webm_data)} bytes WebM (sample_rate={sample_rate}Hz)")
                return webm_data
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(pcm_path)
                    os.unlink(webm_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error converting PCM to WebM: {e}")
            return b''

