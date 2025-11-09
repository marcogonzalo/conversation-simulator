"""
Gemini Live API service for real-time voice-to-voice conversations.
"""
import asyncio
import json
import logging
import io
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime

from google import genai
from google.genai import types

from src.shared.infrastructure.external_apis.api_config import APIConfig
from src.shared.application.prompt_service import PromptService
from src.shared.domain.interfaces.voice_service_interface import VoiceServiceInterface
from src.conversation.domain.entities.message import MessageRole

logger = logging.getLogger(__name__)


class GeminiVoiceService(VoiceServiceInterface):
    """Service for Gemini Live API voice-to-voice conversations using gemini-2.5-flash."""
    
    # Gemini Live API works best with 16kHz PCM audio
    GEMINI_SAMPLE_RATE = 16000
    GEMINI_INPUT_FORMAT = "pcm16"  # Gemini expects pcm16 format
    
    def __init__(self, api_config: APIConfig):
        self.api_config = api_config
        self.client: Optional[genai.Client] = None
        self.session: Optional[Any] = None  # Gemini session object
        self._session_cm: Optional[Any] = None  # Session context manager
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
        # Gemini handles turn detection, this timeout controls chunk aggregation size
        self._audio_timeout = 0.3  # 300ms for smooth chunk aggregation
        
        # Store full text accumulator for transcription
        self._assistant_transcript_accumulator = ""
        
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.api_config.gemini_api_key:
            raise ValueError("Gemini API key not configured")
            
        self.client = genai.Client(api_key=self.api_config.gemini_api_key)
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
        """Connect to Gemini Live API voice-to-voice service."""
        if not self.client:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        try:
            # Store callbacks and config
            self._on_audio_chunk = on_audio_chunk
            self._on_transcript = on_transcript
            self._on_error = on_error
            self._on_audio_complete = on_audio_complete
            self.conversation_id = conversation_id
            
            # Configure Gemini Live session
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_id
                        )
                    )
                )
            )
            
            # Connect to Gemini Live API using async context manager
            # The session is managed as an async generator context manager
            self._session_cm = self.client.aio.live.connect(
                model=self.api_config.gemini_voice_model,
                config=config
            )
            self.session = await self._session_cm.__aenter__()
            
            # Send initial system instructions as non-realtime content
            await self.session.send_client_content(
                turns=types.Content(
                    role="user",
                    parts=[types.Part(text=instructions)]
                )
            )
            
            # Start listening for events
            self._listen_task = asyncio.create_task(self._listen_for_events())
            
            self._is_connected = True
            logger.info(f"Connected to Gemini Live API for conversation {conversation_id} with voice {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            await on_error(f"Connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from Gemini Live API."""
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
            
            # Close session connection properly using context manager
            if self._session_cm and self.session:
                try:
                    await self._session_cm.__aexit__(None, None, None)
                    logger.info("Disconnected from Gemini Live API")
                except Exception as e:
                    logger.warning(f"Error closing session: {e}")
        except Exception as e:
            logger.error(f"Error disconnecting from Gemini Live API: {e}")
        finally:
            self._is_connected = False
            self.session = None
            self._session_cm = None
            self._listen_task = None
            # Reset audio accumulation system
            self._audio_buffer.clear()
            self._audio_timer = None
            self._is_processing_audio = False
            self._user_audio_timestamp = None
            self._assistant_transcript_accumulator = ""
    
    async def send_audio(self, audio_data: bytes) -> bool:
        """Send audio data to Gemini using accumulation system."""
        if not self._is_connected or not self.session:
            logger.warning("Not connected to Gemini Live API")
            return False
        
        try:
            # Capture timestamp when user audio arrives at server
            user_audio_timestamp = datetime.utcnow()
            
            # Store timestamp for later use in transcript processing
            self._user_audio_timestamp = user_audio_timestamp
            
            # Convert WebM/Opus audio to PCM16 format expected by Gemini
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
        """Process all accumulated audio chunks as a single request to Gemini."""
        try:
            # Wait for the timeout period
            await asyncio.sleep(self._audio_timeout)
            
            # Check if we're already processing audio
            if self._is_processing_audio:
                logger.warning(f"Audio already being processed (is_processing_audio={self._is_processing_audio}), skipping")
                return
            
            # Check connection before processing
            if not self._is_connected or not self.session:
                logger.warning("Not connected to Gemini Live API during audio processing")
                return
            
            # Double-check buffer is not empty
            if not self._audio_buffer:
                logger.info("No audio chunks to process")
                return
            
            # Create a copy of the buffer and clear the original
            audio_chunks_copy = self._audio_buffer.copy()
            buffer_size = len(audio_chunks_copy)
            total_bytes = sum(len(chunk) for chunk in audio_chunks_copy)
            self._audio_buffer.clear()
            
            self._is_processing_audio = True
            logger.info(f"Starting audio processing: {buffer_size} chunks, {total_bytes} total bytes")
            
            # Concatenate all audio chunks
            combined_audio = b''.join(audio_chunks_copy)
            
            # Validate audio duration using configured minimum
            min_audio_bytes = self.api_config.audio_min_bytes_pcm
            if len(combined_audio) < min_audio_bytes:
                logger.warning(f"Audio too short: {len(combined_audio)} bytes (minimum: {min_audio_bytes} bytes for {self.api_config.audio_min_duration_ms}ms) - skipping")
                return
            
            # Send combined audio to Gemini using realtime input
            await self.session.send_realtime_input(
                audio=types.Blob(
                    data=combined_audio,
                    mime_type=f"audio/pcm;rate={self.GEMINI_SAMPLE_RATE}"
                )
            )
            logger.info(f"✅ Successfully sent audio to Gemini: {len(combined_audio)} bytes")
            
        except asyncio.CancelledError:
            logger.info("Audio processing timer cancelled (more audio arrived, buffer preserved for next timer)")
            return
        except Exception as e:
            logger.error(f"Error processing accumulated audio: {e}", exc_info=True)
        finally:
            self._is_processing_audio = False
            logger.info("Audio processing completed, reset _is_processing_audio flag")
    
    async def _listen_for_events(self):
        """Listen for events from Gemini Live API."""
        try:
            # Reset assistant transcript accumulator at start
            self._assistant_transcript_accumulator = ""
            
            # Listen for server messages
            async for response in self.session.receive():
                try:
                    await self._handle_event(response)
                except Exception as e:
                    logger.error(f"Error handling event: {e}")
        except Exception as e:
            logger.error(f"Error listening for events: {e}")
            if self._on_error:
                await self._on_error(f"Connection error: {str(e)}")
    
    async def _handle_event(self, response: Any):
        """Handle individual events from Gemini."""
        try:
            # Gemini Live API returns different types of responses
            # Check for server content (audio/text response)
            if hasattr(response, 'server_content'):
                server_content = response.server_content
                
                # Handle turn complete (user input processed)
                if hasattr(server_content, 'turn_complete') and server_content.turn_complete:
                    logger.info("User turn complete")
                    
                    # If there's accumulated text, send it as user transcript
                    if hasattr(server_content, 'model_turn') and server_content.model_turn:
                        # Extract user transcript from model turn parts
                        for part in server_content.model_turn.parts:
                            if hasattr(part, 'text') and part.text:
                                # This is the user's transcribed speech
                                if self._on_transcript:
                                    user_speech_timestamp = self._user_audio_timestamp or datetime.utcnow()
                                    await self._on_transcript(part.text, MessageRole.USER.value, user_speech_timestamp)
                
                # Handle model turn (AI response)
                if hasattr(server_content, 'model_turn') and server_content.model_turn:
                    model_turn = server_content.model_turn
                    
                    # Process each part of the model turn
                    for part in model_turn.parts:
                        # Handle text response (transcript)
                        if hasattr(part, 'text') and part.text:
                            # Accumulate text for complete transcript
                            self._assistant_transcript_accumulator += part.text
                            
                        # Handle inline audio data
                        if hasattr(part, 'inline_data') and part.inline_data:
                            inline_data = part.inline_data
                            if hasattr(inline_data, 'data') and inline_data.data:
                                audio_data = inline_data.data
                                if self._on_audio_chunk:
                                    logger.debug(f"Received audio chunk: {len(audio_data)} bytes")
                                    await self._on_audio_chunk(audio_data)
                
                # Handle turn complete for assistant (response finished)
                if hasattr(server_content, 'turn_complete') and server_content.turn_complete:
                    # Send accumulated transcript as complete assistant response
                    if self._assistant_transcript_accumulator and self._on_transcript:
                        ai_response_timestamp = datetime.utcnow()
                        await self._on_transcript(
                            self._assistant_transcript_accumulator, 
                            MessageRole.ASSISTANT.value, 
                            ai_response_timestamp
                        )
                        # Reset accumulator for next response
                        self._assistant_transcript_accumulator = ""
                    
                    # Trigger audio complete callback
                    if self._on_audio_complete:
                        try:
                            await self._on_audio_complete()
                        except Exception as e:
                            logger.error(f"Error in audio complete callback: {e}")
            
            # Handle tool calls or other response types if needed
            # (Future extension point)
                
        except Exception as e:
            logger.error(f"Error handling Gemini event: {e}")
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
                    '-ar', str(self.GEMINI_SAMPLE_RATE),  # Use Gemini sample rate
                    '-ac', '1',      # Mono
                    '-f', 'wav',     # WAV format
                    '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
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
        Map persona accent to Gemini-specific voice ID.
        
        Gemini voice mapping (Gemini 2.0 Flash prebuilt voices):
        - Puck: Friendly, casual voice
        - Charon: Deep, authoritative voice
        - Kore: Warm, professional voice
        - Fenrir: Energetic voice
        - Aoede: Smooth, melodic voice
        
        Args:
            accent: Standard accent key (e.g., "mexicano", "peruano")
            
        Returns:
            Gemini voice ID (e.g., "Puck", "Charon")
        """
        # Gemini-specific voice mapping
        accent_voice_map = {
            "mexicano": "Puck",
            "peruano": "Charon",
            "venezolano": "Kore",
            "caribeño": "Fenrir",
            "caribbean": "Aoede",
            "venezuelan": "Charon",
            "peruvian": "Kore",
            "argentino": "Aoede",
            "colombiano": "Puck",
            "español": "Puck",
            "neutral": "Puck"
        }
        
        voice_id = accent_voice_map.get(accent.lower(), "Puck")
        logger.info(f"Mapping accent '{accent}' to Gemini voice '{voice_id}'")
        return voice_id
    
    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "gemini"
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected to voice service."""
        return self._is_connected

