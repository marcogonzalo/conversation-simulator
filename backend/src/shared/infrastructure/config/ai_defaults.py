"""
Default configuration values for AI services.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TextAIDefaults:
    temperature: float = 0.7
    max_tokens: int = 10000


@dataclass(frozen=True)
class VoiceAIDefaults:
    temperature: float = 0.7
    max_tokens: int = 4096


TEXT_AI_DEFAULTS = TextAIDefaults()
VOICE_AI_DEFAULTS = VoiceAIDefaults()


