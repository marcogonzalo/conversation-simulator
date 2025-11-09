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
        
        # Store full text accumulators for transcriptions
        self._assistant_transcript_accumulator = ""
        self._user_transcript_accumulator = ""
        
        # VAD mode configuration (internal defaults)
        from src.shared.infrastructure.config.ai_defaults import GEMINI_VOICE_DEFAULTS
        self._vad_mode = GEMINI_VOICE_DEFAULTS.vad_mode
        # Derive streaming behavior from VAD mode
        self._use_streaming = (self._vad_mode == "auto")
        
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.api_config.gemini_api_key:
            raise ValueError("Gemini API key not configured")
            
        self.client = genai.Client(api_key=self.api_config.gemini_api_key, http_options={"api_version": "v1alpha"})
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
            
            # Configure Gemini Live session with system instructions
            # Use both AUDIO and TEXT modalities for best experience
            use_auto_vad = self._vad_mode == "auto"
            logger.info(f"Configuring Gemini with VAD mode: {self._vad_mode}, streaming: {self._use_streaming}")
            
            # Build config step by step to identify issues
            config_dict = {
                "response_modalities": ["AUDIO"],  # Only audio for now
                "system_instruction": types.Content(
                    parts=[types.Part(text=instructions)]
                ),
                "speech_config": types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_id
                        )
                    )
                ),
                # Enable transcriptions
                "input_audio_transcription": {},
                "output_audio_transcription": {}
            }
            
            # Add VAD configuration only for manual mode
            if not use_auto_vad:
                config_dict["realtime_input_config"] = types.RealtimeInputConfig(
                    automatic_activity_detection=types.AutomaticActivityDetection(
                        disabled=True
                    )
                )
            
            config = types.LiveConnectConfig(**config_dict)
            
            # Connect to Gemini Live API using async context manager
            # The session is managed as an async generator context manager
            self._session_cm = self.client.aio.live.connect(
                model=self.api_config.gemini_voice_model,
                config=config
            )
            self.session = await self._session_cm.__aenter__()
            
            logger.info("Session established, waiting for initial model greeting...")
            
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
        """Send audio data to Gemini (streaming or buffered based on VAD mode)."""
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
            
            # Choose strategy based on VAD mode and streaming configuration
            if self._use_streaming:
                # STREAMING MODE: Send chunks immediately (for auto VAD)
                await self.session.send_realtime_input(
                    audio=types.Blob(
                        data=pcm_audio,
                        mime_type=f"audio/pcm;rate={self.GEMINI_SAMPLE_RATE}"
                    )
                )
                logger.info(f"✅ Sent audio chunk to Gemini: {len(pcm_audio)} bytes (streaming)")
            else:
                # BUFFERING MODE: Accumulate chunks before sending (for manual VAD)
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
            logger.error(f"Error sending audio: {e}")
            return False
    
    async def _process_accumulated_audio(self):
        """Process all accumulated audio chunks (used in buffering mode with manual VAD)."""
        try:
            # Wait for the timeout period
            await asyncio.sleep(self._audio_timeout)
            
            # Check if we're already processing audio
            if self._is_processing_audio:
                logger.warning(f"Audio already being processed, skipping")
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
                logger.warning(f"Audio too short: {len(combined_audio)} bytes (minimum: {min_audio_bytes} bytes) - skipping")
                return
            
            # In manual VAD mode, send activity signals to mark user turn boundaries
            await self.session.send_realtime_input(
                activity_start=types.ActivityStart()
            )
            logger.info("📢 Sent activityStart to Gemini")
            
            await self.session.send_realtime_input(
                audio=types.Blob(
                    data=combined_audio,
                    mime_type=f"audio/pcm;rate={self.GEMINI_SAMPLE_RATE}"
                )
            )
            logger.info(f"🎤 Sent audio to Gemini: {len(combined_audio)} bytes")
            
            await self.session.send_realtime_input(
                activity_end=types.ActivityEnd()
            )
            logger.info("🛑 Sent activityEnd to Gemini - user turn complete")
            
        except asyncio.CancelledError:
            logger.info("Audio processing timer cancelled (more audio arrived)")
            return
        except Exception as e:
            logger.error(f"Error processing accumulated audio: {e}", exc_info=True)
        finally:
            self._is_processing_audio = False
            logger.info("Audio processing completed")
    
    async def _listen_for_events(self):
        """Listen for events from Gemini Live API."""
        try:
            # Reset assistant transcript accumulator at start
            self._assistant_transcript_accumulator = ""
            
            logger.info("🎧 Started listening for Gemini events")
            
            # Keep listening in a loop to handle multiple turns
            # The session.receive() generator ends after each turn with parallel sends
            while self._is_connected and self.session:
                try:
                    logger.info("🔄 Starting/restarting session.receive() loop")
                    # Listen for server messages
                    async for response in self.session.receive():
                        try:
                            logger.info(f"📨 Gemini event received: type={type(response).__name__}")
                            logger.debug(f"📨 Full Gemini event: {response}")
                            await self._handle_event(response)
                        except Exception as e:
                            logger.error(f"Error handling event: {e}", exc_info=True)
                    
                    # If we reach here, the generator ended
                    if self._is_connected:
                        logger.info("🔄 session.receive() ended, restarting listener for next turn")
                        # No delay - restart immediately
                    else:
                        logger.info("🎧 Session disconnected, stopping listener")
                        break
                        
                except Exception as e:
                    if self._is_connected:
                        logger.error(f"Error in receive loop: {e}, retrying...", exc_info=True)
                    else:
                        logger.info("🎧 Session disconnected during error, stopping listener")
                        break
            
            logger.info("🎧 Stopped listening for Gemini events")
        except Exception as e:
            logger.error(f"Error listening for events: {e}", exc_info=True)
            if self._on_error:
                await self._on_error(f"Connection error: {str(e)}")
    
    async def _handle_event(self, response: Any):
        """Handle individual events from Gemini."""
        try:
            # Handle input audio transcription (user speech)
            if hasattr(response, 'server_content') and hasattr(response.server_content, 'input_transcription'):
                input_transcription = response.server_content.input_transcription
                if hasattr(input_transcription, 'text') and input_transcription.text:
                    logger.info(f"🎤 User transcript chunk: {input_transcription.text}")
                    # Accumulate user transcript chunks instead of sending immediately
                    self._user_transcript_accumulator += input_transcription.text
            
            # Handle output audio transcription (assistant speech)
            if hasattr(response, 'server_content') and hasattr(response.server_content, 'output_transcription'):
                output_transcription = response.server_content.output_transcription
                logger.debug(f"🔍 output_transcription object: {output_transcription}")
                if hasattr(output_transcription, 'text'):
                    text_value = output_transcription.text
                    logger.info(f"🤖 Assistant transcript chunk ({len(text_value) if text_value else 0} chars): {text_value}")
                    if text_value:
                        # Just accumulate, don't send yet - we'll send the complete transcript on turn_complete
                        self._assistant_transcript_accumulator += output_transcription.text
                        logger.info(f"📝 Accumulated assistant transcript: {len(self._assistant_transcript_accumulator)} chars total")
                else:
                    logger.warning(f"⚠️ output_transcription has no 'text' attribute: {dir(output_transcription)}")
            
            # Gemini Live API returns different types of responses
            # Check for server content (audio/text response)
            if hasattr(response, 'server_content'):
                server_content = response.server_content
                logger.info(f"📦 Processing server_content: turn_complete={getattr(server_content, 'turn_complete', None)}, has_model_turn={hasattr(server_content, 'model_turn')}, has_input_transcription={hasattr(server_content, 'input_transcription')}, has_output_transcription={hasattr(server_content, 'output_transcription')}")
                
                # Handle turn complete (user input processed)
                if hasattr(server_content, 'turn_complete') and server_content.turn_complete:
                    logger.info("✅ Turn complete")
                    
                    # Send accumulated user transcript when turn is complete
                    if self._user_transcript_accumulator and self._on_transcript:
                        user_speech_timestamp = self._user_audio_timestamp or datetime.utcnow()
                        logger.info(f"📤 Sending user transcript: {self._user_transcript_accumulator}")
                        await self._on_transcript(
                            self._user_transcript_accumulator, 
                            MessageRole.USER.value, 
                            user_speech_timestamp
                        )
                        # Reset user accumulator for next turn
                        self._user_transcript_accumulator = ""
                
                # Handle model turn (AI response)
                if hasattr(server_content, 'model_turn') and server_content.model_turn:
                    model_turn = server_content.model_turn
                    logger.info(f"🤖 Processing model_turn with {len(model_turn.parts)} parts")
                    
                    # Process each part of the model turn
                    for idx, part in enumerate(model_turn.parts):
                        text_value = getattr(part, 'text', None)
                        text_len = len(text_value) if text_value else 0
                        logger.info(f"📄 Part {idx}: has_text={hasattr(part, 'text')}, text_length={text_len}, has_inline_data={hasattr(part, 'inline_data')}")
                        
                        # NOTE: We do NOT use part.text for transcriptions because Gemini sends
                        # its internal "thinking" there (e.g., "**Acknowledge and Engage**...")
                        # Instead, we rely on output_transcription for the actual spoken text
                        if hasattr(part, 'text') and part.text:
                            logger.debug(f"📝 Model turn text (internal thinking, not used): {part.text[:100]}...")
                            
                        # Handle inline audio data
                        if hasattr(part, 'inline_data') and part.inline_data:
                            inline_data = part.inline_data
                            if hasattr(inline_data, 'data') and inline_data.data:
                                audio_data = inline_data.data
                                if self._on_audio_chunk:
                                    logger.info(f"🔊 Received audio chunk: {len(audio_data)} bytes")
                                    await self._on_audio_chunk(audio_data)
                
                # Handle turn complete for assistant (response finished)
                if hasattr(server_content, 'turn_complete') and server_content.turn_complete:
                    logger.info(f"🏁 Turn complete - accumulated transcript length: {len(self._assistant_transcript_accumulator)}")
                    # Send accumulated transcript as complete assistant response
                    if self._assistant_transcript_accumulator and self._on_transcript:
                        ai_response_timestamp = datetime.utcnow()
                        logger.info(f"📤 Sending assistant transcript: {self._assistant_transcript_accumulator[:100]}...")
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
                            logger.info("🎬 Calling audio complete callback")
                            await self._on_audio_complete()
                        except Exception as e:
                            logger.error(f"Error in audio complete callback: {e}")
            else:
                logger.warning(f"⚠️ Event has no server_content attribute. Type: {type(response).__name__}, attributes: {dir(response)}")
            
            # Handle tool calls or other response types if needed
            # (Future extension point)
                
        except Exception as e:
            logger.error(f"Error handling Gemini event: {e}", exc_info=True)
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

