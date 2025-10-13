"""
Enhanced conversation API routes with intelligent message processing.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from src.conversation.application.services.enhanced_conversation_service import EnhancedConversationService
from src.conversation.infrastructure.repositories.enhanced_conversation_repository import EnhancedConversationRepository
from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository


# Dependency injection
def get_enhanced_conversation_service(
    conversation_repo: SQLConversationRepository = Depends(),
    enhanced_repo: EnhancedConversationRepository = Depends()
) -> EnhancedConversationService:
    return EnhancedConversationService(conversation_repo, enhanced_repo)


router = APIRouter()


# Pydantic models
class TextChunkRequest(BaseModel):
    content: str
    is_final: bool = False
    confidence: Optional[float] = None
    message_group_id: Optional[str] = None


class AudioMessageRequest(BaseModel):
    audio_data: str
    audio_format: str = "webm"
    duration_ms: Optional[int] = None
    transcription: Optional[str] = None
    confidence: Optional[float] = None


class MessageUpdateRequest(BaseModel):
    content: str


@router.get("/conversations/{conversation_id}/enhanced")
async def get_enhanced_conversation(
    conversation_id: str,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Get a conversation with enhanced message processing."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        enhanced_data = await service.get_enhanced_conversation(conversation_id_obj)
        
        if not enhanced_data:
            raise HTTPException(status_code=404, detail="Enhanced conversation not found")
        
        return enhanced_data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enhanced conversation: {str(e)}")


@router.get("/conversations/{conversation_id}/messages/enhanced")
async def get_enhanced_messages(
    conversation_id: str,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> List[Dict[str, Any]]:
    """Get enhanced messages for a conversation."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        messages = await service.get_enhanced_messages(conversation_id_obj)
        
        return [message.to_dict() for message in messages]
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enhanced messages: {str(e)}")


@router.post("/conversations/{conversation_id}/messages/text-chunk")
async def process_text_chunk(
    conversation_id: str,
    request: TextChunkRequest,
    role: str = Query(..., description="Message role: 'user' or 'assistant'"),
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Process a text chunk and add it to the conversation."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        if role not in ['user', 'assistant']:
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")
        
        message = await service.process_text_chunk(
            conversation_id=conversation_id_obj,
            role=role,
            content=request.content,
            is_final=request.is_final,
            confidence=request.confidence,
            message_group_id=request.message_group_id
        )
        
        return {
            "message_id": str(message.id),
            "processed_content": message.get_display_content(),
            "is_final": message.has_final_content(),
            "processing_status": message.processing_status.value
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text chunk: {str(e)}")


@router.post("/conversations/{conversation_id}/messages/audio")
async def process_audio_message(
    conversation_id: str,
    request: AudioMessageRequest,
    role: str = Query(..., description="Message role: 'user' or 'assistant'"),
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Process an audio message and add it to the conversation."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        if role not in ['user', 'assistant']:
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")
        
        message = await service.process_audio_message(
            conversation_id=conversation_id_obj,
            role=role,
            audio_data=request.audio_data,
            audio_format=request.audio_format,
            duration_ms=request.duration_ms,
            transcription=request.transcription,
            confidence=request.confidence
        )
        
        return {
            "message_id": str(message.id),
            "message_type": message.message_type.value,
            "has_transcription": bool(message.get_display_content()),
            "audio_duration_ms": message.audio_metadata.duration_ms if message.audio_metadata else None
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio message: {str(e)}")


@router.put("/conversations/{conversation_id}/messages/{message_id}/content")
async def update_message_content(
    conversation_id: str,
    message_id: str,
    request: MessageUpdateRequest,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Update the content of a specific message."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        message_id_obj = UUID(message_id)
        
        success = await service.update_message_content(
            conversation_id=conversation_id_obj,
            message_id=message_id_obj,
            content=request.content
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {"success": True, "message": "Content updated successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating message content: {str(e)}")


@router.post("/conversations/{conversation_id}/messages/{message_id}/finalize")
async def finalize_message(
    conversation_id: str,
    message_id: str,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Finalize a message and ensure all chunks are processed."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        message_id_obj = UUID(message_id)
        
        success = await service.finalize_message(
            conversation_id=conversation_id_obj,
            message_id=message_id_obj
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {"success": True, "message": "Message finalized successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finalizing message: {str(e)}")


@router.post("/conversations/{conversation_id}/merge-chunks")
async def merge_conversation_chunks(
    conversation_id: str,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Merge message chunks in a conversation for better readability."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        await service.merge_conversation_chunks(conversation_id_obj)
        
        return {"success": True, "message": "Chunks merged successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging chunks: {str(e)}")


@router.get("/conversations/{conversation_id}/statistics")
async def get_conversation_statistics(
    conversation_id: str,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Get conversation statistics."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        statistics = await service.get_conversation_summary(conversation_id_obj)
        
        if not statistics:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return statistics
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@router.get("/conversations/{conversation_id}/export")
async def export_conversation_for_analysis(
    conversation_id: str,
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Export conversation data in a format suitable for analysis."""
    try:
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        conversation_id_obj = ConversationId(UUID(conversation_id))
        
        export_data = await service.export_conversation_for_analysis(conversation_id_obj)
        
        if not export_data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return export_data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting conversation: {str(e)}")


@router.get("/personas/{persona_id}/conversations/enhanced")
async def get_enhanced_conversations_by_persona(
    persona_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> List[Dict[str, Any]]:
    """Get enhanced conversations by persona ID."""
    try:
        conversations = await service.get_enhanced_conversations_by_persona(
            persona_id=persona_id,
            limit=limit,
            offset=offset
        )
        
        return conversations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")


@router.post("/cleanup/expired-messages")
async def cleanup_expired_messages(
    max_age_seconds: int = Query(300, ge=60, le=3600),
    service: EnhancedConversationService = Depends(get_enhanced_conversation_service)
) -> Dict[str, Any]:
    """Clean up expired pending messages."""
    try:
        cleaned_messages = await service.cleanup_expired_messages(max_age_seconds)
        
        return {
            "cleaned_count": len(cleaned_messages),
            "message_ids": [str(msg.id) for msg in cleaned_messages]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up messages: {str(e)}")
