"""
Factory for creating text-based AI services.

This factory handles text-based AI providers (OpenAI, Gemini, etc.)
For voice-based AI services, use VoiceServiceFactory instead.
"""
import logging
from typing import Optional, Dict, Any

from src.shared.domain.interfaces.ai_service_interface import AIServiceInterface
from src.shared.infrastructure.external_apis.api_config import api_config
from src.shared.infrastructure.external_apis.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """
    Factory for creating text-based AI services.
    
    Supports multiple providers and is designed to be easily extended.
    To add a new provider:
    1. Implement AIServiceInterface
    2. Add provider name to _SUPPORTED_PROVIDERS
    3. Add API key getter to _get_api_key_for_provider()
    4. Add factory method _create_<provider>_service()
    5. Add case to create_ai_service()
    """
    
    # Registry of supported text AI providers
    _SUPPORTED_PROVIDERS = ["openai"]  # Will expand: ["openai", "gemini", "anthropic", ...]
    
    @staticmethod
    def create_ai_service(
        ai_provider: str = None, 
        api_key: str = None,
        model: str = None,
        **kwargs
    ) -> Optional[AIServiceInterface]:
        """
        Create text-based AI service based on configuration or parameters.
        
        Args:
            ai_provider: Provider name ('openai', 'gemini', etc.). If None, uses api_config.
            api_key: API key for the provider. If None, retrieved from config.
            model: Model name. If None, uses provider default from config.
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIServiceInterface implementation or None if failed
        """
        try:
            # Use provided parameters or fall back to configuration
            provider = (ai_provider or api_config.text_ai_provider).lower()
            key = api_key or AIServiceFactory._get_api_key_for_provider(provider)
            
            if not key:
                logger.error(f"No API key found for text AI provider: {provider}")
                return None
            
            # Route to appropriate factory method
            if provider == "openai":
                return AIServiceFactory._create_openai_service(key, model, **kwargs)
            # Future providers:
            # elif provider == "gemini":
            #     return AIServiceFactory._create_gemini_service(key, model, **kwargs)
            # elif provider == "anthropic":
            #     return AIServiceFactory._create_anthropic_service(key, model, **kwargs)
            else:
                logger.error(f"Unsupported text AI provider: {provider}")
                logger.info(f"Supported providers: {AIServiceFactory._SUPPORTED_PROVIDERS}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to create text AI service: {e}")
            return None
    
    @staticmethod
    def _get_api_key_for_provider(provider: str) -> Optional[str]:
        """
        Get API key for the specified provider from configuration.
        
        To add a new provider, add a case here that retrieves the key from api_config.
        """
        if provider == "openai":
            return api_config.openai_api_key
        # Future providers:
        # elif provider == "gemini":
        #     return api_config.gemini_api_key
        # elif provider == "anthropic":
        #     return api_config.anthropic_api_key
        return None
    
    @staticmethod
    def _create_openai_service(
        api_key: str, 
        model: str = None,
        **kwargs
    ) -> Optional[OpenAIService]:
        """Create OpenAI text service."""
        try:
            return OpenAIService(
                api_key=api_key,
                model=model or api_config.openai_model
            )
        except Exception as e:
            logger.error(f"Failed to create OpenAI service: {e}")
            return None
    
    # Future provider factory methods will go here:
    # @staticmethod
    # def _create_gemini_service(api_key: str, model: str = None, **kwargs) -> Optional[GeminiService]:
    #     """Create Gemini text service."""
    #     try:
    #         from src.shared.infrastructure.external_apis.gemini_service import GeminiService
    #         return GeminiService(api_key=api_key, model=model or api_config.gemini_model)
    #     except Exception as e:
    #         logger.error(f"Failed to create Gemini service: {e}")
    #         return None
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available text AI providers."""
        return AIServiceFactory._SUPPORTED_PROVIDERS.copy()
    
    @staticmethod
    def validate_provider(provider: str) -> bool:
        """Validate if text AI provider is supported."""
        return provider.lower() in AIServiceFactory._SUPPORTED_PROVIDERS
    
    @staticmethod
    def get_provider_info() -> Dict[str, Any]:
        """Get information about available providers and their configuration."""
        return {
            "supported_providers": AIServiceFactory._SUPPORTED_PROVIDERS,
            "current_provider": api_config.text_ai_provider,
            "configured_providers": [
                p for p in AIServiceFactory._SUPPORTED_PROVIDERS
                if AIServiceFactory._get_api_key_for_provider(p) is not None
            ]
        }
    
    @staticmethod
    def create_conversation_service(ai_provider: str = None, api_key: str = None):
        """Create AI conversation service."""
        from src.conversation.infrastructure.services.ai_conversation_service import AIConversationService
        return AIConversationService(ai_provider, api_key)
    
    @staticmethod
    def create_analysis_service(ai_provider: str = None, api_key: str = None):
        """Create AI analysis service."""
        from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService
        return ConversationAnalysisService(ai_provider, api_key)
