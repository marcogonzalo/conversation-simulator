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
from ....shared.domain.interfaces.voice_service_interface import VoiceServiceInterface
from src.conversation.domain.entities.message import MessageRole

logger = logging.getLogger(__name__)


class OpenAIVoiceService(VoiceServiceInterface):
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
        self._is_connected = False
        self.conversation_id: Optional[str] = None
        self._event_handlers: Dict[str, Callable] = {}
        self._listen_task: Optional[asyncio.Task] = None
        
        # Audio accumulation system
        self._audio_buffer: List[bytes] = []
        self._user_audio_timestamp: Optional[datetime] = None
        
        # Prompt service for dynamic prompts
        self.prompt_service = PromptService(strict_validation=api_config.prompt_strict_validation)
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
        instructions: str,
        voice_id: str,
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
            
            # Connect to OpenAI WebSocket  
            self.websocket = await websockets.connect(
                url, 
                additional_headers=headers
            )
            
            # Configure the session with provided instructions and voice
            await self._configure_session(instructions, voice_id)
            
            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen_for_events())
            
            self._is_connected = True
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
            self._is_connected = False
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
        if not self._is_connected or not self.websocket:
            logger.warning("Not connected to OpenAI voice service")
            return False
        
        try:
            # Capture timestamp when user audio arrives at server
            user_audio_timestamp = datetime.utcnow()
            
            # Store timestamp for later use in transcript processing
            self._user_audio_timestamp = user_audio_timestamp
            
            # Convert WebM/Opus audio to PCM16 format expected by OpenAI
            logger.info(f"Converting audio: {len(audio_data)} bytes WebM to PCM16")
            pcm_audio = await self._convert_audio_to_pcm16(audio_data)
            if not pcm_audio:
                logger.error(f"Failed to convert audio to PCM16 (input: {len(audio_data)} bytes)")
                return False
            
            logger.info(f"Conversion successful: {len(pcm_audio)} bytes PCM16")
            
            # Add to audio buffer
            self._audio_buffer.append(pcm_audio)
            logger.info(f"Added to buffer. Buffer now has {len(self._audio_buffer)} chunks, total bytes: {sum(len(c) for c in self._audio_buffer)}")
            
            # Cancel existing timer if it exists
            if self._audio_timer and not self._audio_timer.done():
                logger.info(f"Cancelling previous timer (buffer had {len(self._audio_buffer)-1} chunks before this one)")
                self._audio_timer.cancel()
            
            # Start new timer to process accumulated audio
            logger.info(f"Starting {self._audio_timeout}s timer to process buffer")
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
            if not self._is_connected or not self.websocket:
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
            logger.info(f"✅ Successfully appended audio to OpenAI buffer: {len(combined_audio)} bytes ({len(audio_base64)} base64 chars)")
            
            # Wait for OpenAI to process the append
            await asyncio.sleep(0.1)  # 100ms buffer
            
            # Commit the audio buffer
            commit_event = {
                "type": "input_audio_buffer.commit"
            }
            await self.websocket.send(json.dumps(commit_event))
            logger.info("✅ Audio committed")
            
            # Wait briefly for commit to be processed
            await asyncio.sleep(0.05)  # 50ms
            
            # Without Server VAD, we need to manually request response generation
            response_create = {
                "type": "response.create"
            }
            await self.websocket.send(json.dumps(response_create))
            logger.info("✅ Response generation requested (Client VAD mode)")
            
        except asyncio.CancelledError:
            logger.info("Audio processing timer cancelled (more audio arrived, buffer preserved for next timer)")
            # Don't raise, just return - buffer is preserved for next processing
            return
        except Exception as e:
            logger.error(f"Error processing accumulated audio: {e}", exc_info=True)
        finally:
            self._is_processing_audio = False
            logger.info("Audio processing completed, reset _is_processing_audio flag")
    
    async def _configure_session(self, instructions: str, voice: str):
        """Configure the OpenAI session with provided instructions and voice."""
        try:
            # Configure session without Server VAD (incompatible with our Client VAD + complete audio flow)
            # We use Client VAD to detect when user stops speaking, then send complete audio
            # Server VAD expects streaming audio, which causes "buffer too small" errors
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
                    "turn_detection": None,  # Disabled: we use Client VAD + manual commit
                    "tools": [],
                    "tool_choice": "auto",
                    "temperature": self.api_config.openai_voice_temperature
                }
            }
            
            logger.info("🎙️ Using Client VAD + manual commit (Server VAD disabled)")
            
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
                        logger.debug(f"Received audio delta: {len(audio_data)} bytes (aligned: {len(audio_data) % 2 == 0})")
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
    
    def get_voice_for_accent(self, accent: str) -> str:
        """
        Map persona accent to OpenAI-specific voice ID.
        
        OpenAI voice mapping:
        - alloy: Balanced, neutral voice
        - echo: Male voice with good articulation
        - fable: Expressive British-accented voice
        - onyx: Deep male voice
        - nova: Friendly female voice
        - shimmer: Warm female voice
        
        Args:
            accent: Standard accent key (e.g., "mexicano", "peruano")
            
        Returns:
            OpenAI voice ID (e.g., "alloy", "echo")
        """
        # OpenAI-specific voice mapping
        accent_voice_map = {
            "mexicano": "alloy",
            "peruano": "echo",
            "venezolano": "fable",
            "caribeño": "onyx",
            "caribbean": "nova",
            "venezuelan": "echo",
            "peruvian": "shimmer",
            "argentino": "nova",
            "colombiano": "shimmer",
            "español": "alloy",
            "neutral": "alloy"
        }
        
        voice_id = accent_voice_map.get(accent.lower(), "alloy")
        logger.info(f"Mapping accent '{accent}' to OpenAI voice '{voice_id}'")
        return voice_id
    
    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "openai"
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected to voice service."""
        return self._is_connected
    
