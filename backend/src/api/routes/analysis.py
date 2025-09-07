"""
Analysis API routes with DDD architecture.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from src.analysis.application.services.analysis_application_service import AnalysisApplicationService
from src.analysis.domain.repositories.analysis_repository import AnalysisRepository
from src.analysis.domain.services.analysis_service import AnalysisService
from src.analysis.infrastructure.repositories.sql_analysis_repository import SQLAnalysisRepository

logger = logging.getLogger(__name__)

# Dependency injection
def get_analysis_repository() -> AnalysisRepository:
    """Get analysis repository instance."""
    return SQLAnalysisRepository()

def get_analysis_service() -> AnalysisService:
    """Get analysis service instance."""
    return AnalysisService()

def get_analysis_application_service(
    repository: AnalysisRepository = Depends(get_analysis_repository),
    service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisApplicationService:
    """Get analysis application service instance."""
    return AnalysisApplicationService(repository, service)

# Router
router = APIRouter()

@router.post("/conversation/{conversation_id}")
async def analyze_conversation(
    conversation_id: str,
    conversation_data: dict,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Analyze a conversation."""
    try:
        result = await service.analyze_conversation(
            conversation_id=conversation_id,
            conversation_data=conversation_data
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return {
            "analysis_id": str(result.analysis_id.value),
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}")
async def get_analysis_by_id(
    analysis_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis by ID."""
    try:
        result = await service.get_analysis_by_id(analysis_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return {
            "analysis": result.analysis,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/conversation/{conversation_id}")
async def get_analysis_by_conversation(
    conversation_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis by conversation ID."""
    try:
        result = await service.get_analysis_by_conversation(conversation_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return {
            "analysis": result.analysis,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis by conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def get_analyses(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analyses with optional filters."""
    try:
        result = await service.get_analyses(
            status=status,
            limit=limit,
            offset=offset
        )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "analyses": result.analyses,
            "total_count": result.total_count,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analyses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}/summary")
async def get_analysis_summary(
    analysis_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis summary."""
    try:
        summary = await service.get_analysis_summary(analysis_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}/metrics")
async def get_analysis_metrics(
    analysis_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis metrics."""
    try:
        metrics = await service.get_analysis_metrics(analysis_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Analysis not found or no metrics available")
        
        return metrics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}/recommendations")
async def get_analysis_recommendations(
    analysis_id: str,
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)"),
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis recommendations."""
    try:
        if priority == "high":
            recommendations = await service.get_high_priority_recommendations(analysis_id)
        else:
            # Get all recommendations
            result = await service.get_analysis_by_id(analysis_id)
            if not result.success:
                raise HTTPException(status_code=404, detail="Analysis not found")
            recommendations = result.analysis.recommendations if result.analysis else []
        
        return {
            "recommendations": recommendations,
            "analysis_id": analysis_id,
            "priority_filter": priority
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}/strengths")
async def get_analysis_strengths(
    analysis_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis strengths."""
    try:
        strengths = await service.get_analysis_strengths(analysis_id)
        
        return {
            "strengths": strengths,
            "analysis_id": analysis_id
        }
    
    except Exception as e:
        logger.error(f"Error getting analysis strengths: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}/improvements")
async def get_analysis_improvements(
    analysis_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis areas for improvement."""
    try:
        improvements = await service.get_analysis_improvements(analysis_id)
        
        return {
            "improvements": improvements,
            "analysis_id": analysis_id
        }
    
    except Exception as e:
        logger.error(f"Error getting analysis improvements: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{analysis_id}/performance")
async def get_analysis_performance(
    analysis_id: str,
    service: AnalysisApplicationService = Depends(get_analysis_application_service)
):
    """Get analysis performance level."""
    try:
        performance_level = await service.get_analysis_performance_level(analysis_id)
        
        if not performance_level:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "performance_level": performance_level,
            "analysis_id": analysis_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis performance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")