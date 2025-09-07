"""
ElevenLabs service for STT and TTS.
"""
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime

from ...domain.entities.audio_chunk import AudioChunk
from ...domain.value_objects.audio_format import AudioFormatVO, AudioFormat
from ...domain.value_objects.voice_id import VoiceId
from ....shared.infrastructure.external_apis.api_config import APIConfig

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for ElevenLabs STT and TTS operations."""
    
    def __init__(self, api_config: APIConfig):
        self.api_config = api_config
        self.base_url = "https://api.elevenlabs.io/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "xi-api-key": self.api_config.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: VoiceId,
        format: AudioFormatVO = None
    ) -> AsyncGenerator[AudioChunk, None]:
        """Convert text to speech using ElevenLabs TTS."""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        if not self.api_config.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        # Use default format if not provided
        if format is None:
            format = AudioFormatVO(AudioFormat.MP3, 44100, 1, 16)
        
        # Prepare request payload
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": self.api_config.tts_stability,
                "similarity_boost": self.api_config.tts_similarity_boost,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        # Make streaming request
        url = f"{self.base_url}/text-to-speech/{voice_id.value}/stream"
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs TTS error: {response.status} - {error_text}")
                
                sequence_number = 0
                async for chunk_data in response.content.iter_chunked(1024):
                    if chunk_data:
                        # Create audio chunk
                        chunk = AudioChunk(
                            id=AudioChunk.id.generate(),
                            data=chunk_data,
                            format=format,
                            sequence_number=sequence_number,
                            timestamp=datetime.utcnow(),
                            is_final=False
                        )
                        sequence_number += 1
                        yield chunk
                
                # Send final chunk
                final_chunk = AudioChunk(
                    id=AudioChunk.id.generate(),
                    data=b"",
                    format=format,
                    sequence_number=sequence_number,
                    timestamp=datetime.utcnow(),
                    is_final=True
                )
                yield final_chunk
                
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise
    
    async def speech_to_text(
        self, 
        audio_chunks: list[AudioChunk],
        language: str = "es"
    ) -> str:
        """Convert speech to text using ElevenLabs STT."""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        if not self.api_config.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        # Merge audio chunks
        from ...domain.services.audio_domain_service import AudioDomainService
        audio_data = AudioDomainService.merge_audio_chunks(audio_chunks)
        
        if not audio_data:
            raise ValueError("No audio data provided")
        
        # Prepare request
        url = f"{self.base_url}/speech-to-text"
        
        # Create form data
        data = aiohttp.FormData()
        data.add_field('file', audio_data, filename='audio.wav', content_type='audio/wav')
        data.add_field('model_id', 'whisper-1')
        data.add_field('language', language)
        
        try:
            async with self.session.post(url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs STT error: {response.status} - {error_text}")
                
                result = await response.json()
                return result.get('text', '')
                
        except Exception as e:
            logger.error(f"ElevenLabs STT error: {e}")
            raise
    
    async def get_available_voices(self) -> list[Dict[str, Any]]:
        """Get list of available voices."""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        if not self.api_config.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        url = f"{self.base_url}/voices"
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs voices error: {response.status} - {error_text}")
                
                result = await response.json()
                return result.get('voices', [])
                
        except Exception as e:
            logger.error(f"ElevenLabs voices error: {e}")
            raise
    
    async def get_voice_by_id(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get voice details by ID."""
        voices = await self.get_available_voices()
        for voice in voices:
            if voice.get('voice_id') == voice_id:
                return voice
        return None
    
    def get_voice_for_persona(self, persona_accent: str) -> VoiceId:
        """Get appropriate voice ID for persona accent."""
        # Map persona accents to ElevenLabs voice IDs
        accent_voice_map = {
            "mexicano": "pNInz6obpgDQGcFmaJgB",  # Adam (Mexican Spanish)
            "peruano": "EXAVITQu4vr4xnSDxMaL",   # Bella (Peruvian Spanish)
            "venezolano": "VR6AewLTigWG4xSOukaG", # Domi (Venezuelan Spanish)
            "caribeño": "pMsXgVXv3BLzUgSXRplM",  # Elli (Caribbean Spanish)
            "argentino": "AZnzlk1XvdvUeBnXmlld", # Josh (Argentine Spanish)
            "colombiano": "pqHfZKP75CvOlQylNhV4", # Rachel (Colombian Spanish)
            "español": "pNInz6obpgDQGcFmaJgB",   # Default to Adam
        }
        
        voice_id = accent_voice_map.get(persona_accent.lower(), accent_voice_map["español"])
        return VoiceId.from_string(voice_id, accent=persona_accent)
