"""
Voice-to-Voice application service for real-time conversations.
Supports multiple voice AI providers through abstraction.
"""
import logging
import asyncio
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from ...domain.repositories.audio_repository import AudioRepository
from ....shared.domain.interfaces.voice_service_interface import VoiceServiceInterface
from ....shared.infrastructure.external_apis.voice_service_factory import VoiceServiceFactory
from ....shared.infrastructure.external_apis.api_config import APIConfig

logger = logging.getLogger(__name__)


class VoiceApplicationService:
    """
    Application service for voice-to-voice operations.
    Provider-agnostic - works with any VoiceServiceInterface implementation.
    """
    
    def __init__(
        self,
        audio_repository: AudioRepository,
        api_config: APIConfig,
        voice_provider: str = None
    ):
        self.audio_repository = audio_repository
        self.api_config = api_config
        self.voice_provider = voice_provider or api_config.voice_ai_provider
        
        # Create voice service at initialization (configured provider)
        self.voice_service: Optional[VoiceServiceInterface] = VoiceServiceFactory.create_voice_service(
            voice_provider=self.voice_provider,
            api_config_instance=self.api_config
        )
        
        if not self.voice_service:
            logger.error(f"Failed to create voice service for provider: {self.voice_provider}")
            raise ValueError(f"Voice provider {self.voice_provider} not available")
        
        self.is_connected = False
        self.conversation_id: Optional[str] = None
        
    async def start_conversation(
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
        Start a voice-to-voice conversation using configured provider.
        
        Args:
            conversation_id: Unique conversation identifier
            instructions: System instructions/prompt (already generated)
            voice_id: Voice identifier for the provider
            on_audio_chunk: Callback for audio chunks
            on_transcript: Callback for transcripts
            on_error: Callback for errors
            on_audio_complete: Optional callback when audio is complete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.conversation_id = conversation_id
            
            # Initialize the service (async context manager entry)
            await self.voice_service.__aenter__()
            
            # Connect with instructions and voice ID (no business logic here)
            success = await self.voice_service.connect(
                conversation_id=conversation_id,
                instructions=instructions,
                voice_id=voice_id,
                on_audio_chunk=on_audio_chunk,
                on_transcript=on_transcript,
                on_error=on_error,
                on_audio_complete=on_audio_complete
            )
            
            if success:
                self.is_connected = True
                logger.info(f"Started voice conversation for {conversation_id} using {self.voice_service.provider}")
            else:
                logger.error(f"Failed to start voice conversation for {conversation_id}")
            
            return success
                
        except Exception as e:
            logger.error(f"Error starting voice conversation: {e}")
            on_error(f"Failed to start conversation: {str(e)}")
            return False
    
    async def send_audio(self, audio_data: bytes) -> bool:
        """Send audio data to the voice service."""
        if not self.voice_service or not self.is_connected:
            logger.warning("Voice service not connected")
            return False
        
        try:
            return await self.voice_service.send_audio(audio_data)
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            return False
    
    async def end_conversation(self):
        """End the current voice conversation."""
        if self.voice_service and self.is_connected:
            try:
                await self.voice_service.disconnect()
                # Properly exit the async context manager
                await self.voice_service.__aexit__(None, None, None)
                logger.info(f"Ended voice conversation for {self.conversation_id}")
            except Exception as e:
                logger.error(f"Error ending voice conversation: {e}")
        
        self.is_connected = False
        self.conversation_id = None
        self.voice_service = None
    
    
    def get_voice_for_accent(self, accent: str) -> str:
        """
        Map persona accent to provider-specific voice ID.
        Delegates to the underlying voice service.
        
        Args:
            accent: Standard accent key (e.g., "mexicano", "neutral")
            
        Returns:
            Provider-specific voice ID
        """
        if not self.voice_service:
            logger.warning(f"Voice service not available, returning default")
            return "alloy"  # Safe default
        
        return self.voice_service.get_voice_for_accent(accent)
    
    async def is_healthy(self) -> bool:
        """Check if the voice service is healthy."""
        return self.is_connected and self.voice_service is not None
    
    @property
    def current_provider(self) -> str:
        """Get the current voice provider name."""
        if self.voice_service:
            return self.voice_service.provider
        return self.voice_provider


# Backward compatibility alias
OpenAIVoiceApplicationService = VoiceApplicationService
