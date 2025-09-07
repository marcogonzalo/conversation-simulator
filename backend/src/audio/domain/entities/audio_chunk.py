"""
Audio chunk entity for streaming audio data.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ..value_objects.audio_id import AudioId
from ..value_objects.audio_format import AudioFormatVO


@dataclass
class AudioChunk:
    """Entity representing a chunk of audio data."""
    
    id: AudioId
    data: bytes
    format: AudioFormatVO
    sequence_number: int
    timestamp: datetime
    is_final: bool = False
    duration_ms: Optional[int] = None
    
    def __post_init__(self):
        if not self.data:
            raise ValueError("Audio data cannot be empty")
        if self.sequence_number < 0:
            raise ValueError("Sequence number must be non-negative")
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError("Duration must be non-negative")
    
    @property
    def size_bytes(self) -> int:
        """Get the size of the audio data in bytes."""
        return len(self.data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "data": self.data.hex(),  # Convert bytes to hex string
            "format": {
                "format": self.format.format.value,
                "sample_rate": self.format.sample_rate,
                "channels": self.format.channels,
                "bit_depth": self.format.bit_depth
            },
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp.isoformat(),
            "is_final": self.is_final,
            "duration_ms": self.duration_ms,
            "size_bytes": self.size_bytes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AudioChunk':
        """Create AudioChunk from dictionary."""
        return cls(
            id=AudioId.from_string(data["id"]),
            data=bytes.fromhex(data["data"]),
            format=AudioFormatVO.from_string(
                data["format"]["format"],
                data["format"]["sample_rate"],
                data["format"]["channels"],
                data["format"]["bit_depth"]
            ),
            sequence_number=data["sequence_number"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            is_final=data.get("is_final", False),
            duration_ms=data.get("duration_ms")
        )
