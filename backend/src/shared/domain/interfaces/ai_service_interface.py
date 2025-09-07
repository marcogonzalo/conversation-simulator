"""
Abstract interface for AI services.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AIServiceInterface(ABC):
    """Abstract interface for AI services."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using AI service."""
        pass
    
    @abstractmethod
    async def generate_conversation_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate conversation response with context."""
        pass
    
    @abstractmethod
    async def analyze_conversation(
        self,
        conversation_data: Dict[str, Any],
        analysis_prompt: str
    ) -> Dict[str, Any]:
        """Analyze conversation using AI."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if AI service is accessible."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the model name."""
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Get the provider name."""
        pass
