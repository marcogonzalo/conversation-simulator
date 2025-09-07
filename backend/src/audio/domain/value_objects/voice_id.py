"""
Voice ID value object for TTS.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VoiceId:
    """Value object for Voice ID."""
    
    value: str
    name: Optional[str] = None
    language: Optional[str] = None
    accent: Optional[str] = None
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Voice ID cannot be empty")
    
    @classmethod
    def from_string(cls, value: str, name: Optional[str] = None, language: Optional[str] = None, accent: Optional[str] = None) -> 'VoiceId':
        """Create Voice ID from string."""
        return cls(value, name, language, accent)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VoiceId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
