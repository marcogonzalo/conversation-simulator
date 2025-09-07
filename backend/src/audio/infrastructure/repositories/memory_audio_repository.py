"""
In-memory audio repository for development and testing.
"""
from typing import List, Optional, Dict
from datetime import datetime

from ...domain.entities.audio_chunk import AudioChunk
from ...domain.repositories.audio_repository import AudioRepository
from ...domain.value_objects.audio_id import AudioId


class MemoryAudioRepository(AudioRepository):
    """In-memory implementation of audio repository."""
    
    def __init__(self):
        self._chunks: Dict[str, AudioChunk] = {}
        self._sequence_index: Dict[int, str] = {}  # sequence_number -> chunk_id
    
    async def save_chunk(self, chunk: AudioChunk) -> None:
        """Save an audio chunk."""
        self._chunks[str(chunk.id)] = chunk
        self._sequence_index[chunk.sequence_number] = str(chunk.id)
    
    async def get_chunk(self, chunk_id: AudioId) -> Optional[AudioChunk]:
        """Get an audio chunk by ID."""
        return self._chunks.get(str(chunk_id))
    
    async def get_chunks_by_sequence(self, start_sequence: int, end_sequence: int) -> List[AudioChunk]:
        """Get audio chunks by sequence range."""
        chunks = []
        for seq_num in range(start_sequence, end_sequence + 1):
            chunk_id = self._sequence_index.get(seq_num)
            if chunk_id and chunk_id in self._chunks:
                chunks.append(self._chunks[chunk_id])
        return chunks
    
    async def delete_chunk(self, chunk_id: AudioId) -> None:
        """Delete an audio chunk."""
        chunk = self._chunks.get(str(chunk_id))
        if chunk:
            del self._sequence_index[chunk.sequence_number]
            del self._chunks[str(chunk_id)]
    
    async def cleanup_old_chunks(self, older_than: datetime) -> int:
        """Clean up old audio chunks and return count of deleted chunks."""
        deleted_count = 0
        chunks_to_delete = []
        
        for chunk_id, chunk in self._chunks.items():
            if chunk.timestamp < older_than:
                chunks_to_delete.append(chunk_id)
        
        for chunk_id in chunks_to_delete:
            chunk = self._chunks[chunk_id]
            del self._sequence_index[chunk.sequence_number]
            del self._chunks[chunk_id]
            deleted_count += 1
        
        return deleted_count
    
    async def get_all_chunks(self) -> List[AudioChunk]:
        """Get all audio chunks (for testing)."""
        return list(self._chunks.values())
    
    async def clear(self) -> None:
        """Clear all chunks (for testing)."""
        self._chunks.clear()
        self._sequence_index.clear()
