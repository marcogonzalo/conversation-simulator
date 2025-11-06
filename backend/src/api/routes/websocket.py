"""
WebSocket API routes with DDD architecture.
"""
import logging
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository
from src.conversation.infrastructure.repositories.enhanced_conversation_repository import EnhancedConversationRepository
from src.conversation.infrastructure.services.transcription_file_service import TranscriptionFileService
from src.audio.application.services.openai_voice_application_service import OpenAIVoiceApplicationService
from src.audio.infrastructure.repositories.memory_audio_repository import MemoryAudioRepository
# Legacy persona imports removed - now using 5-layer system with client_identity
from src.shared.infrastructure.external_apis.api_config import APIConfig
from src.shared.infrastructure.messaging.event_bus import event_bus
from src.api.routes.websocket_helpers import manager, send_error, send_pong, send_transcribed_text, send_processing_status, send_text_response, send_audio_response, send_persona_info, send_analysis_result

logger = logging.getLogger(__name__)

# Dependency injection
def get_conversation_repository() -> IConversationRepository:
    """Get conversation repository instance."""
    return SQLConversationRepository()

def get_conversation_domain_service() -> ConversationDomainService:
    """Get conversation domain service instance."""
    return ConversationDomainService()

def get_conversation_application_service(
    repository: IConversationRepository = Depends(get_conversation_repository),
    domain_service: ConversationDomainService = Depends(get_conversation_domain_service)
) -> ConversationApplicationService:
    """Get conversation application service instance."""
    return ConversationApplicationService(repository, domain_service)

def get_audio_repository():
    """Get audio repository instance."""
    return MemoryAudioRepository()

def get_voice_application_service(
    audio_repo = Depends(get_audio_repository),
    api_config: APIConfig = Depends(lambda: APIConfig())
) -> OpenAIVoiceApplicationService:
    """Get OpenAI voice application service instance."""
    return OpenAIVoiceApplicationService(audio_repo, api_config)

def get_enhanced_conversation_repository() -> EnhancedConversationRepository:
    """Get enhanced conversation repository instance."""
    return None  # Temporarily disabled

def get_voice_conversation_service(
    conversation_service: ConversationApplicationService = Depends(get_conversation_application_service),
    voice_service: OpenAIVoiceApplicationService = Depends(get_voice_application_service),
    enhanced_repo: EnhancedConversationRepository = Depends(get_enhanced_conversation_repository),
    transcription_service: TranscriptionFileService = Depends(lambda: TranscriptionFileService())
) -> OpenAIVoiceConversationService:
    """Get OpenAI voice conversation service instance."""
    api_config = APIConfig()
    return OpenAIVoiceConversationService(
        conversation_service=conversation_service,
        voice_service=voice_service,
        enhanced_repository=enhanced_repo,
        transcription_service=transcription_service,
        api_config=api_config
    )

# WebSocket connection manager
# The ConnectionManager class and its methods are now imported from websocket_helpers.py

# Global connection manager
# manager = ConnectionManager() # This line is removed as manager is now imported directly

# Router
router = APIRouter()

