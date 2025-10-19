"""
OpenAI Voice-to-Voice service for real-time conversations.
"""
import asyncio
import json
import logging
import base64
import websockets
import io
import wave
from typing import Optional, Dict, Any, AsyncGenerator, Callable, List
from datetime import datetime
import struct

from openai import AsyncOpenAI
from ....shared.infrastructure.external_apis.api_config import APIConfig
from ....shared.application.prompt_service import PromptService
from src.conversation.domain.entities.message import MessageRole

logger = logging.getLogger(__name__)


class OpenAIVoiceService:
    """Service for OpenAI voice-to-voice conversations using gpt-4o-mini-realtime-preview."""
    
    # OpenAI Voice API constants
    OPENAI_SAMPLE_RATE = 24000  # OpenAI uses 24kHz for voice API
    OPENAI_INPUT_FORMAT = "pcm16"  # OpenAI expects pcm16 format
    OPENAI_OUTPUT_FORMAT = "pcm16"  # OpenAI expects pcm16 format
    
    def __init__(self, api_config: APIConfig):
        self.api_config = api_config
        self.client: Optional[AsyncOpenAI] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.is_connected = False
        self.conversation_id: Optional[str] = None
        self._event_handlers: Dict[str, Callable] = {}
        self._listen_task: Optional[asyncio.Task] = None
        
        # Audio accumulation system
        self._audio_buffer: List[bytes] = []
        self._user_audio_timestamp: Optional[datetime] = None
        
        # Prompt service for dynamic prompts
        self.prompt_service = PromptService()
        self._audio_timer: Optional[asyncio.Task] = None
        self._is_processing_audio = False
        # Server VAD handles turn detection, this timeout controls chunk aggregation size
        # Larger timeout = bigger chunks = smoother playback (doesn't affect response latency)
        self._audio_timeout = 0.3  # 300ms for smooth chunk aggregation
        
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.api_config.openai_api_key:
            raise ValueError("OpenAI API key not configured")
            
        self.client = AsyncOpenAI(api_key=self.api_config.openai_api_key)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.is_connected:
            await self.disconnect()
    
    async def connect(
        self, 
        conversation_id: str,
        persona_config: Dict[str, Any],
        on_audio_chunk: Callable[[bytes], None],
        on_transcript: Callable[[str], None],
        on_error: Callable[[str], None],
        on_audio_complete: Optional[Callable[[], None]] = None
    ) -> bool:
        """Connect to OpenAI voice-to-voice service."""
        if not self.client:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        try:
            # Store callbacks and config
            self._on_audio_chunk = on_audio_chunk
            self._on_transcript = on_transcript
            self._on_error = on_error
            self._on_audio_complete = on_audio_complete
            self.conversation_id = conversation_id
            
            # OpenAI Realtime API WebSocket URL
            url = f"wss://api.openai.com/v1/realtime?model={self.api_config.openai_voice_model}"
            
            # WebSocket headers with authorization
            headers = {
                "Authorization": f"Bearer {self.api_config.openai_api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            # Debug: Log headers and API key info
            # logger.info(f"OpenAI API Key length: {len(self.api_config.openai_api_key) if self.api_config.openai_api_key else 0}")
            # logger.info(f"OpenAI API Key prefix: {self.api_config.openai_api_key[:10] if self.api_config.openai_api_key else 'None'}...")
            # logger.info(f"WebSocket URL: {url}")
            # logger.info(f"Headers: {headers}")
            
            # Connect to OpenAI WebSocket  
            self.websocket = await websockets.connect(
                url, 
                additional_headers=headers
            )
            
            # Configure the session
            await self._configure_session(persona_config)
            
            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen_for_events())
            
            self.is_connected = True
            logger.info(f"Connected to OpenAI voice service for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI voice service: {e}")
            await on_error(f"Connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from OpenAI voice service."""
        try:
            # Cancel listening task
            if self._listen_task and not self._listen_task.done():
                self._listen_task.cancel()
                try:
                    await self._listen_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel audio timer task
            if self._audio_timer and not self._audio_timer.done():
                self._audio_timer.cancel()
                try:
                    await self._audio_timer
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket connection
            if self.websocket:
                try:
                    await self.websocket.close()
                    logger.info("Disconnected from OpenAI voice service")
                except Exception as e:
                    logger.warning(f"Error closing WebSocket: {e}")
        except Exception as e:
            logger.error(f"Error disconnecting from OpenAI voice service: {e}")
        finally:
            self.is_connected = False
            self.session_id = None
            self.websocket = None
            self._listen_task = None
            # Reset audio accumulation system
            self._audio_buffer.clear()
            self._audio_timer = None
            self._is_processing_audio = False
            self._user_audio_timestamp = None
    
    async def send_audio(self, audio_data: bytes) -> bool:
        """Send audio data to OpenAI using accumulation system to prevent overlapping responses."""
        if not self.is_connected or not self.websocket:
            logger.warning("Not connected to OpenAI voice service")
            return False
        
        try:
            # Capture timestamp when user audio arrives at server
            user_audio_timestamp = datetime.utcnow()
            
            # Store timestamp for later use in transcript processing
            self._user_audio_timestamp = user_audio_timestamp
            
            # Convert WebM/Opus audio to PCM16 format expected by OpenAI
            pcm_audio = await self._convert_audio_to_pcm16(audio_data)
            if not pcm_audio:
                logger.error("Failed to convert audio to PCM16")
                return False
            
            # Add to audio buffer
            self._audio_buffer.append(pcm_audio)
            
            # Cancel existing timer if it exists
            if self._audio_timer and not self._audio_timer.done():
                self._audio_timer.cancel()
            
            # Start new timer to process accumulated audio
            self._audio_timer = asyncio.create_task(self._process_accumulated_audio())
            
            return True
            
        except Exception as e:
            logger.error(f"Error accumulating audio: {e}")
            return False
    
    async def _process_accumulated_audio(self):
        """Process all accumulated audio chunks as a single request to OpenAI."""
        try:
            # Wait for the timeout period
            await asyncio.sleep(self._audio_timeout)
            
            # Check if we're already processing audio to prevent multiple simultaneous processing
            if self._is_processing_audio:
                logger.warning(f"Audio already being processed (is_processing_audio={self._is_processing_audio}), skipping")
                return
            
            # Check connection before processing
            if not self.is_connected or not self.websocket:
                logger.warning("Not connected to OpenAI voice service during audio processing")
                return
            
            # Double-check buffer is not empty (race condition protection)
            if not self._audio_buffer:
                logger.info("No audio chunks to process")
                return
            
            # Create a copy of the buffer and clear the original immediately to prevent race conditions
            audio_chunks_copy = self._audio_buffer.copy()
            buffer_size = len(audio_chunks_copy)
            total_bytes = sum(len(chunk) for chunk in audio_chunks_copy)
            self._audio_buffer.clear()
            
            self._is_processing_audio = True
            logger.info(f"Starting audio processing: {buffer_size} chunks, {total_bytes} total bytes")
            
            # Concatenate all audio chunks
            combined_audio = b''.join(audio_chunks_copy)
            
            # Final validation: ensure we have meaningful audio data
            if len(combined_audio) == 0:
                logger.info("No audio data after concatenation, skipping commit")
                return
            
            # Validate audio duration using configured minimum
            min_audio_bytes = self.api_config.audio_min_bytes_pcm
            if len(combined_audio) < min_audio_bytes:
                logger.warning(f"Audio too short: {len(combined_audio)} bytes (minimum: {min_audio_bytes} bytes for {self.api_config.audio_min_duration_ms}ms) - skipping commit")
                return
            
            # Encode combined audio as base64
            audio_base64 = base64.b64encode(combined_audio).decode('utf-8')
            
            # Validate base64 encoding was successful
            if not audio_base64 or len(audio_base64) == 0:
                logger.error("Failed to encode audio as base64")
                return
            
            # Send combined audio to OpenAI
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self.websocket.send(json.dumps(event))
            
            # Commit the audio buffer to trigger processing
            commit_event = {
                "type": "input_audio_buffer.commit"
            }
            await self.websocket.send(json.dumps(commit_event))
            
            logger.info(f"Successfully committed audio buffer: {len(combined_audio)} bytes ({len(audio_base64)} base64 chars)")
            logger.info("✅ Server VAD will automatically detect when user finishes speaking")
            
        except asyncio.CancelledError:
            logger.info("Audio processing timer cancelled (more audio arrived)")
        except Exception as e:
            logger.error(f"Error processing accumulated audio: {e}")
        finally:
            self._is_processing_audio = False
            logger.info("Audio processing completed, reset _is_processing_audio flag")
    
    async def _configure_session(self, persona_config: Dict[str, Any]):
        """Configure the OpenAI session with persona settings."""
        try:
            # Get voice and instructions based on persona
            voice = self.get_voice_for_persona(persona_config.get("accent", "neutral"))
            instructions = self.get_instructions_for_persona(persona_config)
            
            # Configure session with Server VAD for automatic turn detection
            voice_detection_config = self.api_config.get_openai_voice_config().get("voice_detection", {})
            
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": instructions,
                    "voice": voice,
                    "input_audio_format": self.OPENAI_INPUT_FORMAT,
                    "output_audio_format": self.OPENAI_OUTPUT_FORMAT,
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": voice_detection_config.get("threshold", 0.5),
                        "prefix_padding_ms": voice_detection_config.get("prefix_padding_ms", 300),
                        "silence_duration_ms": voice_detection_config.get("silence_duration_ms", 500)
                    },
                    "tools": [],
                    "tool_choice": "auto",
                    "temperature": self.api_config.openai_voice_temperature
                }
            }
            
            logger.info(f"🎙️ Server VAD enabled: threshold={voice_detection_config.get('threshold', 0.5)}, "
                       f"silence_duration={voice_detection_config.get('silence_duration_ms', 500)}ms")
            
            await self.websocket.send(json.dumps(session_update))
            logger.info(f"🔌 Session configured with voice: {voice}")
            
        except Exception as e:
            logger.error(f"Error configuring session: {e}")
            raise

    async def _listen_for_events(self):
        """Listen for events from OpenAI voice service."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_event(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON message: {e}")
                except Exception as e:
                    logger.error(f"Error handling event: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error listening for events: {e}")
            if self._on_error:
                await self._on_error(f"Connection error: {str(e)}")
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle individual events from OpenAI."""
        try:
            event_type = event.get("type")
            
            if event_type == "conversation.item.input_audio_transcription.completed":
                # Handle user speech transcription
                transcript = event.get("transcript", "")
                if transcript and self._on_transcript:
                    # Use the timestamp when user audio arrived, not when transcription is received
                    user_speech_timestamp = self._user_audio_timestamp or datetime.utcnow()
                    
                    await self._on_transcript(transcript, MessageRole.USER.value, user_speech_timestamp)
                
            elif event_type == "response.audio_transcript.delta":
                # Handle AI response transcript chunks
                delta = event.get("delta", "")
                if delta and self._on_transcript:
                    # Capture timestamp when AI response chunk is received by server
                    ai_response_timestamp = datetime.utcnow()
                    
                    await self._on_transcript(delta, MessageRole.ASSISTANT.value, ai_response_timestamp)
                    
            elif event_type == "response.audio.delta":
                # Handle audio response chunks
                delta = event.get("delta")
                if delta and self._on_audio_chunk:
                    try:
                        audio_data = base64.b64decode(delta)
                        await self._on_audio_chunk(audio_data)
                    except Exception as e:
                        logger.error(f"Error decoding audio delta: {e}")
                        
            elif event_type == "response.audio.done":
                # Trigger callback to send complete audio response
                if self._on_audio_complete:
                    try:
                        await self._on_audio_complete()
                    except Exception as e:
                        logger.error(f"Error in audio complete callback: {e}")
                
            elif event_type == "error":
                # Handle errors
                error_info = event.get("error", {})
                error_msg = error_info.get("message", "Unknown error")
                logger.error(f"❌ OpenAI error: {error_info.get('type')} {error_info.get('code')} - {error_msg}")
                if self._on_error:
                    await self._on_error(error_msg)
                
        except Exception as e:
            logger.error(f"Error handling OpenAI event: {e}")
            if self._on_error:
                await self._on_error(f"Event handling error: {str(e)}")
    
    async def _convert_audio_to_pcm16(self, audio_data: bytes) -> Optional[bytes]:
        """Convert WebM/Opus audio to PCM16 format."""
        try:
            import subprocess
            import tempfile
            import os
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                output_path = output_file.name
            
            try:
                # Use ffmpeg to convert WebM to PCM16 WAV
                cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-ar', str(self.OPENAI_SAMPLE_RATE),  # Use OpenAI sample rate
                    '-ac', '1',      # Mono
                    '-f', 'wav',     # WAV format
                    '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian (correct FFmpeg format)
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    return None
                
                # Read the converted PCM data
                with open(output_path, 'rb') as f:
                    wav_data = f.read()
                
                # Extract PCM data (skip WAV header)
                if len(wav_data) > 44:  # WAV header is typically 44 bytes
                    pcm_data = wav_data[44:]  # Skip WAV header
                    return pcm_data
                else:
                    logger.error("Converted file too small")
                    return None
                    
            finally:
                # Clean up temporary files
                try:
                    os.unlink(input_path)
                    os.unlink(output_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return None
    

    def get_voice_for_persona(self, persona_accent: str) -> str:
        """Get appropriate voice for persona accent."""
        # Map persona accents to OpenAI voices
        accent_voice_map = {
            "mexicano": "alloy",      # Default voice
            "peruano": "echo",        # Alternative voice
            "venezolano": "fable",    # Alternative voice
            "caribeño": "onyx",       # Alternative voice
            "argentino": "nova",      # Alternative voice
            "colombiano": "shimmer",  # Alternative voice
            "español": "alloy",       # Default voice
        }
        
        return accent_voice_map.get(persona_accent.lower(), "alloy")
    
    def get_instructions_for_persona(self, persona_config: Dict[str, Any]) -> str:
        """Generate instructions for the persona using the new dynamic prompt system."""
        try:
            # Extract conversation context and persona ID from persona_config
            conversation_context_id = persona_config.get("conversation_context_id", "compra_vivienda")
            persona_id = persona_config.get("persona_id", "carlos_mendoza")
            
            # Use the new dynamic prompt system (which includes security)
            instructions = self.prompt_service.generate_prompt(conversation_context_id, persona_id)
            
            logger.info(f"Generated secure prompt using dynamic system: {conversation_context_id} + {persona_id}")
            return instructions
            
        except Exception as e:
            logger.error(f"Error generating instructions with dynamic system: {e}")
            # Fallback to basic instructions if dynamic system fails
            return self._get_fallback_instructions(persona_config)
    
    def _get_fallback_instructions(self, persona_config: Dict[str, Any]) -> str:
        """Fallback instructions if dynamic system fails."""
        name = persona_config.get("name", "Assistant")
        return f"""Eres {name}, un cliente potencial en una conversación de ventas.
        
REGLAS BÁSICAS:
- Actúa como un cliente real, no como un asistente
- Evalúa la solución desde la perspectiva del comprador
- Mantén la conversación natural y fluida
- Responde en español
- No reveles que eres una IA o simulador"""
    
