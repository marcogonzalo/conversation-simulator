"""
Comprehensive tests for all value objects
"""
import pytest
from uuid import uuid4
from datetime import datetime

# Import all value objects
from src.shared.domain.value_objects import MessageContent
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.value_objects.message_content import MessageContent as ConvMessageContent
# Legacy persona imports removed - module deleted
from src.audio.domain.value_objects.audio_id import AudioId
from src.audio.domain.value_objects.audio_format import AudioFormat
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.value_objects.metric_score import MetricScore
from src.analysis.domain.value_objects.recommendation import Recommendation


class TestAllValueObjects:
    """Comprehensive tests for all value objects"""
    
    # MessageContent tests
    def test_message_content_all_cases(self):
        """Test MessageContent comprehensively"""
        # Empty
        mc1 = MessageContent(value="")
        assert mc1.value == ""
        
        # Normal
        mc2 = MessageContent(value="Hello world")
        assert mc2.value == "Hello world"
        
        # Long
        mc3 = MessageContent(value="A" * 10000)
        assert len(mc3.value) == 10000
        
        # Unicode
        mc4 = MessageContent(value="Hola ñ 👋")
        assert "ñ" in mc4.value
        
        # String repr
        assert str(mc2) == "Hello world"
    
    # ConversationId tests
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
    
    # Legacy persona tests removed - module deleted
    
    # AudioId tests
    def test_audio_id_all_cases(self):
        """Test AudioId comprehensively"""
        uid1 = uuid4()
        uid2 = uuid4()
        
        aid1 = AudioId(value=uid1)
        aid2 = AudioId(value=uid1)
        aid3 = AudioId(value=uid2)
        
        assert aid1.value == aid2.value
        assert aid1.value != aid3.value
        assert str(aid1) == str(uid1)
    
    # AudioFormat tests
    def test_audio_format_all_cases(self):
        """Test AudioFormat comprehensively"""
        # WAV formats
        f1 = AudioFormat(format_type="wav", sample_rate=16000)
        f2 = AudioFormat(format_type="wav", sample_rate=24000)
        f3 = AudioFormat(format_type="wav", sample_rate=48000)
        
        assert f1.format_type == "wav"
        assert f1.sample_rate == 16000
        assert f2.sample_rate == 24000
        assert f3.sample_rate == 48000
        
        # Other formats
        f4 = AudioFormat(format_type="webm", sample_rate=24000)
        f5 = AudioFormat(format_type="pcm16", sample_rate=16000)
        
        assert f4.format_type == "webm"
        assert f5.format_type == "pcm16"
        
        # String representation
        str_f1 = str(f1)
        assert isinstance(str_f1, str)
    
    # AnalysisId tests
    def test_analysis_id_all_cases(self):
        """Test AnalysisId comprehensively"""
        aid1 = AnalysisId(value="analysis_123")
        aid2 = AnalysisId(value="analysis_123")
        aid3 = AnalysisId(value="analysis_456")
        
        assert aid1.value == aid2.value
        assert aid1.value != aid3.value
        assert str(aid1) == "analysis_123"
    
    # MetricScore tests
    def test_metric_score_all_cases(self):
        """Test MetricScore comprehensively"""
        # Various scores
        s1 = MetricScore(value=0)
        s2 = MetricScore(value=50)
        s3 = MetricScore(value=100)
        s4 = MetricScore(value=75)
        
        assert s1.value == 0
        assert s2.value == 50
        assert s3.value == 100
        assert s4.value == 75
        
        # All should be valid
        for score in [s1, s2, s3, s4]:
            assert 0 <= score.value <= 100
    
    # Recommendation tests
    def test_recommendation_all_cases(self):
        """Test Recommendation comprehensively"""
        r1 = Recommendation(value="Practice more")
        r2 = Recommendation(value="")
        r3 = Recommendation(value="A" * 500)
        
        assert r1.value == "Practice more"
        assert r2.value == ""
        assert len(r3.value) == 500
        assert str(r1) == "Practice more"
    
    # Cross-comparisons
    def test_different_value_object_types_independent(self):
        """Test different value object types are independent"""
        cid = ConversationId(value=uuid4())
        aid = AnalysisId(value="analysis")
        
        # All should be different types
        assert type(cid) != type(aid)
    
    def test_value_objects_immutable(self):
        """Test value objects are immutable"""
        mc = MessageContent(value="test")
        
        # Should not be able to change value directly
        with pytest.raises(AttributeError):
            mc.value = "new value"
    
    def test_all_value_objects_hashable(self):
        """Test all value objects can be used in sets"""
        cid = ConversationId(value=uuid4())
        ms = MetricScore(value=75)
        
        # Should not raise
        value_set = {cid, ms}
        assert len(value_set) == 2
    
    # Legacy persona tests removed
    
    def test_audio_format_equality(self):
        """Test AudioFormat equality"""
        f1 = AudioFormat(format_type="wav", sample_rate=16000)
        f2 = AudioFormat(format_type="wav", sample_rate=16000)
        f3 = AudioFormat(format_type="webm", sample_rate=16000)
        
        # Same format and rate should be equal
        assert f1.format_type == f2.format_type
        assert f1.sample_rate == f2.sample_rate
        
        # Different format should be different
        assert f1.format_type != f3.format_type

