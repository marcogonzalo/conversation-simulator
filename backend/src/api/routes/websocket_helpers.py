from fastapi import WebSocket
import json
import logging
from typing import Dict, List, Any

from src.conversation.domain.entities.message import MessageRole

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        logger.info(f"WebSocket connected for conversation {conversation_id}")

    def disconnect(self, conversation_id: str):
        """Disconnect a WebSocket."""
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
            logger.info(f"WebSocket disconnected and removed for conversation {conversation_id}")

    async def send_message(self, conversation_id: str, message: Dict[str, Any]):
        """Send a JSON message to a specific WebSocket connection."""
        # Convert UUID to string if necessary
        conversation_id_str = str(conversation_id)
        
        logger.info(f"send_message called for {conversation_id_str}, message type: {message.get('type')}")
        logger.info(f"Active connections: {list(self.active_connections.keys())}")
        
        if conversation_id_str in self.active_connections:
            websocket = self.active_connections[conversation_id_str]
            logger.info(f"WebSocket found for {conversation_id_str}, attempting to send message")
            try:
                message_json = json.dumps(message)
                logger.info(f"Sending message to {conversation_id_str}: {message_json[:200]}...")
                await websocket.send_text(message_json)
                logger.info(f"✅ Message sent successfully to {conversation_id_str}")
            except Exception as e:
                logger.error(f"❌ Error sending message to {conversation_id_str}: {e}")
                logger.error(f"❌ WebSocket state: {websocket.client_state if hasattr(websocket, 'client_state') else 'unknown'}")
                # Consider disconnecting on send error
                self.disconnect(conversation_id_str)
        else:
            logger.error(f"❌ No active connection found for {conversation_id_str}")
            logger.error(f"❌ Available connections: {list(self.active_connections.keys())}")

manager = ConnectionManager()

async def send_error(conversation_id: str, error_message: str):
    """Send an error message to the client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "error",
        "error": error_message,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_pong(conversation_id: str):
    """Send pong response to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "pong",
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_transcribed_text(conversation_id: str, text: str, role: str = MessageRole.ASSISTANT.value):
    """Send transcribed text to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "transcribed_text",
        "content": text,
        "role": role,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_processing_status(conversation_id: str, status: str):
    """Send processing status to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "processing_status",
        "status": status,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_text_response(conversation_id: str, text: str):
    """Send AI text response to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "text_response",
        "content": text,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_audio_chunk(conversation_id: str, audio_data: str):
    """Send AI audio chunk for streaming playback."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "audio_chunk",
        "audio_data": audio_data,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_audio_response(conversation_id: str, audio_data: str):
    """Send complete AI audio response to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "audio_response",
        "audio_data": audio_data,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_persona_info(conversation_id: str, name: str, accent: str):
    """Send persona info to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "persona_info",
        "name": name,
        "accent": accent,
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)

async def send_analysis_result(conversation_id: str, analysis_data: dict):
    """Send conversation analysis result to client."""
    conversation_id_str = str(conversation_id)
    message = {
        "type": "analysis_result",
        "analysis": analysis_data.get("analysis", ""),
        "analysis_id": analysis_data.get("analysis_id", ""),
        "conversation_id": conversation_id_str
    }
    await manager.send_message(conversation_id_str, message)



