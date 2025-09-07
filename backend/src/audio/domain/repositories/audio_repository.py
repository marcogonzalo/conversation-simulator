"""
Audio repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.audio_chunk import AudioChunk
from ..value_objects.audio_id import AudioId


class AudioRepository(ABC):
    """Abstract repository for audio data."""
    
    @abstractmethod
    async def save_chunk(self, chunk: AudioChunk) -> None:
        """Save an audio chunk."""
        pass
    
    @abstractmethod
    async def get_chunk(self, chunk_id: AudioId) -> Optional[AudioChunk]:
        """Get an audio chunk by ID."""
        pass
    
    @abstractmethod
    async def get_chunks_by_sequence(self, start_sequence: int, end_sequence: int) -> List[AudioChunk]:
        """Get audio chunks by sequence range."""
        pass
    
    @abstractmethod
    async def delete_chunk(self, chunk_id: AudioId) -> None:
        """Delete an audio chunk."""
        pass
    
    @abstractmethod
    async def cleanup_old_chunks(self, older_than: datetime) -> int:
        """Clean up old audio chunks and return count of deleted chunks."""
        pass
