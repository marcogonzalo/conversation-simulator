"""
Analyze conversation command.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from src.analysis.domain.value_objects.analysis_id import AnalysisId


@dataclass
class AnalyzeConversationCommand:
    """Command to analyze a conversation."""
    conversation_id: str
    conversation_data: Dict[str, Any]
    
    def __post_init__(self):
        if not self.conversation_id or not self.conversation_id.strip():
            raise ValueError("Conversation ID is required")
        
        if not self.conversation_data:
            raise ValueError("Conversation data is required")


@dataclass
class AnalyzeConversationResult:
    """Result of analyzing a conversation."""
    analysis_id: Optional[AnalysisId]
    success: bool
    message: Optional[str] = None


@dataclass
class GetAnalysisCommand:
    """Command to get an analysis."""
    analysis_id: str
    
    def __post_init__(self):
        if not self.analysis_id or not self.analysis_id.strip():
            raise ValueError("Analysis ID is required")


@dataclass
class GetAnalysisResult:
    """Result of getting an analysis."""
    analysis_id: Optional[AnalysisId]
    success: bool
    message: Optional[str] = None


@dataclass
class UpdateAnalysisCommand:
    """Command to update an analysis."""
    analysis_id: str
    feedback: Optional[str] = None
    recommendations: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.analysis_id or not self.analysis_id.strip():
            raise ValueError("Analysis ID is required")


@dataclass
class UpdateAnalysisResult:
    """Result of updating an analysis."""
    analysis_id: Optional[AnalysisId]
    success: bool
    message: Optional[str] = None


@dataclass
class DeleteAnalysisCommand:
    """Command to delete an analysis."""
    analysis_id: str
    
    def __post_init__(self):
        if not self.analysis_id or not self.analysis_id.strip():
            raise ValueError("Analysis ID is required")


@dataclass
class DeleteAnalysisResult:
    """Result of deleting an analysis."""
    success: bool
    message: Optional[str] = None
