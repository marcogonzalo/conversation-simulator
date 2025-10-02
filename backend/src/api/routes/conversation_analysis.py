"""
Conversation Analysis API routes.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService

logger = logging.getLogger(__name__)

# Request/Response models
class ConversationAnalysisRequest(BaseModel):
    conversation_id: str
    messages: list
    duration_seconds: int
    persona_name: str
    metadata: Dict[str, Any] = {}

class ConversationAnalysisResponse(BaseModel):
    conversation_id: str
    analysis: str
    success: bool
    message: str

# Dependency injection
def get_analysis_service() -> ConversationAnalysisService:
    """Get conversation analysis service instance."""
    return ConversationAnalysisService()

# Router
router = APIRouter()

@router.post("/analyze", response_model=ConversationAnalysisResponse)
async def analyze_conversation(
    request: ConversationAnalysisRequest,
    analysis_service: ConversationAnalysisService = Depends(get_analysis_service)
):
    """Analyze a conversation and return markdown analysis."""
    try:
        logger.info(f"Starting analysis for conversation {request.conversation_id}")
        
        # Prepare conversation data
        conversation_data = {
            "conversation_id": request.conversation_id,
            "messages": request.messages,
            "duration_seconds": request.duration_seconds,
            "persona_name": request.persona_name,
            "metadata": request.metadata
        }
        
        # Generate analysis
        analysis = await analysis_service.analyze_conversation(conversation_data)
        
        logger.info(f"Analysis completed for conversation {request.conversation_id}")
        
        return ConversationAnalysisResponse(
            conversation_id=request.conversation_id,
            analysis=analysis,
            success=True,
            message="Analysis completed successfully"
        )
    
    except Exception as e:
        logger.error(f"Error analyzing conversation {request.conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "conversation_analysis"}

