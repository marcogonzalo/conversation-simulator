"""
Get analysis query.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.entities.analysis import AnalysisStatus


@dataclass
class GetAnalysisQuery:
    """Query to get an analysis by ID."""
    analysis_id: str


@dataclass
class GetAnalysisByConversationQuery:
    """Query to get analysis by conversation ID."""
    conversation_id: str


@dataclass
class GetAnalysesQuery:
    """Query to get analyses with filters."""
    status: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class AnalysisDto:
    """Analysis data transfer object."""
    id: str
    conversation_id: str
    status: str
    overall_score: Optional[float]
    feedback: Optional[str]
    recommendations: List[Dict[str, Any]]
    sales_metrics: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


@dataclass
class GetAnalysisResult:
    """Result of getting an analysis."""
    analysis: Optional[AnalysisDto]
    success: bool
    message: Optional[str] = None


@dataclass
class GetAnalysisByConversationResult:
    """Result of getting analysis by conversation."""
    analysis: Optional[AnalysisDto]
    success: bool
    message: Optional[str] = None


@dataclass
class GetAnalysesResult:
    """Result of getting analyses."""
    analyses: List[AnalysisDto]
    total_count: int
    success: bool
    message: Optional[str] = None
