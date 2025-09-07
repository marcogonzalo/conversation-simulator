"""
Audio domain service for business logic.
"""
from typing import List, Optional
from datetime import datetime, timedelta

from ..entities.audio_chunk import AudioChunk
from ..value_objects.audio_format import AudioFormatVO


class AudioDomainService:
    """Domain service for audio-related business logic."""
    
    @staticmethod
    def validate_audio_quality(chunks: List[AudioChunk], target_latency_ms: int = 500) -> bool:
        """Validate that audio chunks meet quality requirements."""
        if not chunks:
            return False
        
        # Check if all chunks have the same format
        first_format = chunks[0].format
        for chunk in chunks[1:]:
            if chunk.format != first_format:
                return False
        
        # Check latency requirements
        if len(chunks) > 1:
            time_diff = (chunks[-1].timestamp - chunks[0].timestamp).total_seconds() * 1000
            if time_diff > target_latency_ms:
                return False
        
        return True
    
    @staticmethod
    def calculate_audio_duration(chunks: List[AudioChunk]) -> int:
        """Calculate total duration of audio chunks in milliseconds."""
        if not chunks:
            return 0
        
        total_duration = 0
        for chunk in chunks:
            if chunk.duration_ms:
                total_duration += chunk.duration_ms
            else:
                # Estimate duration based on data size and format
                bytes_per_second = (chunk.format.sample_rate * chunk.format.channels * chunk.format.bit_depth) // 8
                estimated_duration = (chunk.size_bytes / bytes_per_second) * 1000
                total_duration += int(estimated_duration)
        
        return total_duration
    
    @staticmethod
    def merge_audio_chunks(chunks: List[AudioChunk]) -> bytes:
        """Merge audio chunks into a single audio stream."""
        if not chunks:
            return b""
        
        # Sort chunks by sequence number
        sorted_chunks = sorted(chunks, key=lambda x: x.sequence_number)
        
        # Concatenate audio data
        merged_data = b""
        for chunk in sorted_chunks:
            merged_data += chunk.data
        
        return merged_data
    
    @staticmethod
    def split_audio_data(data: bytes, chunk_size: int, format: AudioFormatVO) -> List[bytes]:
        """Split audio data into chunks of specified size."""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def validate_audio_format(format: AudioFormatVO) -> bool:
        """Validate audio format parameters."""
        # Check sample rate
        if format.sample_rate not in [8000, 16000, 22050, 44100, 48000]:
            return False
        
        # Check channels
        if format.channels not in [1, 2]:
            return False
        
        # Check bit depth
        if format.bit_depth not in [8, 16, 24, 32]:
            return False
        
        return True
