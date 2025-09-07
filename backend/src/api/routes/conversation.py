"""
Conversation API routes with DDD architecture.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

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

# Pydantic models for API
class StartConversationRequest(BaseModel):
    persona_id: str
    metadata: Optional[dict] = None

class StartConversationResponse(BaseModel):
    conversation_id: str
    success: bool
    message: Optional[str] = None

class SendMessageRequest(BaseModel):
    role: str
    content: str
    audio_url: Optional[str] = None
    metadata: Optional[dict] = None

class SendMessageResponse(BaseModel):
    message_id: str
    success: bool
    message: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    persona_id: str
    status: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    messages: List[dict]
    metadata: dict

class CompleteConversationResponse(BaseModel):
    success: bool
    message: Optional[str] = None

# Router
router = APIRouter()

@router.post("/", response_model=StartConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Start a new conversation."""
    try:
        result = await service.start_conversation(
            persona_id=request.persona_id,
            metadata=request.metadata
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return StartConversationResponse(
            conversation_id=str(result.conversation_id.value),
            success=result.success,
            message=result.message
        )
    
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Get a conversation by ID."""
    try:
        result = await service.get_conversation(conversation_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        conversation = result.conversation
        return ConversationResponse(
            id=conversation.id,
            persona_id=conversation.persona_id,
            status=conversation.status,
            started_at=conversation.started_at.isoformat() if conversation.started_at else None,
            ended_at=conversation.ended_at.isoformat() if conversation.ended_at else None,
            duration_seconds=conversation.duration_seconds,
            messages=[
                {
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "role": msg.role,
                    "content": msg.content,
                    "audio_url": msg.audio_url,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in conversation.messages
            ],
            metadata=conversation.metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Send a message in a conversation."""
    try:
        result = await service.send_message(
            conversation_id=conversation_id,
            role=request.role,
            content=request.content,
            audio_url=request.audio_url,
            metadata=request.metadata
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return SendMessageResponse(
            message_id=str(result.message_id),
            success=result.success,
            message=result.message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{conversation_id}/complete", response_model=CompleteConversationResponse)
async def complete_conversation(
    conversation_id: str,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Complete a conversation."""
    try:
        success = await service.complete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to complete conversation")
        
        return CompleteConversationResponse(
            success=True,
            message="Conversation completed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{conversation_id}/metrics")
async def get_conversation_metrics(
    conversation_id: str,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Get conversation metrics."""
    try:
        metrics = await service.get_conversation_metrics(conversation_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Conversation not found or no metrics available")
        
        return metrics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/persona/{persona_id}")
async def get_conversations_by_persona(
    persona_id: str,
    limit: int = 100,
    offset: int = 0,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Get conversations by persona ID."""
    try:
        conversations = await service.get_conversations_by_persona(
            persona_id=persona_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "conversations": conversations,
            "total_count": len(conversations),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"Error getting conversations by persona: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")