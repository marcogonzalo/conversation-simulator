"""
AI analysis service for infrastructure layer.
"""
from typing import Dict, Any, List
import json

from src.analysis.domain.entities.sales_metrics import ClosingNextStepsMetrics, CommunicationMetrics, OpeningQualificationMetrics, PresentationObjectionsMetrics, SalesMetrics
from src.analysis.domain.value_objects.metric_score import MetricScore
from src.analysis.domain.value_objects.recommendation import Recommendation
from src.analysis.domain.exceptions import AnalysisFailedError
from src.shared.infrastructure.external_apis.api_config import api_config
from src.shared.infrastructure.external_apis.ai_service_factory import AIServiceFactory


class AIAnalysisService:
    """Service for AI-powered conversation analysis."""
    
    def __init__(self, ai_provider: str = None, api_key: str = None):
        self.ai_provider = ai_provider or api_config.ai_provider
        self.api_key = api_key
        self.api_config = api_config
        
        # Initialize AI service using factory
        self.ai_service = AIServiceFactory.create_ai_service(self.ai_provider, self.api_key)
    
    async def analyze_conversation(self, conversation_data: Dict[str, Any]) -> SalesMetrics:
        """Analyze conversation using AI."""
        try:
            # This is a placeholder implementation
            # In a real system, this would use OpenAI GPT-4o-mini-realtime to analyze the conversation
            
            messages = conversation_data.get('messages', [])
            duration_seconds = conversation_data.get('duration_seconds', 0)
            
            # Simulate AI analysis
            analysis_result = await self._simulate_ai_analysis(messages, duration_seconds)
            
            return analysis_result
        
        except Exception as e:
            raise AnalysisFailedError("ai_analysis", f"AI analysis failed: {str(e)}")
    
    async def _simulate_ai_analysis(self, messages: List[Dict], duration_seconds: int) -> SalesMetrics:
        """Simulate AI analysis for MVP."""
        from datetime import datetime
        from src.analysis.domain.entities.sales_metrics import (
            OpeningQualificationMetrics, PresentationObjectionsMetrics,
            ClosingNextStepsMetrics, CommunicationMetrics
        )
        
        # Count user and assistant messages
        user_messages = [m for m in messages if m.get('role') == 'user']
        assistant_messages = [m for m in messages if m.get('role') == 'assistant']
        
        total_messages = len(messages)
        user_speak_ratio = len(user_messages) / total_messages if total_messages > 0 else 0
        duration_minutes = duration_seconds / 60
        
        # Simulate analysis based on conversation characteristics
        # In a real implementation, this would use NLP to analyze the actual content
        
        # Opening and qualification metrics
        opening_qualification = OpeningQualificationMetrics(
            open_questions_rate=min(0.7 + (len(user_messages) * 0.05), 1.0),
            listen_speak_ratio=min(0.6 + (user_speak_ratio * 0.2), 1.0),
            pain_point_identified=len(user_messages) > 3,
            qualification_completed=len(assistant_messages) > 2,
            rapport_established=len(messages) > 5
        )
        
        # Presentation and objections metrics
        presentation_objections = PresentationObjectionsMetrics(
            value_points_connected=min(len(assistant_messages) // 2, 5),
            objections_handled=min(len(user_messages) // 3, 3),
            evidence_used=min(len(assistant_messages) // 3, 4),
            presentation_clear=len(assistant_messages) > 1,
            objections_addressed=len(user_messages) > 2
        )
        
        # Closing and next steps metrics
        closing_next_steps = ClosingNextStepsMetrics(
            close_attempted=len(assistant_messages) > 3,
            close_successful=len(messages) > 8,
            next_steps_defined=len(assistant_messages) > 2,
            timeline_established=len(messages) > 6,
            commitment_obtained=len(messages) > 10
        )
        
        # Communication metrics
        communication = CommunicationMetrics(
            clarity_score=min(70 + (len(assistant_messages) * 2), 95),
            engagement_score=min(65 + (len(user_messages) * 3), 90),
            empathy_score=min(60 + (len(messages) * 2), 85),
            confidence_score=min(75 + (len(assistant_messages) * 2), 95),
            active_listening_score=min(70 + (user_speak_ratio * 20), 90)
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            opening_qualification, presentation_objections,
            closing_next_steps, communication
        )
        
        return SalesMetrics(
            opening_qualification=opening_qualification,
            presentation_objections=presentation_objections,
            closing_next_steps=closing_next_steps,
            communication=communication,
            overall_score=overall_score,
            conversation_duration_minutes=duration_minutes,
            message_count=total_messages,
            user_speak_ratio=user_speak_ratio,
            analysis_timestamp=datetime.utcnow()
        )
    
    def _calculate_overall_score(
        self,
        opening_qualification: OpeningQualificationMetrics,
        presentation_objections: PresentationObjectionsMetrics,
        closing_next_steps: ClosingNextStepsMetrics,
        communication: CommunicationMetrics
    ) -> MetricScore:
        """Calculate overall score from metrics."""
        # Weighted scoring system
        weights = {
            'opening_qualification': 0.25,
            'presentation_objections': 0.30,
            'closing_next_steps': 0.25,
            'communication': 0.20
        }
        
        # Calculate weighted scores
        opening_score = self._calculate_opening_score(opening_qualification)
        presentation_score = self._calculate_presentation_score(presentation_objections)
        closing_score = self._calculate_closing_score(closing_next_steps)
        communication_score = self._calculate_communication_score(communication)
        
        # Calculate weighted average
        overall_score = (
            opening_score * weights['opening_qualification'] +
            presentation_score * weights['presentation_objections'] +
            closing_score * weights['closing_next_steps'] +
            communication_score * weights['communication']
        )
        
        return MetricScore(overall_score)
    
    def _calculate_opening_score(self, metrics: OpeningQualificationMetrics) -> float:
        """Calculate opening and qualification score."""
        score = 0.0
        
        # Open questions rate (0-30 points)
        score += min(metrics.open_questions_rate * 30, 30)
        
        # Listen/speak ratio (0-25 points)
        score += min(metrics.listen_speak_ratio * 25, 25)
        
        # Pain point identification (0-20 points)
        if metrics.pain_point_identified:
            score += 20
        
        # Qualification completion (0-15 points)
        if metrics.qualification_completed:
            score += 15
        
        # Rapport establishment (0-10 points)
        if metrics.rapport_established:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_presentation_score(self, metrics: PresentationObjectionsMetrics) -> float:
        """Calculate presentation and objections score."""
        score = 0.0
        
        # Value points connected (0-30 points)
        score += min(metrics.value_points_connected * 10, 30)
        
        # Objections handled (0-25 points)
        score += min(metrics.objections_handled * 12.5, 25)
        
        # Evidence used (0-20 points)
        score += min(metrics.evidence_used * 6.67, 20)
        
        # Presentation clarity (0-15 points)
        if metrics.presentation_clear:
            score += 15
        
        # Objections addressed (0-10 points)
        if metrics.objections_addressed:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_closing_score(self, metrics: ClosingNextStepsMetrics) -> float:
        """Calculate closing and next steps score."""
        score = 0.0
        
        # Close attempted (0-30 points)
        if metrics.close_attempted:
            score += 30
        
        # Close successful (0-25 points)
        if metrics.close_successful:
            score += 25
        
        # Next steps defined (0-20 points)
        if metrics.next_steps_defined:
            score += 20
        
        # Timeline established (0-15 points)
        if metrics.timeline_established:
            score += 15
        
        # Commitment obtained (0-10 points)
        if metrics.commitment_obtained:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_communication_score(self, metrics: CommunicationMetrics) -> float:
        """Calculate communication score."""
        return (
            metrics.clarity_score * 0.25 +
            metrics.engagement_score * 0.25 +
            metrics.empathy_score * 0.25 +
            metrics.confidence_score * 0.15 +
            metrics.active_listening_score * 0.10
        )
    
    async def generate_recommendations(self, sales_metrics: SalesMetrics) -> List[Recommendation]:
        """Generate AI-powered recommendations."""
        recommendations = []
        
        # Opening and qualification recommendations
        if sales_metrics.opening_qualification.open_questions_rate < 0.6:
            recommendations.append(Recommendation(
                text="Increase the use of open-ended questions to better understand customer needs",
                category="Opening & Qualification",
                priority=1
            ))
        
        if sales_metrics.opening_qualification.listen_speak_ratio < 0.5:
            recommendations.append(Recommendation(
                text="Practice active listening - aim for a 60/40 listen/speak ratio",
                category="Communication",
                priority=1
            ))
        
        if not sales_metrics.opening_qualification.pain_point_identified:
            recommendations.append(Recommendation(
                text="Focus on identifying and understanding customer pain points early in the conversation",
                category="Opening & Qualification",
                priority=1
            ))
        
        # Presentation and objections recommendations
        if sales_metrics.presentation_objections.value_points_connected < 3:
            recommendations.append(Recommendation(
                text="Connect more value propositions to specific customer pain points",
                category="Presentation",
                priority=2
            ))
        
        if sales_metrics.presentation_objections.objections_handled < 2:
            recommendations.append(Recommendation(
                text="Develop stronger objection handling techniques and practice common objections",
                category="Objection Handling",
                priority=1
            ))
        
        # Closing recommendations
        if not sales_metrics.closing_next_steps.close_attempted:
            recommendations.append(Recommendation(
                text="Practice different closing techniques and don't be afraid to ask for the sale",
                category="Closing",
                priority=1
            ))
        
        if not sales_metrics.closing_next_steps.next_steps_defined:
            recommendations.append(Recommendation(
                text="Always define clear next steps and timeline with the customer",
                category="Closing",
                priority=1
            ))
        
        # Communication recommendations
        if sales_metrics.communication.clarity_score < 75:
            recommendations.append(Recommendation(
                text="Work on message clarity - practice explaining complex concepts simply",
                category="Communication",
                priority=2
            ))
        
        if sales_metrics.communication.engagement_score < 75:
            recommendations.append(Recommendation(
                text="Increase engagement by asking more questions and showing genuine interest",
                category="Communication",
                priority=2
            ))
        
        return recommendations
    
    async def generate_feedback(self, sales_metrics: SalesMetrics, overall_score: MetricScore) -> str:
        """Generate AI-powered feedback."""
        score_value = float(overall_score.value)
        
        if score_value >= 90:
            feedback = "Outstanding performance! You demonstrated excellent sales skills across all areas."
        elif score_value >= 80:
            feedback = "Great job! You showed strong sales skills with room for minor improvements."
        elif score_value >= 70:
            feedback = "Good performance with several areas for improvement. Focus on the recommendations below."
        elif score_value >= 60:
            feedback = "Satisfactory performance but significant improvement needed in key areas."
        else:
            feedback = "This conversation needs substantial improvement. Focus on the fundamentals first."
        
        # Add specific feedback based on metrics
        strengths = sales_metrics.get_strengths()
        if strengths:
            feedback += f"\n\nStrengths:\n• " + "\n• ".join(strengths)
        
        improvements = sales_metrics.get_areas_for_improvement()
        if improvements:
            feedback += f"\n\nAreas for Improvement:\n• " + "\n• ".join(improvements)
        
        return feedback
