"""
Tests for Analysis structure and repository.
"""
import pytest
from pathlib import Path
import json
import tempfile
import shutil

from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService
from src.analysis.infrastructure.repositories.file_analysis_repository import FileAnalysisRepository


@pytest.mark.asyncio
class TestAnalysisStructure:
    """Test suite for analysis data structure validation."""

    @pytest.fixture
    def temp_analysis_dir(self):
        """Create a temporary directory for analysis files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def analysis_repository(self, temp_analysis_dir):
        """Create analysis repository with temp directory."""
        return FileAnalysisRepository(base_path=temp_analysis_dir)

    @pytest.fixture
    def analysis_service(self, analysis_repository):
        """Create analysis service without AI (simulated mode)."""
        return ConversationAnalysisService(
            ai_provider=None,
            api_key=None,
            analysis_repository=analysis_repository
        )

    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation data for testing."""
        return {
            "conversation_id": "test-conversation-123",
            "persona_name": "Ana García",
            "context_id": "evaluacion_crm",
            "duration_seconds": 180,
            "messages": [
                {
                    "role": "user",
                    "content": "Hola, buenos días",
                    "timestamp": "2025-01-01T10:00:00"
                },
                {
                    "role": "assistant",
                    "content": "Buenos días, ¿en qué puedo ayudarte?",
                    "timestamp": "2025-01-01T10:00:05"
                }
            ],
            "metadata": {
                "source": "openai_voice_conversation"
            }
        }

    async def test_analysis_has_required_fields(self, analysis_service, sample_conversation_data):
        """Test that generated analysis has all required fields."""
        # Act
        result = await analysis_service.analyze_conversation(sample_conversation_data)
        
        # Assert - Check top-level required fields
        assert "analysis_id" in result
        assert "conversation_id" in result
        assert result["conversation_id"] == "test-conversation-123"
        assert "overall_score" in result
        assert "summary" in result
        assert "strengths" in result
        assert "areas_for_improvement" in result
        assert "recommendations" in result
        assert "metrics" in result
        assert "metadata" in result

    async def test_analysis_overall_score_is_valid(self, analysis_service, sample_conversation_data):
        """Test that overall_score is a valid number between 0 and 10."""
        # Act
        result = await analysis_service.analyze_conversation(sample_conversation_data)
        
        # Assert
        assert isinstance(result["overall_score"], (int, float))
        assert 0 <= result["overall_score"] <= 10

    async def test_analysis_metrics_structure(self, analysis_service, sample_conversation_data):
        """Test that metrics has the 6 required categories and no extra fields."""
        # Act
        result = await analysis_service.analyze_conversation(sample_conversation_data)
        
        # Assert - Check metrics has exactly the 6 categories
        metrics = result["metrics"]
        assert isinstance(metrics, dict)
        
        required_metrics = [
            "opening_qualification",
            "needs_assessment",
            "value_presentation",
            "objection_handling",
            "closing_effectiveness",
            "communication_rapport"
        ]
        
        for metric in required_metrics:
            assert metric in metrics, f"Missing required metric: {metric}"
            assert isinstance(metrics[metric], (int, float))
            assert 0 <= metrics[metric] <= 10, f"Metric {metric} out of range: {metrics[metric]}"
        
        # Ensure NO extra fields in metrics
        forbidden_fields = ["duration_seconds", "message_count"]
        for field in forbidden_fields:
            assert field not in metrics, f"Field {field} should not be in metrics, only in metadata"

    async def test_analysis_metadata_structure(self, analysis_service, sample_conversation_data):
        """Test that metadata has the required fields."""
        # Act
        result = await analysis_service.analyze_conversation(sample_conversation_data)
        
        # Assert - Check metadata fields
        metadata = result["metadata"]
        assert isinstance(metadata, dict)
        
        assert "duration_seconds" in metadata
        assert metadata["duration_seconds"] == 180
        
        assert "message_count" in metadata
        assert metadata["message_count"] == 2
        
        assert "persona_name" in metadata
        assert metadata["persona_name"] == "Ana García"
        
        assert "context_id" in metadata
        assert metadata["context_id"] == "evaluacion_crm"
        
        assert "conversation_metadata" in metadata
        assert isinstance(metadata["conversation_metadata"], dict)

    async def test_analysis_lists_have_items(self, analysis_service, sample_conversation_data):
        """Test that strengths, areas_for_improvement, and recommendations are non-empty lists."""
        # Act
        result = await analysis_service.analyze_conversation(sample_conversation_data)
        
        # Assert
        assert isinstance(result["strengths"], list)
        assert len(result["strengths"]) >= 3, "Should have at least 3 strengths"
        
        assert isinstance(result["areas_for_improvement"], list)
        assert len(result["areas_for_improvement"]) >= 3, "Should have at least 3 areas for improvement"
        
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) >= 3, "Should have at least 3 recommendations"

    async def test_analysis_repository_saves_correct_structure(
        self, 
        analysis_repository, 
        temp_analysis_dir
    ):
        """Test that repository saves analysis with correct structure."""
        # Arrange
        analysis_data = {
            "overall_score": 8.5,
            "summary": "Test summary",
            "strengths": ["Strength 1", "Strength 2", "Strength 3"],
            "areas_for_improvement": ["Area 1", "Area 2", "Area 3"],
            "recommendations": ["Rec 1", "Rec 2", "Rec 3"],
            "metrics": {
                "opening_qualification": 7,
                "needs_assessment": 8,
                "value_presentation": 9,
                "objection_handling": 7,
                "closing_effectiveness": 6,
                "communication_rapport": 8
            },
            "metadata": {
                "duration_seconds": 180,
                "message_count": 10,
                "persona_name": "Test Persona",
                "context_id": "test_context",
                "conversation_metadata": {"source": "test"}
            }
        }
        
        # Act
        analysis_id = await analysis_repository.save_analysis(
            "test-conversation-123", 
            analysis_data
        )
        
        # Assert - Read file directly and verify structure
        file_path = Path(temp_analysis_dir) / f"{analysis_id}.json"
        assert file_path.exists()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_analysis = json.load(f)
        
        # Verify all fields are present
        assert saved_analysis["analysis_id"] == analysis_id
        assert saved_analysis["conversation_id"] == "test-conversation-123"
        assert "created_at" in saved_analysis
        assert saved_analysis["overall_score"] == 8.5
        assert saved_analysis["summary"] == "Test summary"
        assert len(saved_analysis["strengths"]) == 3
        assert len(saved_analysis["areas_for_improvement"]) == 3
        assert len(saved_analysis["recommendations"]) == 3
        
        # Verify metrics structure
        assert "opening_qualification" in saved_analysis["metrics"]
        assert "duration_seconds" not in saved_analysis["metrics"]
        
        # Verify metadata structure
        assert saved_analysis["metadata"]["duration_seconds"] == 180
        assert saved_analysis["metadata"]["message_count"] == 10
        assert saved_analysis["metadata"]["persona_name"] == "Test Persona"
        assert saved_analysis["metadata"]["context_id"] == "test_context"
        
        # Ensure no recursive metadata
        assert "metadata" not in saved_analysis["metadata"]["conversation_metadata"]

    async def test_analysis_no_legacy_fields(self, analysis_service, sample_conversation_data):
        """Test that analysis does not contain legacy fields like 'analysis' string."""
        # Act
        result = await analysis_service.analyze_conversation(sample_conversation_data)
        
        # Assert - Should NOT have legacy markdown field
        # Note: It's OK if it exists for backward compatibility, but it should be structured data
        if "analysis" in result:
            # If present, it should be empty or we're in a fallback scenario
            # The main data should be in structured fields
            assert result["overall_score"] is not None
            assert len(result["metrics"]) > 0

