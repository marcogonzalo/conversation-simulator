"""
Abstract interface for voice AI services.

This interface handles technical communication with voice AI providers.
Business logic (instructions) is handled by the orchestration layer, but
voice mapping is provider-specific and handled by each implementation.
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional


class VoiceServiceInterface(ABC):
    """
    Abstract interface for voice-to-voice AI services.
    
    This interface defines the technical operations needed to communicate
    with a voice AI provider. Prompt generation is handled in the orchestration
    layer, but voice mapping (accent -> voice_id) is provider-specific.
    """
    
    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
    
    @abstractmethod
    async def connect(
        self, 
        conversation_id: str,
        instructions: str,
        voice_id: str,
        on_audio_chunk: Callable[[bytes], None],
        on_transcript: Callable[[str], None],
        on_error: Callable[[str], None],
        on_audio_complete: Optional[Callable[[], None]] = None
    ) -> bool:
        """
        Connect to voice-to-voice service.
        
        Args:
            conversation_id: Unique conversation identifier
            instructions: System instructions/prompt (already generated)
            voice_id: Voice identifier for the provider
            on_audio_chunk: Callback for audio chunks received
            on_transcript: Callback for transcript updates
            on_error: Callback for errors
            on_audio_complete: Optional callback when audio response is complete
            
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from voice service."""
        pass
    
    @abstractmethod
    async def send_audio(self, audio_data: bytes) -> bool:
        """
        Send audio data to the voice service.
        
        Args:
            audio_data: Audio data bytes (format depends on provider)
            
        Returns:
            True if send successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_voice_for_accent(self, accent: str) -> str:
        """
        Map a standard accent key to a provider-specific voice ID.
        
        Each provider implements its own mapping from standard accent keys
        (e.g., "mexicano", "peruano", "caribeño", "neutral") to their
        specific voice IDs.
        
        Args:
            accent: Standard accent key
            
        Returns:
            Provider-specific voice ID (e.g., "alloy" for OpenAI)
        """
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Get the provider name (e.g., 'openai', 'gemini')."""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected to voice service."""
        pass

