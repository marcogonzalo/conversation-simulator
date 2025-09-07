"""
Factory for creating AI services.
"""
import logging
from typing import Optional

from src.shared.domain.interfaces.ai_service_interface import AIServiceInterface
from src.shared.infrastructure.external_apis.api_config import api_config
from src.shared.infrastructure.external_apis.openai_service import OpenAIService
from src.shared.infrastructure.external_apis.claude_service import ClaudeService

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """Factory for creating AI services based on configuration."""
    
    @staticmethod
    def create_ai_service(ai_provider: str = None, api_key: str = None) -> Optional[AIServiceInterface]:
        """Create AI service based on configuration or parameters."""
        try:
            # Use provided parameters or fall back to configuration
            provider = (ai_provider or api_config.ai_provider).lower()
            key = api_key or AIServiceFactory._get_api_key_for_provider(provider)
            
            if not key:
                logger.error(f"No API key found for provider: {provider}")
                return None
            
            if provider == "openai":
                return AIServiceFactory._create_openai_service(key)
            elif provider == "claude":
                return AIServiceFactory._create_claude_service(key)
            else:
                logger.error(f"Unsupported AI provider: {provider}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to create AI service: {e}")
            return None
    
    @staticmethod
    def _get_api_key_for_provider(provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        if provider == "openai":
            return api_config.openai_api_key
        elif provider == "claude":
            return api_config.anthropic_api_key
        return None
    
    @staticmethod
    def _create_openai_service(api_key: str) -> Optional[OpenAIService]:
        """Create OpenAI service."""
        try:
            return OpenAIService(
                api_key=api_key,
                model=api_config.openai_model
            )
        
        except Exception as e:
            logger.error(f"Failed to create OpenAI service: {e}")
            return None
    
    @staticmethod
    def _create_claude_service(api_key: str) -> Optional[ClaudeService]:
        """Create Claude service."""
        try:
            return ClaudeService(
                api_key=api_key,
                model=api_config.claude_model
            )
        
        except Exception as e:
            logger.error(f"Failed to create Claude service: {e}")
            return None
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available AI providers."""
        return ["openai", "claude"]
    
    @staticmethod
    def validate_provider(provider: str) -> bool:
        """Validate if provider is supported."""
        return provider.lower() in AIServiceFactory.get_available_providers()
    
    @staticmethod
    def create_conversation_service(ai_provider: str = None, api_key: str = None):
        """Create AI conversation service."""
        from src.conversation.infrastructure.services.ai_conversation_service import AIConversationService
        return AIConversationService(ai_provider, api_key)
    
    @staticmethod
    def create_analysis_service(ai_provider: str = None, api_key: str = None):
        """Create AI analysis service."""
        from src.analysis.infrastructure.services.ai_analysis_service import AIAnalysisService
        return AIAnalysisService(ai_provider, api_key)
