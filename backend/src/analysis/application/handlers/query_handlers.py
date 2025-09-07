"""
Query handlers for analysis bounded context.
"""
from typing import List
from uuid import UUID

from src.analysis.application.queries.get_analysis import (
    GetAnalysisQuery, GetAnalysisResult, AnalysisDto,
    GetAnalysisByConversationQuery, GetAnalysisByConversationResult,
    GetAnalysesQuery, GetAnalysesResult
)
from src.analysis.domain.entities.analysis import AnalysisStatus
from src.analysis.domain.repositories.analysis_repository import AnalysisRepository
from src.analysis.domain.exceptions import AnalysisNotFoundError


class GetAnalysisQueryHandler:
    """Handler for get analysis query."""
    
    def __init__(self, analysis_repository: AnalysisRepository):
        self._analysis_repository = analysis_repository
    
    async def handle(self, query: GetAnalysisQuery) -> GetAnalysisResult:
        """Handle get analysis query."""
        try:
            from src.analysis.domain.value_objects.analysis_id import AnalysisId
            
            analysis_id = AnalysisId(UUID(query.analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id)
            
            if not analysis:
                return GetAnalysisResult(
                    analysis=None,
                    success=False,
                    message="Analysis not found"
                )
            
            # Convert to DTO
            analysis_dto = AnalysisDto(
                id=str(analysis.id.value),
                conversation_id=analysis.conversation_id,
                status=analysis.status.value,
                overall_score=float(analysis.overall_score.value) if analysis.overall_score else None,
                feedback=analysis.feedback,
                recommendations=[rec.to_dict() for rec in analysis.recommendations],
                sales_metrics=analysis.sales_metrics.to_dict() if analysis.sales_metrics else None,
                metadata=analysis.metadata,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at,
                completed_at=analysis.completed_at
            )
            
            return GetAnalysisResult(
                analysis=analysis_dto,
                success=True,
                message="Analysis retrieved successfully"
            )
        
        except (ValueError, TypeError):
            return GetAnalysisResult(
                analysis=None,
                success=False,
                message="Invalid analysis ID"
            )
        except Exception as e:
            return GetAnalysisResult(
                analysis=None,
                success=False,
                message=f"Failed to get analysis: {str(e)}"
            )


class GetAnalysisByConversationQueryHandler:
    """Handler for get analysis by conversation query."""
    
    def __init__(self, analysis_repository: AnalysisRepository):
        self._analysis_repository = analysis_repository
    
    async def handle(self, query: GetAnalysisByConversationQuery) -> GetAnalysisByConversationResult:
        """Handle get analysis by conversation query."""
        try:
            analysis = await self._analysis_repository.get_by_conversation_id(
                query.conversation_id
            )
            
            if not analysis:
                return GetAnalysisByConversationResult(
                    analysis=None,
                    success=False,
                    message="Analysis not found for this conversation"
                )
            
            # Convert to DTO
            analysis_dto = AnalysisDto(
                id=str(analysis.id.value),
                conversation_id=analysis.conversation_id,
                status=analysis.status.value,
                overall_score=float(analysis.overall_score.value) if analysis.overall_score else None,
                feedback=analysis.feedback,
                recommendations=[rec.to_dict() for rec in analysis.recommendations],
                sales_metrics=analysis.sales_metrics.to_dict() if analysis.sales_metrics else None,
                metadata=analysis.metadata,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at,
                completed_at=analysis.completed_at
            )
            
            return GetAnalysisByConversationResult(
                analysis=analysis_dto,
                success=True,
                message="Analysis retrieved successfully"
            )
        
        except Exception as e:
            return GetAnalysisByConversationResult(
                analysis=None,
                success=False,
                message=f"Failed to get analysis: {str(e)}"
            )


class GetAnalysesQueryHandler:
    """Handler for get analyses query."""
    
    def __init__(self, analysis_repository: AnalysisRepository):
        self._analysis_repository = analysis_repository
    
    async def handle(self, query: GetAnalysesQuery) -> GetAnalysesResult:
        """Handle get analyses query."""
        try:
            # Get analyses based on filters
            if query.status:
                analyses = await self._analysis_repository.get_by_status(
                    query.status, query.limit, query.offset
                )
            else:
                analyses = await self._analysis_repository.get_all(
                    query.limit, query.offset
                )
            
            # Convert to DTOs
            analysis_dtos = [
                AnalysisDto(
                    id=str(analysis.id.value),
                    conversation_id=analysis.conversation_id,
                    status=analysis.status.value,
                    overall_score=float(analysis.overall_score.value) if analysis.overall_score else None,
                    feedback=analysis.feedback,
                    recommendations=[rec.to_dict() for rec in analysis.recommendations],
                    sales_metrics=analysis.sales_metrics.to_dict() if analysis.sales_metrics else None,
                    metadata=analysis.metadata,
                    created_at=analysis.created_at,
                    updated_at=analysis.updated_at,
                    completed_at=analysis.completed_at
                )
                for analysis in analyses
            ]
            
            return GetAnalysesResult(
                analyses=analysis_dtos,
                total_count=len(analysis_dtos),
                success=True,
                message="Analyses retrieved successfully"
            )
        
        except Exception as e:
            return GetAnalysesResult(
                analyses=[],
                total_count=0,
                success=False,
                message=f"Failed to get analyses: {str(e)}"
            )
