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


@dataclass(frozen=True)
class OpenAIVoiceDefaults:
    """Default configuration for OpenAI voice services."""
    temperature: float = 0.8
    max_tokens: int = 4096
    default_voice: str = "alloy"


@dataclass(frozen=True)
class GeminiVoiceDefaults:
    """Default configuration for Gemini voice services."""
    temperature: float = 0.8
    max_tokens: int = 4096
    default_voice: str = "Puck"


TEXT_AI_DEFAULTS = TextAIDefaults()
VOICE_AI_DEFAULTS = VoiceAIDefaults()
OPENAI_VOICE_DEFAULTS = OpenAIVoiceDefaults()
GEMINI_VOICE_DEFAULTS = GeminiVoiceDefaults()


