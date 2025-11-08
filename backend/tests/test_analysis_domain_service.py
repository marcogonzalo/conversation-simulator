"""
Focused tests for the analysis domain service logic.
"""
from datetime import datetime
from typing import Dict, Any

import pytest

from src.analysis.domain.entities.sales_metrics import (
    SalesMetrics,
    OpeningQualificationMetrics,
    PresentationObjectionsMetrics,
    ClosingNextStepsMetrics,
    CommunicationMetrics,
)
from src.analysis.domain.exceptions import AnalysisValidationError
from src.analysis.domain.services.analysis_service import AnalysisService
from src.analysis.domain.value_objects.metric_score import MetricScore


@pytest.fixture
def service() -> AnalysisService:
    """Return a fresh AnalysisService instance for each test."""
    return AnalysisService()


def _build_sales_metrics(
    opening: OpeningQualificationMetrics,
    presentation: PresentationObjectionsMetrics,
    closing: ClosingNextStepsMetrics,
    communication: CommunicationMetrics,
    overall_score: float,
) -> SalesMetrics:
    """Helper to assemble SalesMetrics with consistent metadata."""
    return SalesMetrics(
        opening_qualification=opening,
        presentation_objections=presentation,
        closing_next_steps=closing,
        communication=communication,
        overall_score=MetricScore(overall_score),
        conversation_duration_minutes=30.0,
        message_count=20,
        user_speak_ratio=0.5,
        analysis_timestamp=datetime.utcnow(),
    )


def test_calculate_overall_score_weights_all_categories(service: AnalysisService) -> None:
    """Ensure the weighted score considers each metric group correctly."""
    opening = OpeningQualificationMetrics(
        open_questions_rate=0.8,
        listen_speak_ratio=0.7,
        pain_point_identified=True,
        qualification_completed=True,
        rapport_established=True,
    )
    presentation = PresentationObjectionsMetrics(
        value_points_connected=4,
        objections_handled=2,
        evidence_used=3,
        presentation_clear=True,
        objections_addressed=True,
    )
    closing = ClosingNextStepsMetrics(
        close_attempted=True,
        close_successful=True,
        next_steps_defined=True,
        timeline_established=True,
        commitment_obtained=True,
    )
    communication = CommunicationMetrics(
        clarity_score=92.0,
        engagement_score=88.0,
        empathy_score=80.0,
        confidence_score=75.0,
        active_listening_score=70.0,
    )

    metrics = _build_sales_metrics(
        opening=opening,
        presentation=presentation,
        closing=closing,
        communication=communication,
        overall_score=80.0,
    )

    overall = service.calculate_overall_score(metrics)

    assert isinstance(overall, MetricScore)
    assert overall.value == pytest.approx(93.28, rel=1e-3)


def test_generate_recommendations_flags_low_scores(service: AnalysisService) -> None:
    """Low-performing metrics should trigger targeted recommendations."""
    opening = OpeningQualificationMetrics(
        open_questions_rate=0.3,
        listen_speak_ratio=0.35,
        pain_point_identified=False,
        qualification_completed=False,
        rapport_established=False,
    )
    presentation = PresentationObjectionsMetrics(
        value_points_connected=1,
        objections_handled=0,
        evidence_used=0,
        presentation_clear=False,
        objections_addressed=False,
    )
    closing = ClosingNextStepsMetrics(
        close_attempted=False,
        close_successful=False,
        next_steps_defined=False,
        timeline_established=False,
        commitment_obtained=False,
    )
    communication = CommunicationMetrics(
        clarity_score=60.0,
        engagement_score=58.0,
        empathy_score=55.0,
        confidence_score=62.0,
        active_listening_score=59.0,
    )

    metrics = _build_sales_metrics(
        opening=opening,
        presentation=presentation,
        closing=closing,
        communication=communication,
        overall_score=45.0,
    )

    recommendations = service.generate_recommendations(metrics)
    recommendation_texts = {rec.text for rec in recommendations}

    expected = {
        "Increase the use of open-ended questions to better understand customer needs",
        "Practice active listening - aim for a 60/40 listen/speak ratio",
        "Focus on identifying and understanding customer pain points early in the conversation",
        "Connect more value propositions to specific customer pain points",
        "Develop stronger objection handling techniques and practice common objections",
        "Simplify your presentation and use clear, concise language",
        "Practice different closing techniques and don't be afraid to ask for the sale",
        "Always define clear next steps and timeline with the customer",
        "Work on message clarity - practice explaining complex concepts simply",
        "Increase engagement by asking more questions and showing genuine interest",
        "Show more empathy and understanding of customer challenges",
    }

    assert expected.issubset(recommendation_texts)


