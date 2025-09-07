"""
WebSocket API routes with DDD architecture.
"""
import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.conversation.domain.repositories.conversation_repository import ConversationRepository
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.infrastructure.repositories.sql_conversation_repository import SQLConversationRepository
from src.shared.infrastructure.messaging.event_bus import event_bus

logger = logging.getLogger(__name__)

# Dependency injection
def get_conversation_repository() -> ConversationRepository:
    """Get conversation repository instance."""
    return SQLConversationRepository()

def get_conversation_domain_service() -> ConversationDomainService:
    """Get conversation domain service instance."""
    return ConversationDomainService()

def get_conversation_application_service(
    repository: ConversationRepository = Depends(get_conversation_repository),
    domain_service: ConversationDomainService = Depends(get_conversation_domain_service)
) -> ConversationApplicationService:
    """Get conversation application service instance."""
    return ConversationApplicationService(repository, domain_service)

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        logger.info(f"WebSocket connected for conversation {conversation_id}")
    
    def disconnect(self, conversation_id: str):
        """Disconnect a WebSocket connection."""
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
            logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    
    async def send_message(self, conversation_id: str, message: Dict[str, Any]):
        """Send a message to a specific conversation."""
        if conversation_id in self.active_connections:
            try:
                await self.active_connections[conversation_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to conversation {conversation_id}: {e}")
                self.disconnect(conversation_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected conversations."""
        for conversation_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to conversation {conversation_id}: {e}")
                self.disconnect(conversation_id)

# Global connection manager
manager = ConnectionManager()

# Router
router = APIRouter()

@router.websocket("/conversation/{conversation_id}")
async def websocket_conversation(
    websocket: WebSocket,
    conversation_id: str,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """WebSocket endpoint for real-time conversation."""
    await manager.connect(websocket, conversation_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message based on type
            message_type = message_data.get("type")
            
            if message_type == "audio":
                await handle_audio_message(conversation_id, message_data, service)
            elif message_type == "text":
                await handle_text_message(conversation_id, message_data, service)
            elif message_type == "ping":
                await handle_ping(conversation_id)
            else:
                await send_error(conversation_id, f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        manager.disconnect(conversation_id)
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for conversation {conversation_id}: {e}")
        manager.disconnect(conversation_id)

async def handle_audio_message(
    conversation_id: str,
    message_data: Dict[str, Any],
    service: ConversationApplicationService
):
    """Handle audio message from client."""
    try:
        audio_data = message_data.get("audio_data")
        audio_url = message_data.get("audio_url")
        
        if not audio_data and not audio_url:
            await send_error(conversation_id, "No audio data provided")
            return
        
        # For now, we'll simulate processing the audio
        # In a real implementation, this would:
        # 1. Send audio to ElevenLabs STT
        # 2. Get transcribed text
        # 3. Process with AI
        # 4. Generate response
        # 5. Send to ElevenLabs TTS
        # 6. Return audio response
        
        # Simulate processing
        await send_processing_status(conversation_id, "Processing audio...")
        
        # Simulate AI response
        response_text = "Gracias por tu mensaje. ¿Podrías contarme más sobre tus necesidades?"
        
        # Send text response
        await send_text_response(conversation_id, response_text)
        
        # Simulate audio response
        await send_audio_response(conversation_id, "simulated_audio_url")
        
    except Exception as e:
        logger.error(f"Error handling audio message: {e}")
        await send_error(conversation_id, "Error processing audio message")

async def handle_text_message(
    conversation_id: str,
    message_data: Dict[str, Any],
    service: ConversationApplicationService
):
    """Handle text message from client."""
    try:
        content = message_data.get("content")
        role = message_data.get("role", "user")
        
        if not content:
            await send_error(conversation_id, "No content provided")
            return
        
        # Send message to conversation
        result = await service.send_message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        
        if not result.success:
            await send_error(conversation_id, result.message)
            return
        
        # Simulate AI response
        response_text = "Entiendo tu punto. ¿Qué opciones has considerado hasta ahora?"
        
        # Send AI response
        ai_result = await service.send_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text
        )
        
        if ai_result.success:
            await send_text_response(conversation_id, response_text)
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        await send_error(conversation_id, "Error processing text message")

async def handle_ping(conversation_id: str):
    """Handle ping message."""
    await send_pong(conversation_id)

async def send_processing_status(conversation_id: str, status: str):
    """Send processing status to client."""
    message = {
        "type": "processing_status",
        "status": status,
        "conversation_id": conversation_id
    }
    await manager.send_message(conversation_id, message)

async def send_text_response(conversation_id: str, text: str):
    """Send text response to client."""
    message = {
        "type": "text_response",
        "content": text,
        "conversation_id": conversation_id
    }
    await manager.send_message(conversation_id, message)

async def send_audio_response(conversation_id: str, audio_url: str):
    """Send audio response to client."""
    message = {
        "type": "audio_response",
        "audio_url": audio_url,
        "conversation_id": conversation_id
    }
    await manager.send_message(conversation_id, message)

async def send_error(conversation_id: str, error_message: str):
    """Send error message to client."""
    message = {
        "type": "error",
        "error": error_message,
        "conversation_id": conversation_id
    }
    await manager.send_message(conversation_id, message)

async def send_pong(conversation_id: str):
    """Send pong response to client."""
    message = {
        "type": "pong",
        "conversation_id": conversation_id
    }
    await manager.send_message(conversation_id, message)

# Health check endpoint for WebSocket
@router.get("/health")
async def websocket_health():
    """WebSocket health check."""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "service": "websocket"
    }