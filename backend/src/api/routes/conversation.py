"""
Conversation API routes using ORM directly.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository

logger = logging.getLogger(__name__)

# Dependency injection following Hexagonal Architecture
def get_conversation_repository() -> IConversationRepository:
    """Get conversation repository implementation (ADAPTER)."""
    return SQLConversationRepository()

def get_conversation_domain_service() -> ConversationDomainService:
    """Get conversation domain service instance."""
    return ConversationDomainService()

def get_conversation_application_service(
    repository: IConversationRepository = Depends(get_conversation_repository),
    domain_service: ConversationDomainService = Depends(get_conversation_domain_service)
) -> ConversationApplicationService:
    """Get conversation application service instance.
    
    This is the ASSEMBLY POINT in Hexagonal Architecture - it connects
    the concrete infrastructure adapter with the application service.
    """
    return ConversationApplicationService(repository, domain_service)

# Pydantic models for API
class StartConversationRequest(BaseModel):
    persona_id: str
    context_id: str = "default"
    metadata: Optional[dict] = None

class StartConversationResponse(BaseModel):
    conversation_id: Optional[str] = None
    transcription_id: Optional[str] = None
    success: bool
    message: Optional[str] = None

class AssignAnalysisRequest(BaseModel):
    analysis_id: str

class AssignAnalysisResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    persona_id: str
    context_id: str
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    transcription_id: Optional[str] = None
    analysis_id: Optional[str] = None
    metadata: dict
    duration_seconds: Optional[int] = None

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
            context_id=request.context_id,
            metadata=request.metadata
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return StartConversationResponse(
            conversation_id=result.conversation_id,
            transcription_id=result.transcription_id,
            success=result.success,
            message=result.message
        )
    
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history", response_model=List[ConversationResponse])
async def get_conversation_history(
    limit: int = 50,
    offset: int = 0,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Get all conversations for history view."""
    try:
        conversations = await service.get_conversations(limit=limit, offset=offset)
        
        return [
            ConversationResponse(
                id=conv.id,
                persona_id=conv.persona_id,
                context_id=conv.context_id,
                status=conv.status,
                created_at=conv.created_at.isoformat() if conv.created_at else None,
                completed_at=conv.completed_at.isoformat() if conv.completed_at else None,
                transcription_id=conv.transcription_id,
                analysis_id=conv.analysis_id,
                metadata=conv.metadata,
                duration_seconds=conv.duration_seconds
            )
            for conv in conversations
        ]
    
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
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
            context_id=conversation.context_id,
            status=conversation.status,
            created_at=conversation.created_at.isoformat() if conversation.created_at else None,
            completed_at=conversation.completed_at.isoformat() if conversation.completed_at else None,
            transcription_id=conversation.transcription_id,
            analysis_id=conversation.analysis_id,
            metadata=conversation.metadata,
            duration_seconds=conversation.duration_seconds
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{conversation_id}/analysis", response_model=AssignAnalysisResponse)
async def assign_analysis(
    conversation_id: str,
    request: AssignAnalysisRequest,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Assign an analysis to a conversation."""
    try:
        success = await service.assign_analysis(
            conversation_id=conversation_id,
            analysis_id=request.analysis_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to assign analysis")
        
        return AssignAnalysisResponse(
            success=True,
            message="Analysis assigned successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning analysis: {e}")
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

@router.get("/{conversation_id}/full-detail")
async def get_conversation_full_detail(
    conversation_id: str,
    service: ConversationApplicationService = Depends(get_conversation_application_service)
):
    """Get complete conversation detail including transcription and analysis."""
    try:
        # Import services here to avoid circular dependencies
        from src.conversation.infrastructure.services.transcription_file_service import TranscriptionFileService
        from src.analysis.infrastructure.repositories.file_analysis_repository import FileAnalysisRepository
        
        # Get conversation
        result = await service.get_conversation(conversation_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        conversation = result.conversation
        
        # Get transcription if available
        transcription = None
        if conversation.transcription_id:
            transcription_service = TranscriptionFileService()
            transcription = await transcription_service.get_transcription(conversation.transcription_id)
        
        # Get analysis if available
        analysis = None
        if conversation.analysis_id:
            analysis_repo = FileAnalysisRepository()
            analysis = await analysis_repo.get_analysis(conversation.analysis_id)
        
        return {
            "conversation": {
                "id": conversation.id,
                "persona_id": conversation.persona_id,
                "context_id": conversation.context_id,
                "status": conversation.status,
                "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                "completed_at": conversation.completed_at.isoformat() if conversation.completed_at else None,
                "transcription_id": conversation.transcription_id,
                "analysis_id": conversation.analysis_id,
                "metadata": conversation.metadata,
                "duration_seconds": conversation.duration_seconds
            },
            "transcription": transcription,
            "analysis": analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting full conversation detail: {e}")
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