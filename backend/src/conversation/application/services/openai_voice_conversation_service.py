"""
OpenAI Voice-to-Voice conversation service for real-time conversations.
"""
import logging
import base64
import asyncio
import numpy as np
from typing import Optional, Dict, Any, Callable, List, Tuple
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
from src.api.routes.websocket_helpers import send_error, send_transcribed_text, send_processing_status, send_audio_response, send_audio_chunk

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
        # Audio buffer for silence-based chunking
        self.audio_buffer: Dict[str, bytes] = {}
        # Track if streaming was used for each conversation
        self.streaming_used: Dict[str, bool] = {}
        
    def _detect_silence_segments(self, pcm_data: bytes, sample_rate: int = 24000, 
                                silence_threshold: float = 0.005, min_silence_duration: float = 0.1) -> List[Tuple[int, int]]:
        """Detect silence segments in PCM audio data."""
        try:
            # Convert bytes to numpy array (PCM16)
            audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Calculate RMS energy in small windows
            window_size = int(sample_rate * 0.05)  # 50ms windows for better precision
            hop_size = int(window_size / 2)  # 50% overlap
            
            energy = []
            for i in range(0, len(audio_array) - window_size, hop_size):
                window = audio_array[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                energy.append(rms)
            
            # Find silence segments
            silence_segments = []
            in_silence = False
            silence_start = 0
            
            for i, e in enumerate(energy):
                if e < silence_threshold and not in_silence:
                    # Start of silence
                    in_silence = True
                    silence_start = i * hop_size
                elif e >= silence_threshold and in_silence:
                    # End of silence
                    silence_duration = (i * hop_size - silence_start) / sample_rate
                    if silence_duration >= min_silence_duration:
                        silence_segments.append((silence_start, i * hop_size))
                    in_silence = False
            
            # Handle case where audio ends in silence
            if in_silence:
                silence_duration = (len(audio_array) - silence_start) / sample_rate
                if silence_duration >= min_silence_duration:
                    silence_segments.append((silence_start, len(audio_array)))
            
            return silence_segments
            
        except Exception as e:
            logger.error(f"Error detecting silence segments: {e}")
            return []
    
    def _split_audio_by_silence(self, pcm_data: bytes, sample_rate: int = 24000) -> List[bytes]:
        """Split audio into segments based on silence detection."""
        try:
            silence_segments = self._detect_silence_segments(pcm_data, sample_rate)
            
            if not silence_segments:
                # No silence detected, return as single segment
                return [pcm_data]
            
            # Convert to numpy array for easier slicing
            audio_array = np.frombuffer(pcm_data, dtype=np.int16)
            segments = []
            last_end = 0
            
            for silence_start, silence_end in silence_segments:
                # Add segment before silence
                if silence_start > last_end:
                    segment = audio_array[last_end:silence_start].tobytes()
                    if len(segment) > 0:
                        segments.append(segment)
                last_end = silence_end
            
            # Add remaining audio after last silence
            if last_end < len(audio_array):
                segment = audio_array[last_end:].tobytes()
                if len(segment) > 0:
                    segments.append(segment)
            
            return segments if segments else [pcm_data]
            
        except Exception as e:
            logger.error(f"Error splitting audio by silence: {e}")
            return [pcm_data]
        
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
    
    async def _process_audio_buffer(self, conversation_id: str):
        """Process accumulated audio buffer and send segments based on silence detection."""
        try:
            if conversation_id not in self.audio_buffer:
                return
            
            buffer_data = self.audio_buffer[conversation_id]
            if len(buffer_data) < 2400:  # Less than 0.1 seconds at 24kHz (more aggressive processing)
                return
            
            # Force processing if buffer gets too large (prevent accumulation)
            if len(buffer_data) > 48000:  # More than 2 seconds at 24kHz
                logger.warning(f"🎵 Buffer too large ({len(buffer_data)} bytes), forcing processing")
            
            # Split audio by silence
            playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
            segments = self._split_audio_by_silence(buffer_data, sample_rate=playback_sample_rate)
            
            if len(segments) > 1:
                # Mark that streaming is being used
                self.streaming_used[conversation_id] = True
                
                # Send all segments except the last one (which might be incomplete)
                for segment in segments[:-1]:
                    webm_data = await self._convert_pcm_to_webm(segment, sample_rate=playback_sample_rate)
                    if webm_data:
                        audio_base64 = base64.b64encode(webm_data).decode('utf-8')
                        await send_audio_chunk(conversation_id, audio_base64)
                
                # Keep the last segment in buffer (might be incomplete)
                self.audio_buffer[conversation_id] = segments[-1]
            else:
                # No silence detected, keep accumulating
                pass
                
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error processing audio buffer: {e}", exc_info=True)
    
    async def _send_complete_audio_response(self, conversation_id: str):
        """Send complete audio response after accumulating all chunks."""
        try:
            if conversation_id not in self.audio_chunks or not self.audio_chunks[conversation_id]:
                logger.warning(f"[{conversation_id}] - No audio chunks to process")
                return
            
            # Send any remaining buffer segments first
            if conversation_id in self.audio_buffer and self.audio_buffer[conversation_id]:
                await self._process_audio_buffer(conversation_id)
                # Send the final buffer segment
                if conversation_id in self.audio_buffer and self.audio_buffer[conversation_id]:
                    playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
                    webm_data = await self._convert_pcm_to_webm(self.audio_buffer[conversation_id], sample_rate=playback_sample_rate)
                    if webm_data:
                        audio_base64 = base64.b64encode(webm_data).decode('utf-8')
                        await send_audio_chunk(conversation_id, audio_base64)
            
            # Only send complete audio if streaming was not used
            if not self.streaming_used.get(conversation_id, False):
                
                # Combine all PCM chunks for complete response
                complete_pcm = b''.join(self.audio_chunks[conversation_id])
                
                # Convert PCM16 to WebM for frontend compatibility
                playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
                webm_data = await self._convert_pcm_to_webm(complete_pcm, sample_rate=playback_sample_rate)
                
                # Convert to base64 for WebSocket transmission
                audio_base64 = base64.b64encode(webm_data).decode('utf-8')
                
                # Send the complete audio response
                await send_audio_response(conversation_id, audio_base64)
            
            # Clear the accumulated chunks and buffer
            self.audio_chunks[conversation_id] = []
            self.audio_buffer.pop(conversation_id, None)
            self.streaming_used.pop(conversation_id, None)
            
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
        
        # Reset audio state for new conversation/response
        self.audio_chunks[conversation_id] = []
        self.audio_buffer[conversation_id] = b''
        self.streaming_used[conversation_id] = False
        
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
                "prompt_template": persona.prompt_template,
                "instructions": self.voice_service.get_instructions_for_persona({
                    "name": persona.name,
                    "personality": persona.personality_traits.traits,
                    "accent": persona.accent.value,
                    "background": persona.background,
                    "prompt_template": persona.prompt_template
                })
            }
            
            # Define callbacks for voice service
            async def on_audio_chunk(audio_data: bytes):
                """Handle incoming audio chunks from OpenAI with silence-based chunking."""
                try:
                    
                    # Initialize state if not exists (with reset for new response)
                    if conversation_id not in self.audio_chunks:
                        self.audio_chunks[conversation_id] = []
                        self.audio_buffer[conversation_id] = b''
                        self.streaming_used[conversation_id] = False
                    else:
                        # Reset state for new response if this is the first chunk
                        if len(self.audio_chunks[conversation_id]) == 0:
                            self.audio_buffer[conversation_id] = b''
                            self.streaming_used[conversation_id] = False
                    
                    # Ensure audio_buffer exists (safety check)
                    if conversation_id not in self.audio_buffer:
                        self.audio_buffer[conversation_id] = b''
                    
                    self.audio_chunks[conversation_id].append(audio_data)
                    self.audio_buffer[conversation_id] += audio_data
                    
                    # Process accumulated audio for silence-based chunking
                    await self._process_audio_buffer(conversation_id)
                        
                except Exception as e:
                    logger.error(f"[{conversation_id}] - Error handling audio chunk: {e}", exc_info=True)
            
            async def on_transcript(transcript: str):
                """Handle transcript from OpenAI."""
                try:
                    if transcript.strip():
                        # Send transcript immediately to frontend (non-blocking)
                        await send_transcribed_text(conversation_id, transcript)
                        
                        # Save AI message to conversation (async, non-blocking)
                        # Don't await this to avoid blocking audio processing
                        asyncio.create_task(
                            self.conversation_service.send_message(
                                conversation_id=str(conversation_id),
                                role="assistant",
                                content=transcript,
                                audio_url=None
                            )
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
