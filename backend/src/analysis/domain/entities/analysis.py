"""
Analysis entity for the analysis bounded context.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from src.shared.domain.value_objects import EntityId
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.value_objects.metric_score import MetricScore
from src.analysis.domain.value_objects.recommendation import Recommendation
from src.analysis.domain.entities.sales_metrics import SalesMetrics


class AnalysisStatus(Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis:
    """Analysis aggregate root."""
    
    def __init__(
        self,
        analysis_id: AnalysisId,
        conversation_id: str,
        status: AnalysisStatus = AnalysisStatus.PENDING,
        sales_metrics: Optional[SalesMetrics] = None,
        overall_score: Optional[MetricScore] = None,
        feedback: Optional[str] = None,
        recommendations: Optional[List[Recommendation]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._id = analysis_id
        self._conversation_id = conversation_id
        self._status = status
        self._sales_metrics = sales_metrics
        self._overall_score = overall_score
        self._feedback = feedback
        self._recommendations = recommendations or []
        self._metadata = metadata or {}
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._completed_at: Optional[datetime] = None
    
    @property
    def id(self) -> AnalysisId:
        return self._id
    
    @property
    def conversation_id(self) -> str:
        return self._conversation_id
    
    @property
    def status(self) -> AnalysisStatus:
        return self._status
    
    @property
    def sales_metrics(self) -> Optional[SalesMetrics]:
        return self._sales_metrics
    
    @property
    def overall_score(self) -> Optional[MetricScore]:
        return self._overall_score
    
    @property
    def feedback(self) -> Optional[str]:
        return self._feedback
    
    @property
    def recommendations(self) -> List[Recommendation]:
        return self._recommendations.copy()
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    def start_analysis(self) -> None:
        """Start the analysis process."""
        if self._status != AnalysisStatus.PENDING:
            raise ValueError("Analysis can only be started from pending status")
        
        self._status = AnalysisStatus.IN_PROGRESS
        self._updated_at = datetime.utcnow()
    
    def complete_analysis(
        self,
        sales_metrics: SalesMetrics,
        overall_score: MetricScore,
        feedback: str,
        recommendations: List[Recommendation]
    ) -> None:
        """Complete the analysis with results."""
        if self._status != AnalysisStatus.IN_PROGRESS:
            raise ValueError("Analysis can only be completed from in_progress status")
        
        self._sales_metrics = sales_metrics
        self._overall_score = overall_score
        self._feedback = feedback
        self._recommendations = recommendations
        self._status = AnalysisStatus.COMPLETED
        self._completed_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    def fail_analysis(self, error_message: str) -> None:
        """Mark analysis as failed."""
        if self._status not in [AnalysisStatus.PENDING, AnalysisStatus.IN_PROGRESS]:
            raise ValueError("Analysis can only be failed from pending or in_progress status")
        
        self._status = AnalysisStatus.FAILED
        self._metadata['error_message'] = error_message
        self._updated_at = datetime.utcnow()
    
    def add_recommendation(self, recommendation: Recommendation) -> None:
        """Add a recommendation to the analysis."""
        if self._status == AnalysisStatus.COMPLETED:
            raise ValueError("Cannot add recommendations to completed analysis")
        
        self._recommendations.append(recommendation)
        self._updated_at = datetime.utcnow()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update analysis metadata."""
        self._metadata[key] = value
        self._updated_at = datetime.utcnow()
    
    def is_completed(self) -> bool:
        """Check if analysis is completed."""
        return self._status == AnalysisStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if analysis failed."""
        return self._status == AnalysisStatus.FAILED
    
    def is_in_progress(self) -> bool:
        """Check if analysis is in progress."""
        return self._status == AnalysisStatus.IN_PROGRESS
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        return {
            'id': str(self._id.value),
            'conversation_id': self._conversation_id,
            'status': self._status.value,
            'overall_score': float(self._overall_score.value) if self._overall_score else None,
            'recommendations_count': len(self._recommendations),
            'has_feedback': bool(self._feedback),
            'has_metrics': bool(self._sales_metrics),
            'created_at': self._created_at.isoformat(),
            'completed_at': self._completed_at.isoformat() if self._completed_at else None
        }
    
    def get_high_priority_recommendations(self) -> List[Recommendation]:
        """Get high priority recommendations."""
        return [r for r in self._recommendations if r.priority == 1]
    
    def get_medium_priority_recommendations(self) -> List[Recommendation]:
        """Get medium priority recommendations."""
        return [r for r in self._recommendations if r.priority == 2]
    
    def get_low_priority_recommendations(self) -> List[Recommendation]:
        """Get low priority recommendations."""
        return [r for r in self._recommendations if r.priority == 3]
