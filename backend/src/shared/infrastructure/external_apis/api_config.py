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
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Audio settings
        self.audio_channels = int(os.getenv("AUDIO_CHANNELS", "1"))
        self.audio_playback_sample_rate = int(os.getenv("AUDIO_PLAYBACK_SAMPLE_RATE", "24000"))  # Playback sample rate for frontend
        # Audio output format for AI responses: 'webm' (default, compressed, better for streaming) or 'wav' (uncompressed, larger)
        self.audio_output_format = os.getenv("AUDIO_OUTPUT_FORMAT", "webm")

        
        # AI settings (for fallback text conversations)
        # Separate providers for text and voice AI
        self.text_ai_provider = os.getenv("TEXT_AI_PROVIDER", os.getenv("AI_PROVIDER", "openai"))
        self.voice_ai_provider = os.getenv("VOICE_AI_PROVIDER", os.getenv("AI_PROVIDER", "openai"))
        
        # Legacy compatibility
        self.ai_provider = self.text_ai_provider  # For backward compatibility
        
        # Text AI model settings
        self.ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # For OpenAI service factory
        self.ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.ai_max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))
        
        # OpenAI Voice-to-Voice settings
        self.openai_voice_model = os.getenv("OPENAI_VOICE_MODEL", "4o-mini-realtime-preview")
        self.openai_voice_temperature = float(os.getenv("OPENAI_VOICE_TEMPERATURE", "0.8"))
        self.openai_voice_max_tokens = int(os.getenv("OPENAI_VOICE_MAX_TOKENS", "4096"))
        self.openai_voice_input_format = os.getenv("OPENAI_VOICE_INPUT_FORMAT", "pcm16")
        self.openai_voice_output_format = os.getenv("OPENAI_VOICE_OUTPUT_FORMAT", "pcm16")
        self.openai_voice_default_voice = os.getenv("OPENAI_VOICE_DEFAULT_VOICE", "alloy")
        
        # Voice detection settings
        self.voice_detection_threshold = float(os.getenv("VOICE_DETECTION_THRESHOLD", "0.5"))
        self.voice_detection_prefix_padding_ms = int(os.getenv("VOICE_DETECTION_PREFIX_PADDING_MS", "300"))
        self.voice_detection_silence_duration_ms = int(os.getenv("VOICE_DETECTION_SILENCE_DURATION_MS", "500"))
        
        # Audio filtering settings (configurable values)
        # These values are related as follows:
        # - audio_min_duration_ms is the minimum audio duration required by OpenAI (100ms).
        # - audio_min_bytes_pcm is the minimum number of bytes for 100ms of PCM16 audio at 24kHz (24,000 samples/sec * 2 bytes/sample * 0.1 sec = 4,800 bytes).
        # - audio_min_bytes_webm is the estimated minimum number of bytes for 100ms of WebM/Opus audio at 32kbps (32,000 bits/sec * 0.1 sec / 8 bits/byte = 400 bytes).
        self.audio_min_duration_ms = 100
        self.audio_min_bytes_pcm = 4800
        self.audio_min_bytes_webm = 400
        
        # Conversation settings
        self.max_conversation_duration = int(os.getenv("MAX_CONVERSATION_DURATION", "1200"))  # 20 minutes
        self.max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH", "10000"))
        
        # Analysis settings
        self.analysis_timeout = int(os.getenv("ANALYSIS_TIMEOUT", "300"))  # 5 minutes
        self.analysis_retry_attempts = int(os.getenv("ANALYSIS_RETRY_ATTEMPTS", "3"))
        
        # Prompt validation settings
        self.prompt_strict_validation = os.getenv("PROMPT_STRICT_VALIDATION", "false").lower() == "true"
    
    def validate_config(self) -> bool:
        """Validate API configuration."""
        required_keys = ["OPENAI_API_KEY"]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"Missing required environment variables: {missing_keys}")
            return False
        
        logger.info("API configuration validated successfully")
        return True
    
    def get_openai_voice_config(self) -> Dict[str, Any]:
        """Get OpenAI voice configuration."""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_voice_model,
            "temperature": self.openai_voice_temperature,
            "max_tokens": self.openai_voice_max_tokens,
            "input_format": self.openai_voice_input_format,
            "output_format": self.openai_voice_output_format,
            "default_voice": self.openai_voice_default_voice,
            "voice_detection": {
                "threshold": self.voice_detection_threshold,
                "prefix_padding_ms": self.voice_detection_prefix_padding_ms,
                "silence_duration_ms": self.voice_detection_silence_duration_ms
            }
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
            "sample_rate": self.audio_playback_sample_rate,
            "channels": self.audio_channels,
            "output_format": self.audio_output_format,
            "min_duration_ms": self.audio_min_duration_ms,
            "min_bytes_pcm": self.audio_min_bytes_pcm,
            "min_bytes_webm": self.audio_min_bytes_webm
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
            "openai_voice": self.get_openai_voice_config(),
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