async def handle_messages(websocket: WebSocket, conversation_id: str, conversation_service: ConversationApplicationService, voice_service: OpenAIVoiceConversationService, conversation_repository: IConversationRepository):
    """Receive and handle messages from the client."""
    logger.info(f"Starting message handler for conversation {conversation_id}")
    message_count = 0
    
    while True:
        try:
            # Check if WebSocket is still connected before trying to receive
            if websocket.client_state.name != "CONNECTED":
                logger.info(f"WebSocket not connected for conversation {conversation_id}, stopping message handler")
                break
                
            message_count += 1
            logger.info(f"[{message_count}] Waiting for message from conversation {conversation_id}")
            
            message_text = await websocket.receive_text()
            logger.info(f"[{message_count}] Raw message received: {len(message_text)} characters")
            logger.info(f"[{message_count}] Message preview: {message_text[:200]}...")
            
            try:
                message_data = json.loads(message_text)
                message_type = message_data.get("type")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await send_error(conversation_id, f"Invalid JSON format: {str(e)}")
                continue
            
            logger.info(f"[{message_count}] Received WebSocket message: {message_type} for conversation {conversation_id}")
            logger.info(f"[{message_count}] Message data keys: {list(message_data.keys())}")
            
            if message_type == "start_voice_conversation":
                logger.info(f"[{message_count}] Handling start_voice_conversation")
                await handle_start_voice_conversation(conversation_id, message_data, conversation_service, voice_service, conversation_repository)
                logger.info(f"[{message_count}] Completed start_voice_conversation")
            elif message_type == "audio_message":
                logger.info(f"[{message_count}] Handling audio_message for conversation {conversation_id}")
                await handle_audio_message(conversation_id, message_data, conversation_service, voice_service, conversation_repository)
                logger.info(f"[{message_count}] Completed audio_message")
            elif message_type == "end_voice_conversation":
                logger.info(f"[{message_count}] Handling end_voice_conversation")
                await handle_end_voice_conversation(conversation_id, message_data, voice_service)
                logger.info(f"[{message_count}] Completed end_voice_conversation")
            elif message_type == "pong":
                logger.info(f"[{message_count}] Handling pong")
            else:
                logger.warning(f"[{message_count}] Unknown message type: {message_type}")
                await send_error(conversation_id, f"Unknown message type: {message_type}")
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for conversation {conversation_id}")
            break
        except RuntimeError as e:
            if "WebSocket is not connected" in str(e):
                logger.info(f"WebSocket connection lost for conversation {conversation_id}: {e}")
                break
            else:
                logger.error(f"Runtime error handling message for conversation {conversation_id}: {e}", exc_info=True)
                break
        except Exception as e:
            logger.error(f"Error handling message for conversation {conversation_id}: {e}", exc_info=True)
            # Don't try to send error if connection is broken
            try:
                if websocket.client_state.name == "CONNECTED":
                    await send_error(conversation_id, f"Message processing error: {str(e)}")
            except:
                logger.info(f"Cannot send error message, connection appears to be broken for conversation {conversation_id}")
                break

async def send_pings(websocket: WebSocket, conversation_id: str):
    """Send pings to the client to keep the connection alive."""
    while True:
        await asyncio.sleep(15)  # Send a ping every 15 seconds
        try:
            # Check if WebSocket is still connected before sending ping
            if websocket.client_state.name != "CONNECTED":
                logger.info(f"WebSocket not connected, stopping pings for {conversation_id}")
                break
                
            await websocket.send_text(json.dumps({"type": "ping", "conversation_id": conversation_id}))
            logger.info(f"Ping sent for conversation {conversation_id}")
        except WebSocketDisconnect:
            logger.info(f"Client disconnected, stopping pings for {conversation_id}")
            break
        except RuntimeError as e:
            if "WebSocket is not connected" in str(e):
                logger.info(f"WebSocket connection lost, stopping pings for {conversation_id}: {e}")
                break
            else:
                logger.error(f"Runtime error sending ping for {conversation_id}: {e}")
                break
        except Exception as e:
            logger.error(f"Error sending ping for {conversation_id}: {e}")
            break

