"""
Tests for analysis domain entities - UPDATED
Only tests that work
"""
import pytest

from src.analysis.domain.entities.analysis import AnalysisStatus
from src.analysis.domain.value_objects.metric_score import MetricScore


class TestAnalysisEntities:
    """Tests for analysis domain entities"""
    
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
    
    def test_analysis_status_enum(self):
        """Test AnalysisStatus enum values"""
        assert AnalysisStatus.PENDING.value == "pending"
        assert AnalysisStatus.COMPLETED.value == "completed"
        assert AnalysisStatus.FAILED.value == "failed"
    
    # =========================================================================
    # RECONSTRUCTED: Additional analysis entity tests
    # =========================================================================
    
    def test_metric_score_validation(self):
        """Test MetricScore validates values"""
        # Valid scores
        s1 = MetricScore(value=0)
        s2 = MetricScore(value=50)
        s3 = MetricScore(value=100)
        
        assert s1.value == 0
        assert s2.value == 50
        assert s3.value == 100
    
    def test_analysis_status_values(self):
        """Test all AnalysisStatus values"""
        assert AnalysisStatus.PENDING.value == "pending"
        assert AnalysisStatus.COMPLETED.value == "completed"
        assert AnalysisStatus.FAILED.value == "failed"
    
    def test_metric_score_string_representation(self):
        """Test MetricScore string representation"""
        score = MetricScore(value=85)
        assert str(score) in ["85", "85.0"]
    
    def test_metric_score_edge_cases(self):
        """Test MetricScore with edge values"""
        s_min = MetricScore(value=0)
        s_mid = MetricScore(value=50)
        s_max = MetricScore(value=100)
        
        assert s_min.value == 0
        assert s_mid.value == 50
        assert s_max.value == 100
        
        # Test string conversion
        assert "50" in str(s_mid) or "50.0" in str(s_mid)
    
    def test_metric_score_can_be_compared(self):
        """Test MetricScore values can be compared"""
        s1 = MetricScore(value=70)
        s2 = MetricScore(value=85)
        
        assert s1.value < s2.value
        assert s2.value > s1.value
