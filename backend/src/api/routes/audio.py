"""
Audio API routes.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
import io

from src.audio.application.services.audio_application_service import AudioApplicationService
from src.audio.domain.entities.audio_chunk import AudioChunk
from src.audio.domain.value_objects.voice_id import VoiceId
from src.audio.infrastructure.repositories.memory_audio_repository import MemoryAudioRepository
from src.shared.infrastructure.external_apis.api_config import APIConfig

logger = logging.getLogger(__name__)

# Dependency injection
def get_audio_repository() -> MemoryAudioRepository:
    """Get audio repository instance."""
    return MemoryAudioRepository()

def get_api_config() -> APIConfig:
    """Get API configuration instance."""
    return APIConfig()

def get_audio_service(
    audio_repo: MemoryAudioRepository = Depends(get_audio_repository),
    api_config: APIConfig = Depends(get_api_config)
) -> AudioApplicationService:
    """Get audio application service instance."""
    return AudioApplicationService(audio_repo, api_config)

router = APIRouter()

@router.post("/tts")
async def text_to_speech(
    text: str,
    voice_id: str,
    conversation_id: Optional[str] = None,
    audio_service: AudioApplicationService = Depends(get_audio_service)
):
    """Convert text to speech."""
    try:
        voice = VoiceId.from_string(voice_id)
        
        # Create async generator for streaming response
        async def generate_audio():
            async for chunk in audio_service.text_to_speech(text, voice, conversation_id):
                yield chunk.data
        
        return StreamingResponse(
            generate_audio(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "X-Conversation-ID": conversation_id or ""
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = "es",
    audio_service: AudioApplicationService = Depends(get_audio_service)
):
    """Convert speech to text."""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Create audio chunk
        from src.audio.domain.value_objects.audio_format import AudioFormatVO, AudioFormat
        from datetime import datetime
        
        chunk = AudioChunk(
            id=AudioChunk.id.generate(),
            data=audio_data,
            format=AudioFormatVO(AudioFormat.WAV, 44100, 1, 16),
            sequence_number=0,
            timestamp=datetime.utcnow(),
            is_final=True
        )
        
        # Convert to text
        text = await audio_service.speech_to_text([chunk], language)
        
        return {
            "text": text,
            "language": language,
            "duration_ms": audio_service.calculate_audio_duration([chunk])
        }
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices(
    audio_service: AudioApplicationService = Depends(get_audio_service)
):
    """Get available voices."""
    try:
        voices = await audio_service.get_available_voices()
        return {"voices": voices}
        
    except Exception as e:
        logger.error(f"Get voices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices/persona/{accent}")
async def get_voice_for_persona(
    accent: str,
    audio_service: AudioApplicationService = Depends(get_audio_service)
):
    """Get appropriate voice for persona accent."""
    try:
        voice = audio_service.get_voice_for_persona(accent)
        return {
            "voice_id": str(voice),
            "accent": accent,
            "name": voice.name,
            "language": voice.language
        }
        
    except Exception as e:
        logger.error(f"Get voice for persona error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_audio(
    older_than_hours: int = 24,
    audio_service: AudioApplicationService = Depends(get_audio_service)
):
    """Clean up old audio chunks."""
    try:
        deleted_count = await audio_service.cleanup_old_audio(older_than_hours)
        return {
            "deleted_chunks": deleted_count,
            "older_than_hours": older_than_hours
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
