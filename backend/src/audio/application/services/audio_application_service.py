"""
Audio application service for coordinating audio operations.
"""
import logging
from typing import List, AsyncGenerator, Optional
from datetime import datetime

from ...domain.entities.audio_chunk import AudioChunk
from ...domain.repositories.audio_repository import AudioRepository
from ...domain.services.audio_domain_service import AudioDomainService
from ...domain.value_objects.voice_id import VoiceId
from ...infrastructure.services.elevenlabs_service import ElevenLabsService
from ....shared.infrastructure.external_apis.api_config import APIConfig

logger = logging.getLogger(__name__)


class AudioApplicationService:
    """Application service for audio operations."""
    
    def __init__(
        self,
        audio_repository: AudioRepository,
        api_config: APIConfig
    ):
        self.audio_repository = audio_repository
        self.api_config = api_config
        self.elevenlabs_service = ElevenLabsService(api_config)
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: VoiceId,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[AudioChunk, None]:
        """Convert text to speech and stream audio chunks."""
        try:
            async with self.elevenlabs_service as service:
                async for chunk in service.text_to_speech(text, voice_id):
                    # Save chunk to repository
                    await self.audio_repository.save_chunk(chunk)
                    
                    # Add conversation context if provided
                    if conversation_id:
                        chunk.conversation_id = conversation_id
                    
                    yield chunk
                    
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
    
    async def speech_to_text(
        self, 
        audio_chunks: List[AudioChunk],
        language: str = "es"
    ) -> str:
        """Convert speech to text."""
        try:
            # Validate audio quality
            if not AudioDomainService.validate_audio_quality(audio_chunks):
                raise ValueError("Audio quality validation failed")
            
            async with self.elevenlabs_service as service:
                text = await service.speech_to_text(audio_chunks, language)
                return text
                
        except Exception as e:
            logger.error(f"STT error: {e}")
            raise
    
    async def get_available_voices(self) -> List[dict]:
        """Get list of available voices."""
        try:
            async with self.elevenlabs_service as service:
                voices = await service.get_available_voices()
                return voices
                
        except Exception as e:
            logger.error(f"Get voices error: {e}")
            raise
    
    async def get_voice_for_persona(self, persona_accent: str) -> VoiceId:
        """Get appropriate voice for persona accent."""
        return self.elevenlabs_service.get_voice_for_persona(persona_accent)
    
    async def cleanup_old_audio(self, older_than_hours: int = 24) -> int:
        """Clean up old audio chunks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        return await self.audio_repository.cleanup_old_chunks(cutoff_time)
    
    async def get_audio_chunks_by_sequence(
        self, 
        start_sequence: int, 
        end_sequence: int
    ) -> List[AudioChunk]:
        """Get audio chunks by sequence range."""
        return await self.audio_repository.get_chunks_by_sequence(start_sequence, end_sequence)
    
    async def merge_audio_chunks(self, chunks: List[AudioChunk]) -> bytes:
        """Merge audio chunks into single audio stream."""
        return AudioDomainService.merge_audio_chunks(chunks)
    
    async def calculate_audio_duration(self, chunks: List[AudioChunk]) -> int:
        """Calculate total duration of audio chunks in milliseconds."""
        return AudioDomainService.calculate_audio_duration(chunks)
