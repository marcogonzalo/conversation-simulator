"""
Audio API routes for voice-to-voice integration.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
import io

from src.audio.application.services.openai_voice_application_service import OpenAIVoiceApplicationService
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

def get_voice_service(
    audio_repo: MemoryAudioRepository = Depends(get_audio_repository),
    api_config: APIConfig = Depends(get_api_config)
) -> OpenAIVoiceApplicationService:
    """Get OpenAI voice application service instance."""
    return OpenAIVoiceApplicationService(audio_repo, api_config)

router = APIRouter()

@router.get("/health")
async def audio_health(
    voice_service: OpenAIVoiceApplicationService = Depends(get_voice_service)
):
    """Check audio service health."""
    try:
        is_healthy = await voice_service.is_healthy()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "openai_voice",
            "connected": is_healthy
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices(
    voice_service: OpenAIVoiceApplicationService = Depends(get_voice_service)
):
    """Get available OpenAI voices."""
    try:
        # OpenAI voice options
        voices = [
            {"id": "alloy", "name": "Alloy", "description": "Default voice"},
            {"id": "echo", "name": "Echo", "description": "Alternative voice"},
            {"id": "fable", "name": "Fable", "description": "Alternative voice"},
            {"id": "onyx", "name": "Onyx", "description": "Alternative voice"},
            {"id": "nova", "name": "Nova", "description": "Alternative voice"},
            {"id": "shimmer", "name": "Shimmer", "description": "Alternative voice"}
        ]
        return {"voices": voices}
        
    except Exception as e:
        logger.error(f"Get voices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
