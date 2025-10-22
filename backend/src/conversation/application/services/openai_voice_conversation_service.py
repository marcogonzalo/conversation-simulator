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
from src.audio.infrastructure.services.audio_converter_service import AudioConverterService
from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.entities.message import MessageRole
from src.conversation.domain.value_objects.message_content import MessageContent
from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.conversation.domain.services.message_processing_service import MessageProcessingService
from src.conversation.infrastructure.repositories.enhanced_conversation_repository import EnhancedConversationRepository
from src.conversation.infrastructure.services.transcription_file_service import TranscriptionFileService
from src.persona.domain.entities.persona import Persona
from src.persona.domain.repositories.persona_repository import PersonaRepository
from src.persona.domain.value_objects.persona_id import PersonaId
from src.shared.infrastructure.messaging.event_bus import event_bus
from src.shared.infrastructure.external_apis.api_config import APIConfig
from src.api.routes.websocket_helpers import send_error, send_transcribed_text, send_processing_status, send_audio_response, send_audio_chunk

logger = logging.getLogger(__name__)


class OpenAIVoiceConversationService:
    """Orchestrates voice-to-voice conversations using OpenAI."""
    
    def __init__(
        self,
        conversation_service: ConversationApplicationService,
        voice_service: OpenAIVoiceApplicationService,
        persona_repository: PersonaRepository,
        enhanced_repository: Optional[EnhancedConversationRepository] = None,
        transcription_service: Optional[TranscriptionFileService] = None,
        api_config: Optional[APIConfig] = None
    ):
        self.conversation_service = conversation_service
        self.voice_service = voice_service
        self.persona_repository = persona_repository
        self.transcription_service = transcription_service or TranscriptionFileService()
        self.api_config = api_config or APIConfig()
        self.event_bus = event_bus
        self.active_conversations: Dict[str, bool] = {}
        # Audio accumulation for complete responses
        self.audio_chunks: Dict[str, list] = {}
        # Audio buffer for silence-based chunking
        self.audio_buffer: Dict[str, bytes] = {}
        # Track if streaming was used for each conversation
        self.streaming_used: Dict[str, bool] = {}
        # Enhanced message processing
        self.enhanced_repository = enhanced_repository
        self.message_processor = MessageProcessingService()
        # Chunk aggregation for original system
        self._pending_chunks: Dict[str, Dict[str, str]] = {}
        self._last_chunk_time: Dict[str, datetime] = {}
        # Store messages for transcription file
        self._conversation_messages: Dict[str, List[Dict[str, Any]]] = {}
        # Audio converter service with configured format
        self.audio_converter = AudioConverterService(default_format=self.api_config.audio_output_format)
        
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
        
    async def _convert_pcm_to_audio(self, pcm_data: bytes, sample_rate: int = 24000) -> bytes:
        """Convert PCM16 audio data to configured output format (WAV or WebM).
        
        Uses AudioConverterService which supports:
        - WAV: Simple, no latency, larger files, can have Chrome decode issues with many chunks
        - WebM: Compressed, smaller files, better for streaming, slight quality loss
        
        Format is configured via AUDIO_OUTPUT_FORMAT env variable (default: webm)
        """
        try:
            # Use the audio converter service with configured format
            converted_data = await self.audio_converter.convert_pcm_to_format(
                pcm_data=pcm_data,
                output_format=None,  # Use default from config
                sample_rate=sample_rate
            )
            
            return converted_data
                    
        except Exception as e:
            logger.error(f"Error converting PCM to audio: {e}")
            return b''
    
    async def _process_audio_buffer(self, conversation_id: str):
        """Process accumulated audio buffer with intelligent splitting.
        
        Combines silence detection with size limits for optimal chunking:
        - Prefers natural pauses (silence-based splitting)
        - Enforces size limits to prevent browser decode errors
        - Ensures chunks are neither too small nor too large
        """
        try:
            if conversation_id not in self.audio_buffer:
                return
            
            buffer_data = self.audio_buffer[conversation_id]
            playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
            
            # Size limits for safe browser playback
            MIN_SIZE = 12000   # 0.5s at 24kHz - minimum for smooth playback
            MAX_SIZE = 72000   # 3s at 24kHz - maximum before forcing send
            
            # Only process if we have enough data
            if len(buffer_data) < MIN_SIZE:
                return
            
            # Force send if buffer gets too large (prevent MEDIA_ERR_DECODE)
            if len(buffer_data) >= MAX_SIZE:
                logger.info(f"[{conversation_id}] - Buffer reached max size ({len(buffer_data)} bytes), sending chunk")
                audio_data = await self._convert_pcm_to_audio(buffer_data, sample_rate=playback_sample_rate)
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    await send_audio_chunk(conversation_id, audio_base64)
                    logger.info(f"[{conversation_id}] - Sent chunk by size limit: {len(audio_data)} bytes {self.api_config.audio_output_format.upper()} (~{len(buffer_data)/48000:.1f}s)")
                    await asyncio.sleep(0.025)  # 25ms delay between chunks
                
                self.audio_buffer[conversation_id] = b''
                self.streaming_used[conversation_id] = True
                return
            
            # Try silence-based splitting for natural pauses
            silence_segments = self._detect_silence_segments(buffer_data, sample_rate=playback_sample_rate)
            
            if silence_segments:
                # Split by silence if we found any
                segments = self._split_audio_by_silence(buffer_data, sample_rate=playback_sample_rate)
                
                if len(segments) > 1:
                    # Send all complete segments except the last (might be incomplete)
                    for segment in segments[:-1]:
                        # Only send if segment is large enough
                        if len(segment) >= MIN_SIZE:
                            audio_data = await self._convert_pcm_to_audio(segment, sample_rate=playback_sample_rate)
                            if audio_data:
                                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                                await send_audio_chunk(conversation_id, audio_base64)
                                logger.info(f"[{conversation_id}] - Sent chunk by silence: {len(audio_data)} bytes {self.api_config.audio_output_format.upper()} (~{len(segment)/48000:.1f}s)")
                                await asyncio.sleep(0.025)  # 25ms delay between chunks
                    
                    # Keep the last segment in buffer (might be incomplete)
                    self.audio_buffer[conversation_id] = segments[-1]
                    self.streaming_used[conversation_id] = True
            
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error processing audio buffer: {e}", exc_info=True)
    
    async def _send_complete_audio_response(self, conversation_id: str):
        """Send complete audio response after accumulating all chunks."""
        try:
            if conversation_id not in self.audio_chunks or not self.audio_chunks[conversation_id]:
                logger.warning(f"[{conversation_id}] - No audio chunks to process")
                return
            
            # Send any remaining audio in buffer (last chunk < 2s)
            if conversation_id in self.audio_buffer and self.audio_buffer[conversation_id]:
                playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
                buffer_data = self.audio_buffer[conversation_id]
                
                logger.info(f"[{conversation_id}] - Sending final buffer: {len(buffer_data)} bytes (~{len(buffer_data)/48000:.1f}s)")
                
                audio_data = await self._convert_pcm_to_audio(buffer_data, sample_rate=playback_sample_rate)
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    await send_audio_chunk(conversation_id, audio_base64)
                    logger.info(f"[{conversation_id}] - Sent final chunk: {len(audio_data)} bytes {self.api_config.audio_output_format.upper()}")
            
            # If no streaming was used (very short response), send complete audio
            if not self.streaming_used.get(conversation_id, False) and self.audio_chunks[conversation_id]:
                complete_pcm = b''.join(self.audio_chunks[conversation_id])
                logger.info(f"[{conversation_id}] - No streaming used, sending complete audio: {len(complete_pcm)} bytes")
                
                playback_sample_rate = self.voice_service.api_config.audio_playback_sample_rate
                audio_data = await self._convert_pcm_to_audio(complete_pcm, sample_rate=playback_sample_rate)
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    await send_audio_chunk(conversation_id, audio_base64)
                    logger.info(f"[{conversation_id}] - Sent complete audio: {len(audio_data)} bytes {self.api_config.audio_output_format.upper()}")
            
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
        # Ensure conversation_id is always a string
        conversation_id = str(conversation.id.value)
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
            
            async def on_transcript(transcript: str, role: str = MessageRole.ASSISTANT.value, event_timestamp: Optional[datetime] = None):
                """Handle transcript from OpenAI with chunk processing."""
                try:
                    if transcript.strip():
                        # Use event timestamp if provided, otherwise use current time
                        message_timestamp = event_timestamp or datetime.utcnow()
                        
                        # Process chunk with enhanced message processing
                        if False:  # Temporarily disabled - enhanced_repository:
                            try:
                                from src.conversation.domain.value_objects.conversation_id import ConversationId
                                conversation_id_obj = ConversationId(conversation_id)
                                
                                # Process text chunk using enhanced system
                                enhanced_message = self.message_processor.process_text_chunk(
                                    conversation_id=conversation_id_obj,
                                    role=role,
                                    content=transcript,
                                    is_final=False,  # Assume chunks are not final initially
                                    confidence=None
                                )
                                
                                # Save to enhanced repository
                                await self.enhanced_repository.add_enhanced_message(conversation_id_obj, enhanced_message)
                                
                                # Send processed content to frontend
                                processed_content = enhanced_message.get_display_content()
                                await send_transcribed_text(conversation_id, processed_content, role)
                                
                            except Exception as e:
                                logger.error(f"[{conversation_id}] Error processing enhanced chunk: {e}")
                                # Fallback to original method
                                await send_transcribed_text(conversation_id, transcript, role)
                                asyncio.create_task(
                                    self.conversation_service.send_message(
                                        conversation_id=str(conversation_id),
                                        role=role,
                                        content=transcript,
                                        audio_url=None,
                                        metadata={"event_timestamp": message_timestamp.isoformat()},
                                        message_timestamp=message_timestamp
                                    )
                                )
                        else:
                            # Original method with chunk aggregation
                            await self._handle_chunk_with_aggregation(
                                conversation_id, transcript, role, message_timestamp
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
            
            logger.info(f"[{conversation_id}] - start_conversation returned: {success}")
            
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
        # Ensure conversation_id is always a string
        conversation_id = str(conversation.id.value)
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
        """End a voice conversation and trigger analysis."""
        logger.info(f"[{conversation_id}] - Ending voice conversation")
        
        # Check if conversation is already being ended to prevent double execution
        if conversation_id not in self.active_conversations:
            logger.warning(f"[{conversation_id}] - Conversation already ended or not active")
            return {"success": True, "message": "Conversation already ended"}
        
        try:
            # Save any pending chunks before ending
            await self._save_pending_chunks(conversation_id)
            
            # Save transcription file
            conversation_result = await self.conversation_service.get_conversation(conversation_id)
            if conversation_result.success and conversation_result.conversation:
                transcription_id = conversation_result.conversation.transcription_id
                if transcription_id:
                    await self._save_transcription_file(conversation_id, transcription_id)
            
            # End voice service conversation
            await self.voice_service.end_conversation()
            
            # Trigger conversation analysis
            analysis_result = await self._trigger_conversation_analysis(conversation_id)
            
            # Clean up stored messages after analysis is complete
            if conversation_id in self._conversation_messages:
                del self._conversation_messages[conversation_id]
            
            # Remove from active conversations (after processing is complete)
            self.active_conversations.pop(conversation_id, None)
            
            logger.info(f"[{conversation_id}] - Voice conversation ended successfully")
            return {
                "success": True,
                "analysis": analysis_result
            }
            
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error ending voice conversation: {e}", exc_info=True)
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    async def _handle_chunk_with_aggregation(
        self, 
        conversation_id: str, 
        transcript: str, 
        role: str, 
        message_timestamp: datetime
    ) -> None:
        """Handle text chunks with aggregation to avoid multiple messages."""
        # Create a key for this conversation and role
        chunk_key = f"{conversation_id}_{role}"
        current_time = datetime.utcnow()
        
        # Check if this is a new message (gap of more than 3 seconds since last chunk)
        is_new_message = False
        if chunk_key in self._last_chunk_time:
            time_diff = (current_time - self._last_chunk_time[chunk_key]).total_seconds()
            if time_diff > 3.0:  # More than 3 seconds gap = new message
                is_new_message = True
        
        # If it's a new message, save the previous one and start fresh
        if is_new_message and chunk_key in self._pending_chunks:
            pending = self._pending_chunks[chunk_key]
            content = pending["content"].strip()
            if content:
                # Store message for transcription file
                self._store_message_for_transcription(conversation_id, role, content, pending["timestamp"])
            # Remove the old pending message
            del self._pending_chunks[chunk_key]
        
        # Initialize or update pending chunk
        if chunk_key not in self._pending_chunks:
            self._pending_chunks[chunk_key] = {
                "content": "",
                "timestamp": message_timestamp,
                "last_update": current_time
            }
        
        # Add chunk to pending content
        pending = self._pending_chunks[chunk_key]
        pending["content"] += transcript
        pending["last_update"] = current_time
        self._last_chunk_time[chunk_key] = current_time
        
        # Send only the new chunk to frontend (not the accumulated content)
        await send_transcribed_text(conversation_id, transcript, role)
        
        # Schedule message save after a delay to allow for more chunks
        asyncio.create_task(self._schedule_message_save(chunk_key, conversation_id, role, pending))
    
    async def _schedule_message_save(
        self, 
        chunk_key: str, 
        conversation_id: str, 
        role: str, 
        pending: Dict[str, Any]
    ) -> None:
        """Schedule message save with a delay to aggregate chunks."""
        # Wait 2 seconds for more chunks to arrive
        await asyncio.sleep(2.0)
        
        # Check if this chunk is still the latest
        if chunk_key in self._pending_chunks and self._pending_chunks[chunk_key] == pending:
            # Save the aggregated message
            content = pending["content"].strip()
            if content:
                # Store message for transcription file
                self._store_message_for_transcription(conversation_id, role, content, pending["timestamp"])
                logger.info(f"Aggregated message processed for conversation {conversation_id}: {role} - {content[:50]}...")
            
            # Remove from pending
            if chunk_key in self._pending_chunks:
                del self._pending_chunks[chunk_key]
    
    async def _save_pending_chunks(self, conversation_id: str) -> None:
        """Save any pending chunks when conversation ends."""
        keys_to_remove = []
        
        for chunk_key, pending in self._pending_chunks.items():
            if chunk_key.startswith(conversation_id):
                content = pending["content"].strip()
                if content:
                    role = chunk_key.split("_")[-1]  # Extract role from key
                    # Store message for transcription file
                    self._store_message_for_transcription(conversation_id, role, content, pending["timestamp"])
                    logger.info(f"Message processed for conversation {conversation_id}: {role} - {content[:50]}...")
                keys_to_remove.append(chunk_key)
        
        # Remove processed chunks
        for key in keys_to_remove:
            del self._pending_chunks[key]

    async def _trigger_conversation_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """Trigger conversation analysis after ending the call."""
        try:
            # Get conversation data
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation.success or not conversation.conversation:
                logger.error(f"[{conversation_id}] - Could not retrieve conversation for analysis")
                return {"error": "Could not retrieve conversation data"}
            
            # Get messages from transcription file
            transcription_id = conversation.conversation.transcription_id
            if not transcription_id:
                logger.error(f"[{conversation_id}] - No transcription ID found for analysis")
                return {"error": "No transcription ID found"}
            
            # Read transcription file
            transcription_data = await self.transcription_service.get_transcription(transcription_id)
            if not transcription_data:
                logger.error(f"[{conversation_id}] - Could not read transcription file {transcription_id}")
                return {"error": "Could not read transcription file"}
            
            # Prepare conversation data for analysis
            conversation_data = {
                "conversation_id": conversation_id,
                "messages": transcription_data.get("messages", []),
                "duration_seconds": transcription_data.get("duration_seconds", 0),
                "persona_name": transcription_data.get("persona_id", "Cliente"),
                "context_id": conversation.conversation.context_id,
                "metadata": transcription_data.get("metadata", {})
            }
            
            # Call analysis service
            from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService
            analysis_service = ConversationAnalysisService()
            analysis = await analysis_service.analyze_conversation(conversation_data)
            
            # Assign analysis to conversation and mark as completed
            if analysis and analysis.get('analysis_id'):
                analysis_id = analysis.get('analysis_id')
                
                # Assign analysis to conversation
                await self.conversation_service.assign_analysis(conversation_id, analysis_id)
                
                # Complete the conversation
                await self.conversation_service.complete_conversation(conversation_id)
                
                logger.info(f"[{conversation_id}] - Analysis assigned and conversation completed")
            
            logger.info(f"[{conversation_id}] - Analysis completed successfully")
            return {
                "analysis": analysis,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"[{conversation_id}] - Error in conversation analysis: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
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
    
    def _store_message_for_transcription(self, conversation_id: str, role: str, content: str, timestamp: datetime) -> None:
        """Store a message for transcription file generation."""
        if conversation_id not in self._conversation_messages:
            self._conversation_messages[conversation_id] = []
        
        message_data = {
            "id": f"{conversation_id}_{len(self._conversation_messages[conversation_id])}",
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat(),
            "metadata": {}
        }
        
        self._conversation_messages[conversation_id].append(message_data)
        logger.debug(f"Stored message for transcription: {conversation_id} - {role}")
    
    async def _save_transcription_file(self, conversation_id: str, transcription_id: str) -> None:
        """Save transcription to file when conversation ends."""
        try:
            if conversation_id not in self._conversation_messages:
                logger.warning(f"No messages found for conversation {conversation_id}")
                return
            
            # Get conversation details
            conversation_result = await self.conversation_service.get_conversation(conversation_id)
            if not conversation_result.success or not conversation_result.conversation:
                logger.error(f"Could not get conversation details for {conversation_id}")
                return
            
            conversation = conversation_result.conversation
            
            # Sort messages by timestamp to ensure correct chronological order
            messages = self._conversation_messages[conversation_id]
            sorted_messages = sorted(messages, key=lambda x: x["timestamp"])
            
            # Regenerate IDs to reflect correct chronological order
            for i, message in enumerate(sorted_messages):
                message["id"] = f"{conversation_id}_{i}"
            
            # Save transcription file
            await self.transcription_service.save_transcription(
                conversation_id=conversation_id,
                transcription_id=transcription_id,
                messages=sorted_messages,
                persona_id=conversation.persona_id,
                context_id=conversation.context_id,
                metadata={"source": "openai_voice_conversation"}
            )
            
            logger.info(f"Transcription file saved for conversation {conversation_id}")
            
            # Note: Don't clean up messages here, they might be needed for analysis
                
        except Exception as e:
            logger.error(f"Failed to save transcription file for {conversation_id}: {e}")
