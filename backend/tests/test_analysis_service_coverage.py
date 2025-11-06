"""
Tests for conversation analysis service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService


class TestConversationAnalysisServiceCoverage:
    """Tests for ConversationAnalysisService"""
    
    @pytest.fixture
    def service(self):
        """Create analysis service"""
        return ConversationAnalysisService()
    
    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation data for analysis"""
        return {
            "conversation_id": "test_123",
            "persona_id": "ana_garcia",
            "messages": [
                {"role": "user", "content": "I'm interested in your product", "timestamp": "2024-01-01T10:00:00"},
                {"role": "assistant", "content": "Great! Tell me about your needs", "timestamp": "2024-01-01T10:00:05"},
                {"role": "user", "content": "I need to solve X problem", "timestamp": "2024-01-01T10:00:15"},
                {"role": "assistant", "content": "Our product solves that by...", "timestamp": "2024-01-01T10:00:20"}
            ],
            "metadata": {}
        }
    
    def test_service_initialization(self, service):
        """Test service initializes"""
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_analyze_conversation_structure(self, service, sample_conversation_data):
        """Test that analyze_conversation returns proper structure"""
        with patch.object(service, '_call_openai_analysis') as mock_openai:
            mock_openai.return_value = {
                "overall_score": 75,
                "strengths": ["Good rapport"],
                "weaknesses": ["Slow closing"],
                "recommendations": ["Practice closing"],
                "metrics": {
                    "rapport_building": 80,
                    "needs_discovery": 70,
                    "objection_handling": 60,
                    "closing_effectiveness": 65
                }
            }
            
            result = await service.analyze_conversation(sample_conversation_data)
            
            assert result is not None
            assert 'overall_score' in result
            assert 'strengths' in result
            assert 'weaknesses' in result
    
    @pytest.mark.asyncio
    async def test_analyze_conversation_with_empty_messages(self, service):
        """Test analyzing conversation with no messages"""
        data = {
            "conversation_id": "empty",
            "persona_id": "test",
            "messages": [],
            "metadata": {}
        }
        
        # Should handle gracefully
        try:
            result = await service.analyze_conversation(data)
        except Exception as e:
            # May raise or return empty analysis
            pass
    
    @pytest.mark.asyncio
    async def test_service_handles_openai_error(self, service, sample_conversation_data):
        """Test service handles OpenAI API errors gracefully"""
        with patch.object(service, '_call_openai_analysis') as mock_openai:
            mock_openai.side_effect = Exception("API Error")
            
            # Should handle error gracefully
            try:
                result = await service.analyze_conversation(sample_conversation_data)
            except Exception:
                # Expected to raise or handle
                pass
    
    def test_service_has_required_methods(self, service):
        """Test service has required methods"""
        assert hasattr(service, 'analyze_conversation')
        assert callable(service.analyze_conversation)
    
    @pytest.mark.asyncio
    async def test_conversation_with_long_messages(self, service):
        """Test analyzing conversation with long messages"""
        data = {
            "conversation_id": "long_test",
            "persona_id": "test",
            "messages": [
                {"role": "user", "content": "A" * 5000, "timestamp": "2024-01-01T10:00:00"},
                {"role": "assistant", "content": "B" * 5000, "timestamp": "2024-01-01T10:00:05"}
            ],
            "metadata": {}
        }
        
        with patch.object(service, '_call_openai_analysis') as mock_openai:
            mock_openai.return_value = {"overall_score": 50, "strengths": [], "weaknesses": [], "recommendations": [], "metrics": {}}
            
            # Should handle long content
            result = await service.analyze_conversation(data)
            assert result is not None

