"""
OpenAI Voice-to-Voice application service for real-time conversations.
"""
import logging
import asyncio
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from ...domain.repositories.audio_repository import AudioRepository
from ...infrastructure.services.openai_voice_service import OpenAIVoiceService
from ....shared.infrastructure.external_apis.api_config import APIConfig

logger = logging.getLogger(__name__)


class OpenAIVoiceApplicationService:
    """Application service for OpenAI voice-to-voice operations."""
    
    def __init__(
        self,
        audio_repository: AudioRepository,
        api_config: APIConfig
    ):
        self.audio_repository = audio_repository
        self.api_config = api_config
        self.voice_service: Optional[OpenAIVoiceService] = None
        self.is_connected = False
        self.conversation_id: Optional[str] = None
        
    async def start_conversation(
        self,
        conversation_id: str,
        persona_config: Dict[str, Any],
        on_audio_chunk: Callable[[bytes], None],
        on_transcript: Callable[[str], None],
        on_error: Callable[[str], None],
        on_audio_complete: Optional[Callable[[], None]] = None
    ) -> bool:
        """Start a voice-to-voice conversation."""
        try:
            self.voice_service = OpenAIVoiceService(self.api_config)
            self.conversation_id = conversation_id
            
            # Initialize the service without using async with
            await self.voice_service.__aenter__()
            
            success = await self.voice_service.connect(
                conversation_id=conversation_id,
                persona_config=persona_config,
                on_audio_chunk=on_audio_chunk,
                on_transcript=on_transcript,
                on_error=on_error,
                on_audio_complete=on_audio_complete
            )
            
            if success:
                self.is_connected = True
                logger.info(f"Started voice conversation for {conversation_id}")
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
    
    def get_voice_for_persona(self, persona_accent: str) -> str:
        """Get appropriate voice for persona accent."""
        if not self.voice_service:
            return "alloy"  # Default voice
        
        return self.voice_service.get_voice_for_persona(persona_accent)
    
    def get_instructions_for_persona(self, persona_config: Dict[str, Any]) -> str:
        """Generate instructions for the persona."""
        if not self.voice_service:
            return "You are a helpful assistant."
        
        return self.voice_service.get_instructions_for_persona(persona_config)
    
    async def is_healthy(self) -> bool:
        """Check if the voice service is healthy."""
        return self.is_connected and self.voice_service is not None
