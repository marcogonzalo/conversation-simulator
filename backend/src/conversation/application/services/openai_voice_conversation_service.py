"""
OpenAI Voice-to-Voice conversation service for real-time conversations.
"""
import logging
import base64
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from src.audio.application.services.openai_voice_application_service import OpenAIVoiceApplicationService
from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.entities.message import MessageRole
from src.conversation.domain.value_objects.message_content import MessageContent
from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.persona.domain.entities.persona import Persona
from src.persona.domain.repositories.persona_repository import PersonaRepository
from src.persona.domain.value_objects.persona_id import PersonaId
from src.shared.infrastructure.messaging.event_bus import event_bus
from src.api.routes.websocket_helpers import send_error, send_transcribed_text, send_processing_status, send_audio_response

logger = logging.getLogger(__name__)


class OpenAIVoiceConversationService:
    """Orchestrates voice-to-voice conversations using OpenAI."""
    
    def __init__(
        self,
        conversation_service: ConversationApplicationService,
        voice_service: OpenAIVoiceApplicationService,
        persona_repository: PersonaRepository
    ):
        self.conversation_service = conversation_service
        self.voice_service = voice_service
        self.persona_repository = persona_repository
        self.event_bus = event_bus
        self.active_conversations: Dict[str, bool] = {}
        # Audio accumulation for complete responses
        self.audio_chunks: Dict[str, list] = {}
        
    async def _convert_pcm_to_webm(self, pcm_data: bytes, sample_rate: int = 24000) -> bytes:
        """Convert PCM16 audio data to WebM format for frontend compatibility using ffmpeg."""
        import subprocess
        import tempfile
        import os
        
        try:
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(suffix='.pcm', delete=False) as pcm_file:
                pcm_file.write(pcm_data)
                pcm_path = pcm_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                webm_path = webm_file.name
            
            try:
                # Use ffmpeg to convert PCM16 to WebM with Opus codec
                cmd = [
                    'ffmpeg',
                    '-f', 's16le',  # Input format: signed 16-bit little-endian PCM
                    '-ar', str(sample_rate),  # Sample rate
                    '-ac', '1',  # Mono channel
                    '-i', pcm_path,  # Input file
                    '-c:a', 'libopus',  # Audio codec: Opus
                    '-b:a', '32k',  # Higher bitrate for better quality
                    '-application', 'voip',  # Optimize for voice
                    '-f', 'webm',  # Output format
                    '-y',  # Overwrite output file
                    webm_path  # Output file
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    return b''
                
                # Read the converted WebM file
                with open(webm_path, 'rb') as f:
                    webm_data = f.read()
                
                return webm_data
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(pcm_path)
                    os.unlink(webm_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error converting PCM to WebM: {e}")
            return b''
    
    
    async def _send_complete_audio_response(self, conversation_id: str):
        """Send complete audio response after accumulating all chunks."""
        try:
            if conversation_id not in self.audio_chunks or not self.audio_chunks[conversation_id]:
                logger.warning(f"[{conversation_id}] - No audio chunks to process")
                return
            
            # Combine all PCM chunks
            complete_pcm = b''.join(self.audio_chunks[conversation_id])
            
            # Convert PCM16 to WebM for frontend compatibility
            playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
            webm_data = await self._convert_pcm_to_webm(complete_pcm, sample_rate=playback_sample_rate)
            
            # Convert to base64 for WebSocket transmission
            audio_base64 = base64.b64encode(webm_data).decode('utf-8')
            
            # Send the complete audio response
            await send_audio_response(conversation_id, audio_base64)
            logger.info(f"[{conversation_id}] - Audio response sent successfully")
            
            # Clear the accumulated chunks
            self.audio_chunks[conversation_id] = []
            
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error sending complete audio response: {e}", exc_info=True)
    
    async def start_voice_conversation(
        self,
        conversation: Conversation,
        persona_id: str
    ) -> Dict[str, Any]:
        """Start a voice-to-voice conversation."""
        conversation_id = conversation.id.value
        logger.info(f"[{conversation_id}] - Starting voice conversation with persona {persona_id}")
        
        try:
            # Get persona
            persona_id_vo = PersonaId(persona_id)
            persona = await self.persona_repository.get_by_id(persona_id_vo)
            if not persona:
                error_message = f"Persona not found with ID: {persona_id}"
                logger.error(f"[{conversation_id}] - {error_message}")
                return {"success": False, "error": error_message}
            
            # Prepare persona configuration
            persona_config = {
                "name": persona.name,
                "personality": persona.personality_traits.traits,
                "accent": persona.accent.value,
                "background": persona.background,
                "instructions": self.voice_service.get_instructions_for_persona({
                    "name": persona.name,
                    "personality": persona.personality_traits.traits,
                    "accent": persona.accent.value,
                    "background": persona.background
                })
            }
            
            # Define callbacks for voice service
            async def on_audio_chunk(audio_data: bytes):
                """Handle incoming audio chunks from OpenAI."""
                try:
                    # Accumulate audio chunks instead of sending immediately
                    if conversation_id not in self.audio_chunks:
                        self.audio_chunks[conversation_id] = []
                    self.audio_chunks[conversation_id].append(audio_data)
                except Exception as e:
                    logger.error(f"[{conversation_id}] - Error handling audio chunk: {e}", exc_info=True)
            
            async def on_transcript(transcript: str):
                """Handle transcript from OpenAI."""
                try:
                    if transcript.strip():
                        await send_transcribed_text(conversation_id, transcript)
                        
                        # Save AI message to conversation
                        await self.conversation_service.send_message(
                            conversation_id=str(conversation_id),
                            role="assistant",
                            content=transcript,
                            audio_url=None
                        )
                except Exception as e:
                    logger.error(f"[{conversation_id}] - Error handling transcript: {e}")
            
            async def on_error(error_message: str):
                """Handle errors from OpenAI."""
                try:
                    logger.error(f"[{conversation_id}] - OpenAI voice error: {error_message}")
                    await send_error(conversation_id, f"Voice service error: {error_message}")
                except Exception as e:
                    logger.error(f"[{conversation_id}] - Error handling voice error: {e}")
            
            async def on_audio_complete():
                """Handle audio response completion."""
                try:
                    await self._send_complete_audio_response(conversation_id)
                except Exception as e:
                    logger.error(f"[{conversation_id}] - Error in audio complete callback: {e}")
            
            # Start voice conversation
            success = await self.voice_service.start_conversation(
                conversation_id=conversation_id,
                persona_config=persona_config,
                on_audio_chunk=on_audio_chunk,
                on_transcript=on_transcript,
                on_error=on_error,
                on_audio_complete=on_audio_complete
            )
            
            if success:
                self.active_conversations[conversation_id] = True
                logger.info(f"[{conversation_id}] - Voice conversation started successfully")
                return {
                    "success": True,
                    "persona_name": persona.name,
                    "persona_accent": persona.accent.value,
                    "voice": self.voice_service.get_voice_for_persona(persona.accent.value)
                }
            else:
                error_message = "Failed to start voice conversation"
                logger.error(f"[{conversation_id}] - {error_message}")
                return {"success": False, "error": error_message}
                
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error starting voice conversation: {e}", exc_info=True)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    async def send_audio_message(
        self,
        conversation: Conversation,
        audio_data: str,
        audio_format: str = "webm"
    ) -> Dict[str, Any]:
        """Send audio message to the voice conversation."""
        conversation_id = conversation.id.value
        logger.info(f"[{conversation_id}] - Sending audio message")
        
        try:
            # Check if conversation is active
            if not self.active_conversations.get(conversation_id, False):
                error_message = "Voice conversation not active"
                logger.error(f"[{conversation_id}] - {error_message}")
                return {"success": False, "error": error_message}
            
            # Decode base64 audio data
            try:
                audio_bytes = base64.b64decode(audio_data)
            except Exception as e:
                error_message = f"Invalid audio data: {str(e)}"
                logger.error(f"[{conversation_id}] - {error_message}")
                return {"success": False, "error": error_message}
            
            # Send audio to voice service
            success = await self.voice_service.send_audio(audio_bytes)
            
            if success:
                logger.info(f"[{conversation_id}] - Audio message sent successfully")
                return {"success": True}
            else:
                error_message = "Failed to send audio message"
                logger.error(f"[{conversation_id}] - {error_message}")
                return {"success": False, "error": error_message}
                
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error sending audio message: {e}", exc_info=True)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    async def end_voice_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """End a voice conversation."""
        logger.info(f"[{conversation_id}] - Ending voice conversation")
        
        try:
            # End voice service conversation
            await self.voice_service.end_conversation()
            
            # Remove from active conversations
            self.active_conversations.pop(conversation_id, None)
            
            logger.info(f"[{conversation_id}] - Voice conversation ended successfully")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error ending voice conversation: {e}", exc_info=True)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    async def is_conversation_active(self, conversation_id: str) -> bool:
        """Check if a voice conversation is active."""
        return self.active_conversations.get(conversation_id, False)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of voice service."""
        try:
            voice_healthy = await self.voice_service.is_healthy()
            
            return {
                "voice_service": voice_healthy,
                "active_conversations": len(self.active_conversations),
                "overall": voice_healthy
            }
            
        except Exception as e:
            logger.error(f"Voice service health check failed: {e}")
            return {
                "voice_service": False,
                "active_conversations": 0,
                "overall": False
            }
