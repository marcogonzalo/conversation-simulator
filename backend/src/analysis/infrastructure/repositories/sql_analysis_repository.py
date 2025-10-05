"""
SQL implementation of analysis repository.
"""
import json
from typing import List, Optional
from pathlib import Path
from uuid import UUID

from src.analysis.domain.entities.analysis import Analysis, AnalysisStatus
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.value_objects.metric_score import MetricScore
from src.analysis.domain.value_objects.recommendation import Recommendation
from src.analysis.domain.entities.sales_metrics import (
    SalesMetrics, OpeningQualificationMetrics, PresentationObjectionsMetrics,
    ClosingNextStepsMetrics, CommunicationMetrics
)
from src.analysis.domain.repositories.analysis_repository import AnalysisRepository


class SQLAnalysisRepository(AnalysisRepository):
    """SQL implementation of analysis repository."""
    
    def __init__(self, analyses_dir: str = "data/analyses"):
        self.analyses_dir = Path(analyses_dir)
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, analysis: Analysis) -> None:
        """Save an analysis."""
        analysis_data = self._analysis_to_dict(analysis)
        analysis_file = self.analyses_dir / f"{analysis.id.value}.json"
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, default=str, indent=2)
    
    async def get_by_id(self, analysis_id: AnalysisId) -> Optional[Analysis]:
        """Get analysis by ID."""
        analysis_file = self.analyses_dir / f"{analysis_id.value}.json"
        
        if not analysis_file.exists():
            return None
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
                return self._dict_to_analysis(analysis_data)
        except Exception as e:
            # Log error but don't print to console
            return None
    
    async def get_by_conversation_id(self, conversation_id: str) -> Optional[Analysis]:
        """Get analysis by conversation ID."""
        all_analyses = await self.get_all(limit=1000, offset=0)
        for analysis in all_analyses:
            if analysis.conversation_id == conversation_id:
                return analysis
        return None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Analysis]:
        """Get all analyses with pagination."""
        analyses = []
        
        for json_file in self.analyses_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    analysis = self._dict_to_analysis(analysis_data)
                    if analysis:
                        analyses.append(analysis)
            except Exception as e:
                # Log error but don't print to console
                continue
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x.created_at, reverse=True)
        
        return analyses[offset:offset + limit]
    
    async def get_by_status(self, status: str, limit: int = 100, offset: int = 0) -> List[Analysis]:
        """Get analyses by status."""
        all_analyses = await self.get_all(limit=1000, offset=0)
        filtered_analyses = [a for a in all_analyses if a.status.value == status]
        
        return filtered_analyses[offset:offset + limit]
    
    async def delete(self, analysis_id: AnalysisId) -> bool:
        """Delete an analysis."""
        analysis_file = self.analyses_dir / f"{analysis_id.value}.json"
        
        if analysis_file.exists():
            analysis_file.unlink()
            return True
        return False
    
    async def exists(self, analysis_id: AnalysisId) -> bool:
        """Check if analysis exists."""
        analysis_file = self.analyses_dir / f"{analysis_id.value}.json"
        return analysis_file.exists()
    
    def _analysis_to_dict(self, analysis: Analysis) -> dict:
        """Convert analysis entity to dictionary."""
        return {
            'id': str(analysis.id.value),
            'conversation_id': analysis.conversation_id,
            'status': analysis.status.value,
            'sales_metrics': analysis.sales_metrics.to_dict() if analysis.sales_metrics else None,
            'overall_score': float(analysis.overall_score.value) if analysis.overall_score else None,
            'feedback': analysis.feedback,
            'recommendations': [rec.to_dict() for rec in analysis.recommendations],
            'metadata': analysis.metadata,
            'created_at': analysis.created_at.isoformat(),
            'updated_at': analysis.updated_at.isoformat(),
            'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None
        }
    
    def _dict_to_analysis(self, data: dict) -> Optional[Analysis]:
        """Convert dictionary to analysis entity."""
        try:
            from datetime import datetime
            
            # Create analysis
            analysis = Analysis(
                analysis_id=AnalysisId(UUID(data['id'])),
                conversation_id=data['conversation_id'],
                status=AnalysisStatus(data['status']),
                metadata=data.get('metadata', {})
            )
            
            # Set timestamps
            analysis._created_at = datetime.fromisoformat(data['created_at'])
            analysis._updated_at = datetime.fromisoformat(data['updated_at'])
            if data.get('completed_at'):
                analysis._completed_at = datetime.fromisoformat(data['completed_at'])
            
            # Set sales metrics if available
            if data.get('sales_metrics'):
                sales_metrics_data = data['sales_metrics']
                analysis._sales_metrics = self._dict_to_sales_metrics(sales_metrics_data)
            
            # Set overall score if available
            if data.get('overall_score') is not None:
                analysis._overall_score = MetricScore(data['overall_score'])
            
            # Set feedback if available
            if data.get('feedback'):
                analysis._feedback = data['feedback']
            
            # Set recommendations if available
            if data.get('recommendations'):
                recommendations = []
                for rec_data in data['recommendations']:
                    recommendation = Recommendation(
                        text=rec_data['text'],
                        category=rec_data['category'],
                        priority=rec_data.get('priority', 1)
                    )
                    recommendations.append(recommendation)
                analysis._recommendations = recommendations
            
            return analysis
        
        except Exception as e:
            # Log error but don't print to console
            return None
    
    def _dict_to_sales_metrics(self, data: dict) -> SalesMetrics:
        """Convert dictionary to sales metrics."""
        from datetime import datetime
        
        # Create sub-metrics
        opening_qualification = OpeningQualificationMetrics(
            open_questions_rate=data['opening_qualification']['open_questions_rate'],
            listen_speak_ratio=data['opening_qualification']['listen_speak_ratio'],
            pain_point_identified=data['opening_qualification']['pain_point_identified'],
            qualification_completed=data['opening_qualification']['qualification_completed'],
            rapport_established=data['opening_qualification']['rapport_established']
        )
        
        presentation_objections = PresentationObjectionsMetrics(
            value_points_connected=data['presentation_objections']['value_points_connected'],
            objections_handled=data['presentation_objections']['objections_handled'],
            evidence_used=data['presentation_objections']['evidence_used'],
            presentation_clear=data['presentation_objections']['presentation_clear'],
            objections_addressed=data['presentation_objections']['objections_addressed']
        )
        
        closing_next_steps = ClosingNextStepsMetrics(
            close_attempted=data['closing_next_steps']['close_attempted'],
            close_successful=data['closing_next_steps']['close_successful'],
            next_steps_defined=data['closing_next_steps']['next_steps_defined'],
            timeline_established=data['closing_next_steps']['timeline_established'],
            commitment_obtained=data['closing_next_steps']['commitment_obtained']
        )
        
        communication = CommunicationMetrics(
            clarity_score=data['communication']['clarity_score'],
            engagement_score=data['communication']['engagement_score'],
            empathy_score=data['communication']['empathy_score'],
            confidence_score=data['communication']['confidence_score'],
            active_listening_score=data['communication']['active_listening_score']
        )
        
        return SalesMetrics(
            opening_qualification=opening_qualification,
            presentation_objections=presentation_objections,
            closing_next_steps=closing_next_steps,
            communication=communication,
            overall_score=MetricScore(data['overall_score']),
            conversation_duration_minutes=data['conversation_duration_minutes'],
            message_count=data['message_count'],
            user_speak_ratio=data['user_speak_ratio'],
            analysis_timestamp=datetime.fromisoformat(data['analysis_timestamp'])
        )