def test_generate_recommendations_suppressed_when_scores_high(service: AnalysisService) -> None:
    """High-performing metrics should produce no critical recommendations."""
    opening = OpeningQualificationMetrics(
        open_questions_rate=0.9,
        listen_speak_ratio=0.7,
        pain_point_identified=True,
        qualification_completed=True,
        rapport_established=True,
    )
    presentation = PresentationObjectionsMetrics(
        value_points_connected=4,
        objections_handled=3,
        evidence_used=3,
        presentation_clear=True,
        objections_addressed=True,
    )
    closing = ClosingNextStepsMetrics(
        close_attempted=True,
        close_successful=True,
        next_steps_defined=True,
        timeline_established=True,
        commitment_obtained=True,
    )
    communication = CommunicationMetrics(
        clarity_score=90.0,
        engagement_score=88.0,
        empathy_score=86.0,
        confidence_score=90.0,
        active_listening_score=88.0,
    )

    metrics = _build_sales_metrics(
        opening=opening,
        presentation=presentation,
        closing=closing,
        communication=communication,
        overall_score=92.0,
    )

    recommendations = service.generate_recommendations(metrics)

    assert recommendations == []


def test_generate_feedback_includes_strengths_and_improvements(service: AnalysisService) -> None:
    """Feedback should surface strengths and actionable improvements."""
    opening = OpeningQualificationMetrics(
        open_questions_rate=0.82,
        listen_speak_ratio=0.68,
        pain_point_identified=True,
        qualification_completed=True,
        rapport_established=True,
    )
    presentation = PresentationObjectionsMetrics(
        value_points_connected=4,
        objections_handled=3,
        evidence_used=2,
        presentation_clear=True,
        objections_addressed=True,
    )
    closing = ClosingNextStepsMetrics(
        close_attempted=True,
        close_successful=False,
        next_steps_defined=True,
        timeline_established=True,
        commitment_obtained=False,
    )
    communication = CommunicationMetrics(
        clarity_score=84.0,
        engagement_score=83.0,
        empathy_score=65.0,
        confidence_score=80.0,
        active_listening_score=82.0,
    )

    metrics = _build_sales_metrics(
        opening=opening,
        presentation=presentation,
        closing=closing,
        communication=communication,
        overall_score=85.0,
    )

    feedback = service.generate_feedback(metrics, MetricScore(85.0))

    assert "Great job!" in feedback
    assert "Strengths:" in feedback
    assert "Excellent use of open-ended questions" in feedback
    assert "Areas for Improvement:" in feedback
    assert "Show more empathy" in feedback


@pytest.mark.parametrize(
    "conversation_data,expected_error",
    [
        ({}, "Missing required field"),
        (
            {"messages": [], "duration_seconds": 10, "persona_id": "ana"},
            "Conversation must have at least one message",
        ),
        (
            {"messages": [{"role": "user", "content": "hola"}], "duration_seconds": 0, "persona_id": "ana"},
            "Conversation duration must be positive",
        ),
    ],
)
def test_validate_analysis_data_guards_input(
    service: AnalysisService, conversation_data: Dict[str, Any], expected_error: str
) -> None:
    """Validation should raise meaningful errors for invalid payloads."""
    with pytest.raises(AnalysisValidationError) as exc:
        service.validate_analysis_data(conversation_data)

    assert expected_error in str(exc.value)


def test_extract_metrics_from_conversation_builds_sales_metrics(service: AnalysisService) -> None:
    """The extraction helper should compute derived metrics consistently."""
    conversation = {
        "messages": [
            {"role": "user", "content": "Hola, me gustaría saber más del producto."},
            {"role": "ai", "content": "Con gusto, ¿qué te interesa resolver?"},
            {"role": "user", "content": "Necesito mejorar el seguimiento de leads."},
            {"role": "ai", "content": "Tenemos un módulo de automatización ideal para eso."},
        ],
        "duration_seconds": 600,
        "persona_id": "ana_garcia",
    }

    metrics = service.extract_metrics_from_conversation(conversation)

    assert isinstance(metrics, SalesMetrics)
    assert metrics.message_count == 4
    assert metrics.user_speak_ratio == pytest.approx(0.5, abs=1e-2)
    assert metrics.conversation_duration_minutes == pytest.approx(10.0)
    assert metrics.overall_score.value == pytest.approx(79.8, rel=1e-2)
    assert isinstance(metrics.analysis_timestamp, datetime)

