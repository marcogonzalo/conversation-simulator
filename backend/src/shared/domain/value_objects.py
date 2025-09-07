"""
Shared value objects for the conversation simulator.
"""
from dataclasses import dataclass
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EntityId:
    """Base class for entity IDs."""
    value: UUID
    
    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError("EntityId value must be a UUID")
    
    def __str__(self) -> str:
        return str(self.value)
    
    @classmethod
    def generate(cls) -> 'EntityId':
        """Generate a new random ID."""
        return cls(uuid4())


@dataclass(frozen=True)
class ConversationId(EntityId):
    """Value object for conversation IDs."""
    pass


@dataclass(frozen=True)
class PersonaId(EntityId):
    """Value object for persona IDs."""
    pass


@dataclass(frozen=True)
class AnalysisId(EntityId):
    """Value object for analysis IDs."""
    pass


@dataclass(frozen=True)
class MessageContent:
    """Value object for message content."""
    text: str
    
    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Message content cannot be empty")
        if len(self.text) > 10000:
            raise ValueError("Message content too long")
    
    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class AudioData:
    """Value object for audio data."""
    data: bytes
    sample_rate: int = 44100
    channels: int = 1
    
    def __post_init__(self):
        if not self.data:
            raise ValueError("Audio data cannot be empty")
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels <= 0:
            raise ValueError("Channels must be positive")


@dataclass(frozen=True)
class MetricScore:
    """Value object for metric scores."""
    value: float
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 100.0:
            raise ValueError("Metric score must be between 0.0 and 100.0")
    
    def __str__(self) -> str:
        return f"{self.value:.1f}"


@dataclass(frozen=True)
class Recommendation:
    """Value object for recommendations."""
    text: str
    category: str
    priority: int = 1  # 1 = high, 2 = medium, 3 = low
    
    def __post_init__(self):
        if not self.text or not self.text.strip():
            raise ValueError("Recommendation text cannot be empty")
        if not self.category or not self.category.strip():
            raise ValueError("Recommendation category cannot be empty")
        if not 1 <= self.priority <= 3:
            raise ValueError("Priority must be between 1 and 3")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'text': self.text,
            'category': self.category,
            'priority': self.priority
        }