@router.websocket("/conversation/{conversation_id}")
async def websocket_conversation(
    websocket: WebSocket,
    conversation_id: str,
    conversation_service: ConversationApplicationService = Depends(get_conversation_application_service),
    voice_service: OpenAIVoiceConversationService = Depends(get_voice_conversation_service),
    conversation_repository: IConversationRepository = Depends(get_conversation_repository)
):
    """WebSocket endpoint for real-time voice conversation."""
    await manager.connect(websocket, conversation_id)
    
    message_handler_task = asyncio.create_task(
        handle_messages(websocket, conversation_id, conversation_service, voice_service, conversation_repository)
    )
    ping_sender_task = asyncio.create_task(
        send_pings(websocket, conversation_id)
    )
    
    try:
        done, pending = await asyncio.wait(
            [message_handler_task, ping_sender_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        
        for task in pending:
            task.cancel()
        for task in done:
            task.result()

    except Exception as e:
        logger.error(f"WebSocket error for conversation {conversation_id}: {e}")
    finally:
        # End voice conversation if active
        await voice_service.end_voice_conversation(conversation_id)
        manager.disconnect(conversation_id)
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")


async def handle_start_voice_conversation(
    conversation_id: str,
    message_data: Dict[str, Any],
    conversation_service: ConversationApplicationService,
    voice_service: OpenAIVoiceConversationService,
    conversation_repository: IConversationRepository
):
    """Handle start voice conversation request."""
    logger.info(f"Starting voice conversation for {conversation_id}")
    try:
        # Get the conversation domain entity
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        from uuid import UUID
        
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
        except (ValueError, TypeError):
            await send_error(conversation_id, "Invalid conversation ID")
            return
        
        conversation = await conversation_repository.get_by_id(conversation_id_obj)
        if not conversation:
            await send_error(conversation_id, "Conversation not found")
            return
        
        persona_id = message_data.get("persona_id")
        if not persona_id:
            await send_error(conversation_id, "Persona ID required")
            return
        
        # Get 5-layer configuration (with defaults)
        industry_id = message_data.get("industry_id", "real_estate")
        situation_id = message_data.get("situation_id", "discovery_no_urgency_price")
        psychology_id = message_data.get("psychology_id", "conservative_analytical")
        
        logger.info(f"Starting voice conversation with 5-layer config: {industry_id}/{situation_id}/{psychology_id}/{persona_id}")
        
        # Start voice conversation with 5-layer configuration
        result = await voice_service.start_voice_conversation(
            conversation=conversation,
            persona_id=persona_id,
            industry_id=industry_id,
            situation_id=situation_id,
            psychology_id=psychology_id
        )
        
        if result["success"]:
            await send_persona_info(conversation_id, result["persona_name"], result["persona_accent"])
            logger.info(f"Voice conversation started for {conversation_id}")
        else:
            await send_error(conversation_id, result["error"])

    except Exception as e:
        logger.error(f"Error starting voice conversation: {e}", exc_info=True)
        await send_error(conversation_id, "Error starting voice conversation")

async def handle_audio_message(
    conversation_id: str,
    message_data: Dict[str, Any],
    conversation_service: ConversationApplicationService,
    voice_service: OpenAIVoiceConversationService,
    conversation_repository: IConversationRepository
):
    """Handle audio message from client."""
    logger.info(f"Received audio message for conversation {conversation_id}")
    logger.info(f"Audio message data keys: {list(message_data.keys())}")
    try:
        # Get the conversation domain entity
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        from uuid import UUID
        
        try:
            conversation_id_obj = ConversationId(UUID(conversation_id))
        except (ValueError, TypeError):
            await send_error(conversation_id, "Invalid conversation ID")
            return
        
        conversation = await conversation_repository.get_by_id(conversation_id_obj)
        if not conversation:
            await send_error(conversation_id, "Conversation not found")
            return
        
        audio_data = message_data.get("audio_data")
        audio_format = message_data.get("audio_format", "webm")
        
        if not audio_data:
            await send_error(conversation_id, "No audio data provided")
            return
        
        # Send audio to voice service
        result = await voice_service.send_audio_message(
            conversation=conversation,
            audio_data=audio_data,
            audio_format=audio_format
        )
        
        if not result["success"]:
            await send_error(conversation_id, result["error"])

    except Exception as e:
        logger.error(f"Error handling audio message: {e}", exc_info=True)
        await send_error(conversation_id, "Error processing audio message")

async def handle_end_voice_conversation(
    conversation_id: str,
    message_data: Dict[str, Any],
    voice_service: OpenAIVoiceConversationService
):
    """Handle end voice conversation request."""
    logger.info(f"Ending voice conversation for {conversation_id}")
    try:
        result = await voice_service.end_voice_conversation(conversation_id)
        
        if not result["success"]:
            await send_error(conversation_id, result["error"])
        else:
            logger.info(f"Voice conversation ended for {conversation_id}")
            
            # Send analysis if available
            if "analysis" in result and result["analysis"]:
                analysis_data = result["analysis"]
                if "analysis" in analysis_data:
                    await send_analysis_result(conversation_id, analysis_data)
                else:
                    logger.warning(f"No analysis content found for conversation {conversation_id}")

    except Exception as e:
        logger.error(f"Error ending voice conversation: {e}", exc_info=True)
        await send_error(conversation_id, "Error ending voice conversation")

# Health check endpoint for WebSocket
@router.get("/health")
async def websocket_health():
    """WebSocket health check."""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "service": "websocket"
    }