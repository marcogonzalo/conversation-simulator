"""
Process audio command.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from ...domain.entities.audio_chunk import AudioChunk
from ...domain.value_objects.audio_format import AudioFormatVO
from ...domain.value_objects.voice_id import VoiceId


@dataclass
class ProcessAudioCommand:
    """Command to process audio data."""
    
    audio_chunks: List[AudioChunk]
    operation: str  # "stt" or "tts"
    voice_id: Optional[VoiceId] = None
    text: Optional[str] = None
    language: str = "es"
    format: Optional[AudioFormatVO] = None
    conversation_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        
        if self.operation not in ["stt", "tts"]:
            raise ValueError("Operation must be 'stt' or 'tts'")
        
        if self.operation == "tts" and not self.text:
            raise ValueError("Text is required for TTS operation")
        
        if self.operation == "stt" and not self.audio_chunks:
            raise ValueError("Audio chunks are required for STT operation")
