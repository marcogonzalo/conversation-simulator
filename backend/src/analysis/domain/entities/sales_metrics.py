"""
Sales metrics entity for the analysis bounded context.
"""
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime

from src.shared.domain.value_objects import MetricScore


@dataclass
class OpeningQualificationMetrics:
    """Metrics for opening and qualification phase."""
    open_questions_rate: float  # Percentage of open-ended questions
    listen_speak_ratio: float   # Ratio of listening to speaking time
    pain_point_identified: bool  # Whether pain points were identified
    qualification_completed: bool  # Whether qualification was completed
    rapport_established: bool  # Whether rapport was established
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'open_questions_rate': self.open_questions_rate,
            'listen_speak_ratio': self.listen_speak_ratio,
            'pain_point_identified': self.pain_point_identified,
            'qualification_completed': self.qualification_completed,
            'rapport_established': self.rapport_established
        }


@dataclass
class PresentationObjectionsMetrics:
    """Metrics for presentation and objections handling."""
    value_points_connected: int  # Number of value points connected to pain points
    objections_handled: int  # Number of objections handled
    evidence_used: int  # Number of evidence pieces used
    presentation_clear: bool  # Whether presentation was clear
    objections_addressed: bool  # Whether objections were properly addressed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value_points_connected': self.value_points_connected,
            'objections_handled': self.objections_handled,
            'evidence_used': self.evidence_used,
            'presentation_clear': self.presentation_clear,
            'objections_addressed': self.objections_addressed
        }


@dataclass
class ClosingNextStepsMetrics:
    """Metrics for closing and next steps."""
    close_attempted: bool  # Whether a close was attempted
    close_successful: bool  # Whether the close was successful
    next_steps_defined: bool  # Whether next steps were defined
    timeline_established: bool  # Whether timeline was established
    commitment_obtained: bool  # Whether commitment was obtained
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'close_attempted': self.close_attempted,
            'close_successful': self.close_successful,
            'next_steps_defined': self.next_steps_defined,
            'timeline_established': self.timeline_established,
            'commitment_obtained': self.commitment_obtained
        }


@dataclass
class CommunicationMetrics:
    """Metrics for communication effectiveness."""
    clarity_score: float  # 0-100 score for message clarity
    engagement_score: float  # 0-100 score for engagement
    empathy_score: float  # 0-100 score for empathy
    confidence_score: float  # 0-100 score for confidence
    active_listening_score: float  # 0-100 score for active listening
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'clarity_score': self.clarity_score,
            'engagement_score': self.engagement_score,
            'empathy_score': self.empathy_score,
            'confidence_score': self.confidence_score,
            'active_listening_score': self.active_listening_score
        }


@dataclass
class SalesMetrics:
    """Sales metrics aggregate."""
    opening_qualification: OpeningQualificationMetrics
    presentation_objections: PresentationObjectionsMetrics
    closing_next_steps: ClosingNextStepsMetrics
    communication: CommunicationMetrics
    overall_score: MetricScore
    conversation_duration_minutes: float
    message_count: int
    user_speak_ratio: float
    analysis_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'opening_qualification': self.opening_qualification.to_dict(),
            'presentation_objections': self.presentation_objections.to_dict(),
            'closing_next_steps': self.closing_next_steps.to_dict(),
            'communication': self.communication.to_dict(),
            'overall_score': float(self.overall_score.value),
            'conversation_duration_minutes': self.conversation_duration_minutes,
            'message_count': self.message_count,
            'user_speak_ratio': self.user_speak_ratio,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }
    
    def get_strengths(self) -> List[str]:
        """Get list of strengths based on metrics."""
        strengths = []
        
        if self.opening_qualification.open_questions_rate > 0.7:
            strengths.append("Excellent use of open-ended questions")
        
        if self.opening_qualification.listen_speak_ratio > 0.6:
            strengths.append("Good listening skills")
        
        if self.opening_qualification.pain_point_identified:
            strengths.append("Successfully identified pain points")
        
        if self.presentation_objections.value_points_connected > 3:
            strengths.append("Strong value proposition connection")
        
        if self.presentation_objections.objections_handled > 2:
            strengths.append("Effective objection handling")
        
        if self.closing_next_steps.close_attempted:
            strengths.append("Attempted to close the sale")
        
        if self.closing_next_steps.next_steps_defined:
            strengths.append("Clear next steps defined")
        
        if self.communication.clarity_score > 80:
            strengths.append("Clear communication")
        
        if self.communication.engagement_score > 80:
            strengths.append("High engagement level")
        
        if self.communication.empathy_score > 80:
            strengths.append("Strong empathy")
        
        return strengths
    
    def get_areas_for_improvement(self) -> List[str]:
        """Get list of areas for improvement based on metrics."""
        improvements = []
        
        if self.opening_qualification.open_questions_rate < 0.5:
            improvements.append("Use more open-ended questions")
        
        if self.opening_qualification.listen_speak_ratio < 0.4:
            improvements.append("Listen more, speak less")
        
        if not self.opening_qualification.pain_point_identified:
            improvements.append("Focus on identifying pain points")
        
        if self.presentation_objections.value_points_connected < 2:
            improvements.append("Connect more value points to pain points")
        
        if self.presentation_objections.objections_handled < 1:
            improvements.append("Address objections more effectively")
        
        if not self.closing_next_steps.close_attempted:
            improvements.append("Attempt to close the sale")
        
        if not self.closing_next_steps.next_steps_defined:
            improvements.append("Define clear next steps")
        
        if self.communication.clarity_score < 70:
            improvements.append("Improve message clarity")
        
        if self.communication.engagement_score < 70:
            improvements.append("Increase engagement level")
        
        if self.communication.empathy_score < 70:
            improvements.append("Show more empathy")
        
        return improvements
    
    def get_performance_level(self) -> str:
        """Get overall performance level."""
        score = float(self.overall_score.value)
        
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Satisfactory"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
