"""
Tests for analysis domain entities
"""
import pytest
from datetime import datetime

from src.analysis.domain.entities.analysis import Analysis, AnalysisStatus
from src.analysis.domain.entities.sales_metrics import SalesMetrics
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.value_objects.metric_score import MetricScore
from src.analysis.domain.value_objects.recommendation import Recommendation


class TestAnalysisEntities:
    """Tests for analysis domain entities"""
    
    def test_analysis_id_creation(self):
        """Test AnalysisId creation"""
        analysis_id = AnalysisId(value="analysis_123")
        assert analysis_id.value == "analysis_123"
    
    def test_analysis_id_string_representation(self):
        """Test AnalysisId string representation"""
        analysis_id = AnalysisId(value="test_id")
        assert str(analysis_id) == "test_id"
    
    def test_metric_score_creation(self):
        """Test MetricScore creation"""
        score = MetricScore(value=75)
        assert score.value == 75
    
    def test_metric_score_range(self):
        """Test MetricScore validates range"""
        # Valid scores
        score0 = MetricScore(value=0)
        score100 = MetricScore(value=100)
        score50 = MetricScore(value=50)
        
        assert score0.value == 0
        assert score100.value == 100
        assert score50.value == 50
    
    def test_recommendation_creation(self):
        """Test Recommendation creation"""
        rec = Recommendation(value="Practice more closing techniques")
        assert rec.value == "Practice more closing techniques"
    
    def test_recommendation_string_representation(self):
        """Test Recommendation string representation"""
        rec = Recommendation(value="Test recommendation")
        assert str(rec) == "Test recommendation"
    
    def test_sales_metrics_creation(self):
        """Test SalesMetrics entity creation"""
        metrics = SalesMetrics(
            rapport_building=MetricScore(value=80),
            needs_discovery=MetricScore(value=75),
            objection_handling=MetricScore(value=70),
            closing_effectiveness=MetricScore(value=65),
            active_listening=MetricScore(value=85),
            effective_questioning=MetricScore(value=78)
        )
        
        assert metrics is not None
        assert metrics.rapport_building.value == 80
    
    def test_sales_metrics_all_scores(self):
        """Test all sales metric scores are accessible"""
        metrics = SalesMetrics(
            rapport_building=MetricScore(value=80),
            needs_discovery=MetricScore(value=75),
            objection_handling=MetricScore(value=70),
            closing_effectiveness=MetricScore(value=65),
            active_listening=MetricScore(value=85),
            effective_questioning=MetricScore(value=78)
        )
        
        assert metrics.rapport_building.value == 80
        assert metrics.needs_discovery.value == 75
        assert metrics.objection_handling.value == 70
        assert metrics.closing_effectiveness.value == 65
        assert metrics.active_listening.value == 85
        assert metrics.effective_questioning.value == 78
    
    def test_analysis_status_enum(self):
        """Test AnalysisStatus enum"""
        assert AnalysisStatus.PENDING.value == "pending"
        assert AnalysisStatus.COMPLETED.value == "completed"
        assert AnalysisStatus.FAILED.value == "failed"
    
    def test_analysis_creation(self):
        """Test Analysis entity creation"""
        metrics = SalesMetrics(
            rapport_building=MetricScore(value=80),
            needs_discovery=MetricScore(value=75),
            objection_handling=MetricScore(value=70),
            closing_effectiveness=MetricScore(value=65),
            active_listening=MetricScore(value=85),
            effective_questioning=MetricScore(value=78)
        )
        
        analysis = Analysis(
            analysis_id=AnalysisId(value="analysis_1"),
            conversation_id="conv_123",
            overall_score=MetricScore(value=75),
            metrics=metrics,
            strengths=[Recommendation(value="Good rapport")],
            weaknesses=[Recommendation(value="Slow closing")],
            recommendations=[Recommendation(value="Practice closing")],
            status=AnalysisStatus.COMPLETED,
            created_at=datetime.now()
        )
        
        assert analysis is not None
        assert analysis.overall_score.value == 75
    
    def test_analysis_status_transitions(self):
        """Test analysis status can be set"""
        metrics = SalesMetrics(
            rapport_building=MetricScore(value=80),
            needs_discovery=MetricScore(value=75),
            objection_handling=MetricScore(value=70),
            closing_effectiveness=MetricScore(value=65),
            active_listening=MetricScore(value=85),
            effective_questioning=MetricScore(value=78)
        )
        
        analysis = Analysis(
            analysis_id=AnalysisId(value="test"),
            conversation_id="conv",
            overall_score=MetricScore(value=75),
            metrics=metrics,
            strengths=[],
            weaknesses=[],
            recommendations=[],
            status=AnalysisStatus.PENDING,
            created_at=datetime.now()
        )
        
        assert analysis.status == AnalysisStatus.PENDING
    
    def test_analysis_with_empty_lists(self):
        """Test analysis with empty recommendations"""
        metrics = SalesMetrics(
            rapport_building=MetricScore(value=50),
            needs_discovery=MetricScore(value=50),
            objection_handling=MetricScore(value=50),
            closing_effectiveness=MetricScore(value=50),
            active_listening=MetricScore(value=50),
            effective_questioning=MetricScore(value=50)
        )
        
        analysis = Analysis(
            analysis_id=AnalysisId(value="test"),
            conversation_id="conv",
            overall_score=MetricScore(value=50),
            metrics=metrics,
            strengths=[],
            weaknesses=[],
            recommendations=[],
            status=AnalysisStatus.COMPLETED,
            created_at=datetime.now()
        )
        
        assert len(analysis.strengths) == 0
        assert len(analysis.weaknesses) == 0
        assert len(analysis.recommendations) == 0
    
    def test_multiple_recommendations(self):
        """Test analysis with multiple recommendations"""
        metrics = SalesMetrics(
            rapport_building=MetricScore(value=60),
            needs_discovery=MetricScore(value=60),
            objection_handling=MetricScore(value=60),
            closing_effectiveness=MetricScore(value=60),
            active_listening=MetricScore(value=60),
            effective_questioning=MetricScore(value=60)
        )
        
        recommendations = [
            Recommendation(value="Rec 1"),
            Recommendation(value="Rec 2"),
            Recommendation(value="Rec 3")
        ]
        
        analysis = Analysis(
            analysis_id=AnalysisId(value="test"),
            conversation_id="conv",
            overall_score=MetricScore(value=60),
            metrics=metrics,
            strengths=[],
            weaknesses=[],
            recommendations=recommendations,
            status=AnalysisStatus.COMPLETED,
            created_at=datetime.now()
        )
        
        assert len(analysis.recommendations) == 3

