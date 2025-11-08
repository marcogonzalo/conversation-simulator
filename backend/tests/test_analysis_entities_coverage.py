"""
Tests for analysis domain entities covering value objects and aggregate behavior.
"""
from datetime import datetime
from typing import List

import pytest

from src.analysis.domain.entities.analysis import Analysis, AnalysisStatus
from src.analysis.domain.entities.sales_metrics import (
    SalesMetrics,
    OpeningQualificationMetrics,
    PresentationObjectionsMetrics,
    ClosingNextStepsMetrics,
    CommunicationMetrics,
)
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.value_objects.metric_score import MetricScore
from src.analysis.domain.value_objects.recommendation import Recommendation


def _build_sales_metrics(score: float) -> SalesMetrics:
    """Create a representative SalesMetrics instance for aggregate tests."""
    return SalesMetrics(
        opening_qualification=OpeningQualificationMetrics(
            open_questions_rate=0.75,
            listen_speak_ratio=0.65,
            pain_point_identified=True,
            qualification_completed=True,
            rapport_established=True,
        ),
        presentation_objections=PresentationObjectionsMetrics(
            value_points_connected=4,
            objections_handled=2,
            evidence_used=2,
            presentation_clear=True,
            objections_addressed=True,
        ),
        closing_next_steps=ClosingNextStepsMetrics(
            close_attempted=True,
            close_successful=False,
            next_steps_defined=True,
            timeline_established=True,
            commitment_obtained=False,
        ),
        communication=CommunicationMetrics(
            clarity_score=82.0,
            engagement_score=80.0,
            empathy_score=78.0,
            confidence_score=85.0,
            active_listening_score=80.0,
        ),
        overall_score=MetricScore(score),
        conversation_duration_minutes=32.0,
        message_count=18,
        user_speak_ratio=0.45,
        analysis_timestamp=datetime.utcnow(),
    )


class TestAnalysisValueObjects:
    """Basic coverage for analysis value objects."""

    def test_metric_score_creation(self) -> None:
        score = MetricScore(value=75)
        assert score.value == 75

    def test_metric_score_range(self) -> None:
        score0 = MetricScore(value=0)
        score100 = MetricScore(value=100)
        score50 = MetricScore(value=50)

        assert score0.value == 0
        assert score100.value == 100
        assert score50.value == 50

    def test_analysis_status_enum(self) -> None:
        assert AnalysisStatus.PENDING.value == "pending"
        assert AnalysisStatus.COMPLETED.value == "completed"
        assert AnalysisStatus.FAILED.value == "failed"

    def test_metric_score_string_representation(self) -> None:
        score = MetricScore(value=85)
        assert str(score) in {"85", "85.0"}

    def test_metric_score_edge_cases(self) -> None:
        s_min = MetricScore(value=0)
        s_mid = MetricScore(value=50)
        s_max = MetricScore(value=100)

        assert s_min.value == 0
        assert s_mid.value == 50
        assert s_max.value == 100
        assert "50" in str(s_mid)

    def test_metric_score_can_be_compared(self) -> None:
        s1 = MetricScore(value=70)
        s2 = MetricScore(value=85)

        assert s1.value < s2.value
        assert s2.value > s1.value


class TestAnalysisAggregate:
    """Behavioral tests for the Analysis aggregate root."""

    def _create_analysis(self) -> Analysis:
        return Analysis(
            analysis_id=AnalysisId.generate(),
            conversation_id="conversation-123",
        )

    def _recommendations(self) -> List[Recommendation]:
        return [
            Recommendation(
                text="Focus on rapport building at the start of the call",
                category="Opening & Qualification",
                priority=1,
            ),
            Recommendation(
                text="Summarize next steps at the end of the conversation",
                category="Closing",
                priority=2,
            ),
        ]

    def test_analysis_lifecycle_happy_path(self) -> None:
        analysis = self._create_analysis()
        assert analysis.status == AnalysisStatus.PENDING

        analysis.start_analysis()
        assert analysis.status == AnalysisStatus.IN_PROGRESS

        metrics = _build_sales_metrics(score=82.0)
        recommendations = self._recommendations()
        analysis.complete_analysis(
            sales_metrics=metrics,
            overall_score=MetricScore(82.0),
            feedback="Strong qualifying sequence with minor follow-up gaps.",
            recommendations=recommendations,
        )

        assert analysis.status == AnalysisStatus.COMPLETED
        assert analysis.sales_metrics is metrics
        assert analysis.overall_score.value == pytest.approx(82.0)
        assert analysis.feedback and "qualifying" in analysis.feedback
        assert analysis.get_high_priority_recommendations() == [recommendations[0]]
        assert analysis.get_medium_priority_recommendations() == [recommendations[1]]
        assert analysis.get_low_priority_recommendations() == []
        summary = analysis.get_analysis_summary()
        assert summary["status"] == AnalysisStatus.COMPLETED.value
        assert summary["overall_score"] == pytest.approx(82.0)

    def test_start_analysis_invalid_transition(self) -> None:
        analysis = self._create_analysis()
        analysis.start_analysis()

        with pytest.raises(ValueError):
            analysis.start_analysis()

    def test_complete_analysis_requires_in_progress(self) -> None:
        analysis = self._create_analysis()
        metrics = _build_sales_metrics(score=75.0)

        with pytest.raises(ValueError):
            analysis.complete_analysis(
                sales_metrics=metrics,
                overall_score=MetricScore(75.0),
                feedback="",
                recommendations=[],
            )

    def test_fail_analysis_records_reason(self) -> None:
        analysis = self._create_analysis()
        analysis.fail_analysis("transcription timeout")

        assert analysis.status == AnalysisStatus.FAILED
        assert analysis.metadata["error_message"] == "transcription timeout"

    def test_add_recommendation_only_before_completion(self) -> None:
        analysis = self._create_analysis()
        recommendation = Recommendation(
            text="Clarify pricing tiers earlier in the conversation",
            category="Presentation",
            priority=1,
        )

        analysis.add_recommendation(recommendation)
        assert analysis.recommendations == [recommendation]

        analysis.start_analysis()
        analysis.complete_analysis(
            sales_metrics=_build_sales_metrics(score=78.0),
            overall_score=MetricScore(78.0),
            feedback="",
            recommendations=[recommendation],
        )

        with pytest.raises(ValueError):
            analysis.add_recommendation(recommendation)

    def test_analysis_strengths_and_improvements(self) -> None:
        analysis = self._create_analysis()
        metrics = _build_sales_metrics(score=88.0)
        analysis.start_analysis()
        analysis.complete_analysis(
            sales_metrics=metrics,
            overall_score=MetricScore(88.0),
            feedback="",
            recommendations=self._recommendations(),
        )

        strengths = analysis.sales_metrics.get_strengths()
        improvements = analysis.sales_metrics.get_areas_for_improvement()

        assert "Attempted to close the sale" in strengths
        assert "Clarify" not in improvements
        assert all(isinstance(item, str) for item in strengths + improvements)

    def test_update_metadata_is_mutable(self) -> None:
        analysis = self._create_analysis()
        analysis.update_metadata("attempts", 1)
        analysis.update_metadata("attempts", 2)

        assert analysis.metadata["attempts"] == 2
