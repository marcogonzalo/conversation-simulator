"""
Audio format value object.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Union


class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    WEBM = "webm"
    OGG = "ogg"


@dataclass(frozen=True)
class AudioFormatVO:
    """Value object for audio format."""
    
    format: AudioFormat
    sample_rate: int
    channels: int
    bit_depth: int = 16
    
    def __post_init__(self):
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels <= 0:
            raise ValueError("Channels must be positive")
        if self.bit_depth <= 0:
            raise ValueError("Bit depth must be positive")
    
    @classmethod
    def from_string(cls, format_str: str, sample_rate: int = 44100, channels: int = 1, bit_depth: int = 16) -> 'AudioFormatVO':
        """Create AudioFormatVO from string."""
        try:
            audio_format = AudioFormat(format_str.lower())
            return cls(audio_format, sample_rate, channels, bit_depth)
        except ValueError:
            raise ValueError(f"Unsupported audio format: {format_str}")
    
    def to_mime_type(self) -> str:
        """Convert to MIME type."""
        mime_types = {
            AudioFormat.WAV: "audio/wav",
            AudioFormat.MP3: "audio/mpeg",
            AudioFormat.M4A: "audio/mp4",
            AudioFormat.WEBM: "audio/webm",
            AudioFormat.OGG: "audio/ogg"
        }
        return mime_types[self.format]
    
    def __str__(self) -> str:
        return f"{self.format.value}_{self.sample_rate}Hz_{self.channels}ch_{self.bit_depth}bit"
