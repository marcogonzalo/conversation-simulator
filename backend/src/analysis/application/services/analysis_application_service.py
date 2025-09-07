"""
Analysis application service.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.analysis.application.commands.analyze_conversation import (
    AnalyzeConversationCommand, AnalyzeConversationResult,
    GetAnalysisCommand, GetAnalysisResult,
    UpdateAnalysisCommand, UpdateAnalysisResult,
    DeleteAnalysisCommand, DeleteAnalysisResult
)
from src.analysis.application.queries.get_analysis import (
    GetAnalysisQuery, GetAnalysisResult, AnalysisDto,
    GetAnalysisByConversationQuery, GetAnalysisByConversationResult,
    GetAnalysesQuery, GetAnalysesResult
)
from src.analysis.application.handlers.command_handlers import (
    AnalyzeConversationCommandHandler, GetAnalysisCommandHandler,
    UpdateAnalysisCommandHandler, DeleteAnalysisCommandHandler
)
from src.analysis.application.handlers.query_handlers import (
    GetAnalysisQueryHandler, GetAnalysisByConversationQueryHandler,
    GetAnalysesQueryHandler
)
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.services.analysis_service import AnalysisService
from src.analysis.domain.repositories.analysis_repository import AnalysisRepository


class AnalysisApplicationService:
    """Application service for analysis operations."""
    
    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        analysis_service: AnalysisService
    ):
        self._analysis_repository = analysis_repository
        self._analysis_service = analysis_service
        
        # Initialize handlers
        self._analyze_conversation_handler = AnalyzeConversationCommandHandler(
            analysis_repository, analysis_service
        )
        self._get_analysis_handler = GetAnalysisCommandHandler(
            analysis_repository, analysis_service
        )
        self._update_analysis_handler = UpdateAnalysisCommandHandler(
            analysis_repository, analysis_service
        )
        self._delete_analysis_handler = DeleteAnalysisCommandHandler(
            analysis_repository, analysis_service
        )
        
        self._get_analysis_query_handler = GetAnalysisQueryHandler(
            analysis_repository
        )
        self._get_analysis_by_conversation_handler = GetAnalysisByConversationQueryHandler(
            analysis_repository
        )
        self._get_analyses_handler = GetAnalysesQueryHandler(
            analysis_repository
        )
    
    # Command operations
    async def analyze_conversation(
        self,
        conversation_id: str,
        conversation_data: Dict[str, Any]
    ) -> AnalyzeConversationResult:
        """Analyze a conversation."""
        command = AnalyzeConversationCommand(
            conversation_id=conversation_id,
            conversation_data=conversation_data
        )
        return await self._analyze_conversation_handler.handle(command)
    
    async def get_analysis(self, analysis_id: str) -> GetAnalysisResult:
        """Get an analysis by ID."""
        command = GetAnalysisCommand(analysis_id=analysis_id)
        return await self._get_analysis_handler.handle(command)
    
    async def update_analysis(
        self,
        analysis_id: str,
        feedback: Optional[str] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UpdateAnalysisResult:
        """Update an analysis."""
        command = UpdateAnalysisCommand(
            analysis_id=analysis_id,
            feedback=feedback,
            recommendations=recommendations,
            metadata=metadata
        )
        return await self._update_analysis_handler.handle(command)
    
    async def delete_analysis(self, analysis_id: str) -> DeleteAnalysisResult:
        """Delete an analysis."""
        command = DeleteAnalysisCommand(analysis_id=analysis_id)
        return await self._delete_analysis_handler.handle(command)
    
    # Query operations
    async def get_analysis_by_id(self, analysis_id: str) -> GetAnalysisResult:
        """Get analysis by ID."""
        query = GetAnalysisQuery(analysis_id=analysis_id)
        return await self._get_analysis_query_handler.handle(query)
    
    async def get_analysis_by_conversation(self, conversation_id: str) -> GetAnalysisByConversationResult:
        """Get analysis by conversation ID."""
        query = GetAnalysisByConversationQuery(conversation_id=conversation_id)
        return await self._get_analysis_by_conversation_handler.handle(query)
    
    async def get_analyses(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> GetAnalysesResult:
        """Get analyses with optional filters."""
        query = GetAnalysesQuery(
            status=status,
            limit=limit,
            offset=offset
        )
        return await self._get_analyses_handler.handle(query)
    
    # Domain service operations
    async def get_analysis_summary(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis summary."""
        try:
            analysis_id_obj = AnalysisId(UUID(analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id_obj)
            
            if not analysis:
                return None
            
            return analysis.get_analysis_summary()
        
        except Exception:
            return None
    
    async def get_high_priority_recommendations(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get high priority recommendations for an analysis."""
        try:
            analysis_id_obj = AnalysisId(UUID(analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id_obj)
            
            if not analysis:
                return []
            
            return [rec.to_dict() for rec in analysis.get_high_priority_recommendations()]
        
        except Exception:
            return []
    
    async def get_analysis_metrics(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis metrics."""
        try:
            analysis_id_obj = AnalysisId(UUID(analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id_obj)
            
            if not analysis or not analysis.sales_metrics:
                return None
            
            return analysis.sales_metrics.to_dict()
        
        except Exception:
            return None
    
    async def get_analysis_strengths(self, analysis_id: str) -> List[str]:
        """Get analysis strengths."""
        try:
            analysis_id_obj = AnalysisId(UUID(analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id_obj)
            
            if not analysis or not analysis.sales_metrics:
                return []
            
            return analysis.sales_metrics.get_strengths()
        
        except Exception:
            return []
    
    async def get_analysis_improvements(self, analysis_id: str) -> List[str]:
        """Get analysis areas for improvement."""
        try:
            analysis_id_obj = AnalysisId(UUID(analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id_obj)
            
            if not analysis or not analysis.sales_metrics:
                return []
            
            return analysis.sales_metrics.get_areas_for_improvement()
        
        except Exception:
            return []
    
    async def get_analysis_performance_level(self, analysis_id: str) -> Optional[str]:
        """Get analysis performance level."""
        try:
            analysis_id_obj = AnalysisId(UUID(analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id_obj)
            
            if not analysis or not analysis.sales_metrics:
                return None
            
            return analysis.sales_metrics.get_performance_level()
        
        except Exception:
            return None
    
    async def validate_conversation_for_analysis(self, conversation_data: Dict[str, Any]) -> bool:
        """Validate conversation data for analysis."""
        try:
            return self._analysis_service.validate_analysis_data(conversation_data)
        except Exception:
            return False
