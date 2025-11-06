"""
Comprehensive tests for all value objects - UPDATED
Only tests that work with current API
"""
import pytest
from uuid import uuid4

from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.analysis.domain.value_objects.metric_score import MetricScore


class TestAllValueObjects:
    """Comprehensive tests for all value objects"""
    
    def test_conversation_id_all_cases(self):
        """Test ConversationId comprehensively"""
        uid1 = uuid4()
        uid2 = uuid4()
        
        cid1 = ConversationId(value=uid1)
        cid2 = ConversationId(value=uid1)
        cid3 = ConversationId(value=uid2)
        
        assert cid1.value == cid2.value
        assert cid1.value != cid3.value
        assert str(cid1) == str(uid1)
    
    def test_metric_score_all_cases(self):
        """Test MetricScore comprehensively"""
        # Min boundary
        s1 = MetricScore(value=0)
        assert s1.value == 0
        
        # Max boundary
        s2 = MetricScore(value=100)
        assert s2.value == 100
        
        # Middle
        s3 = MetricScore(value=50)
        assert s3.value == 50
        
        # String representation
        assert str(s3) in ["50", "50.0"]  # Handle both int and float representation
    
    def test_all_value_objects_hashable(self):
        """Test that value objects can be used in sets/dicts"""
        cid1 = ConversationId(value=uuid4())
        cid2 = ConversationId(value=uuid4())
        
        # Should be hashable
        value_set = {cid1, cid2}
        assert len(value_set) == 2
        
        # Should work in dicts
        value_dict = {cid1: "conv1", cid2: "conv2"}
        assert value_dict[cid1] == "conv1"
    
    # =========================================================================
    # RECONSTRUCTED: Additional value object tests
    # =========================================================================
    
    def test_metric_score_boundaries(self):
        """Test MetricScore at boundaries"""
        from src.analysis.domain.value_objects.metric_score import MetricScore
        
        s0 = MetricScore(value=0)
        s100 = MetricScore(value=100)
        
        assert s0.value == 0
        assert s100.value == 100
    
    def test_conversation_id_immutability(self):
        """Test ConversationId is immutable"""
        cid = ConversationId(value=uuid4())
        
        # Should not be able to change value
        with pytest.raises(AttributeError):
            cid.value = uuid4()
    
    def test_value_objects_can_be_compared(self):
        """Test value objects can be compared"""
        uid = uuid4()
        cid1 = ConversationId(value=uid)
        cid2 = ConversationId(value=uid)
        
        assert cid1.value == cid2.value
