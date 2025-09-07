"""
External API configuration for the application.
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class APIConfig:
    """Configuration class for external APIs."""
    
    def __init__(self):
        # API Keys
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Audio settings
        self.audio_sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
        self.audio_channels = int(os.getenv("AUDIO_CHANNELS", "1"))
        self.audio_format = os.getenv("AUDIO_FORMAT", "wav")
        
        # AI settings
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")  # openai, claude
        self.ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.ai_max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))
        
        # Model-specific settings
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
        
        # TTS settings
        self.tts_voice_id = os.getenv("TTS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Default voice
        self.tts_stability = float(os.getenv("TTS_STABILITY", "0.5"))
        self.tts_similarity_boost = float(os.getenv("TTS_SIMILARITY_BOOST", "0.8"))
        
        # STT settings
        self.stt_model = os.getenv("STT_MODEL", "whisper-1")
        self.stt_language = os.getenv("STT_LANGUAGE", "es")
        
        # Conversation settings
        self.max_conversation_duration = int(os.getenv("MAX_CONVERSATION_DURATION", "1200"))  # 20 minutes
        self.max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH", "10000"))
        
        # Analysis settings
        self.analysis_timeout = int(os.getenv("ANALYSIS_TIMEOUT", "300"))  # 5 minutes
        self.analysis_retry_attempts = int(os.getenv("ANALYSIS_RETRY_ATTEMPTS", "3"))
    
    def validate_config(self) -> bool:
        """Validate API configuration."""
        required_keys = [
            "ELEVENLABS_API_KEY"
        ]
        
        # Add AI API key based on provider
        if self.ai_provider == "openai":
            required_keys.append("OPENAI_API_KEY")
        elif self.ai_provider == "claude":
            required_keys.append("ANTHROPIC_API_KEY")
        else:
            logger.error(f"Unsupported AI provider: {self.ai_provider}")
            return False
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"Missing required environment variables: {missing_keys}")
            return False
        
        logger.info("API configuration validated successfully")
        return True
    
    def get_elevenlabs_config(self) -> Dict[str, Any]:
        """Get ElevenLabs configuration."""
        return {
            "api_key": self.elevenlabs_api_key,
            "voice_id": self.tts_voice_id,
            "stability": self.tts_stability,
            "similarity_boost": self.tts_similarity_boost,
            "sample_rate": self.audio_sample_rate
        }
    
    def get_anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic configuration."""
        return {
            "api_key": self.anthropic_api_key,
            "model": self.ai_model,
            "temperature": self.ai_temperature,
            "max_tokens": self.ai_max_tokens
        }
    
    def get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase configuration."""
        return {
            "url": self.supabase_url,
            "key": self.supabase_key
        }
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio configuration."""
        return {
            "sample_rate": self.audio_sample_rate,
            "channels": self.audio_channels,
            "format": self.audio_format
        }
    
    def get_conversation_config(self) -> Dict[str, Any]:
        """Get conversation configuration."""
        return {
            "max_duration": self.max_conversation_duration,
            "max_message_length": self.max_message_length
        }
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration."""
        return {
            "timeout": self.analysis_timeout,
            "retry_attempts": self.analysis_retry_attempts
        }
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration."""
        return {
            "elevenlabs": self.get_elevenlabs_config(),
            "anthropic": self.get_anthropic_config(),
            "supabase": self.get_supabase_config(),
            "audio": self.get_audio_config(),
            "conversation": self.get_conversation_config(),
            "analysis": self.get_analysis_config()
        }


class VoiceConfig:
    """Configuration for voice settings."""
    
    def __init__(self):
        self.voices = {
            "caribbean_spanish": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "name": "Cuban Spanish",
                "accent": "caribbean_spanish"
            },
            "peruvian_spanish": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Peruvian Spanish",
                "accent": "peruvian_spanish"
            },
            "venezuelan_spanish": {
                "voice_id": "VR6AewLTigWG4xSOukaG",
                "name": "Venezuelan Spanish",
                "accent": "venezuelan_spanish"
            },
            "florida_english": {
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "name": "Florida English",
                "accent": "florida_english"
            }
        }
    
    def get_voice_id(self, accent: str) -> Optional[str]:
        """Get voice ID for accent."""
        voice_config = self.voices.get(accent)
        return voice_config["voice_id"] if voice_config else None
    
    def get_voice_name(self, accent: str) -> Optional[str]:
        """Get voice name for accent."""
        voice_config = self.voices.get(accent)
        return voice_config["name"] if voice_config else None
    
    def get_all_voices(self) -> Dict[str, Dict[str, str]]:
        """Get all voice configurations."""
        return self.voices.copy()
    
    def get_voices_by_language(self, language: str) -> Dict[str, Dict[str, str]]:
        """Get voices by language."""
        if language == "spanish":
            return {
                k: v for k, v in self.voices.items()
                if "spanish" in k
            }
        elif language == "english":
            return {
                k: v for k, v in self.voices.items()
                if "english" in k
            }
        return {}


# Global API configuration
api_config = APIConfig()

# Global voice configuration
voice_config = VoiceConfig()
