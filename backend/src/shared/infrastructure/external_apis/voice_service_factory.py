"""
Factory for creating voice AI services.
"""
import logging
from typing import Optional

from src.shared.domain.interfaces.voice_service_interface import VoiceServiceInterface
from src.shared.infrastructure.external_apis.api_config import api_config

logger = logging.getLogger(__name__)


class VoiceServiceFactory:
    """Factory for creating voice AI services based on configuration."""
    
    @staticmethod
    def create_voice_service(
        voice_provider: str = None,
        api_config_instance = None
    ) -> Optional[VoiceServiceInterface]:
        """
        Create voice service based on configuration or parameters.
        
        Args:
            voice_provider: Provider name ('openai', 'gemini', etc.). If None, uses api_config.
            api_config_instance: APIConfig instance. If None, uses global api_config.
            
        Returns:
            VoiceServiceInterface implementation or None if failed
        """
        try:
            # Use provided parameters or fall back to configuration
            provider = (voice_provider or api_config.voice_ai_provider).lower()
            config = api_config_instance or api_config
            
            if provider == "openai":
                return VoiceServiceFactory._create_openai_voice_service(config)
            elif provider == "gemini":
                return VoiceServiceFactory._create_gemini_voice_service(config)
            else:
                logger.error(f"Unsupported voice AI provider: {provider}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to create voice AI service: {e}")
            return None
    
    @staticmethod
    def _create_openai_voice_service(config) -> Optional[VoiceServiceInterface]:
        """Create OpenAI voice service."""
        try:
            from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
            
            if not config.openai_api_key:
                logger.error("OpenAI API key not configured")
                return None
            
            return OpenAIVoiceService(api_config=config)
        
        except Exception as e:
            logger.error(f"Failed to create OpenAI voice service: {e}")
            return None
    
    @staticmethod
    def _create_gemini_voice_service(config) -> Optional[VoiceServiceInterface]:
        """Create Gemini voice service."""
        try:
            from src.audio.infrastructure.services.gemini_voice_service import GeminiVoiceService
            
            if not config.gemini_api_key:
                logger.error("Gemini API key not configured")
                return None
            
            return GeminiVoiceService(api_config=config)
        
        except Exception as e:
            logger.error(f"Failed to create Gemini voice service: {e}")
            return None
    
    @staticmethod
    def get_available_voice_providers() -> list:
        """Get list of available voice AI providers."""
        return ["openai", "gemini"]
    
    @staticmethod
    def validate_voice_provider(provider: str) -> bool:
        """Validate if voice provider is supported."""
        return provider.lower() in VoiceServiceFactory.get_available_voice_providers()

