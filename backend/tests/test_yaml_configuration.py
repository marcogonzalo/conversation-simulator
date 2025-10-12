"""
Test YAML configuration integration for analysis service.
"""
import pytest
import yaml
from pathlib import Path
from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService


class TestYAMLConfiguration:
    """Test that analysis service uses YAML configuration correctly."""
    
    @pytest.fixture
    def analysis_service(self):
        """Create analysis service instance."""
        return ConversationAnalysisService()
    
    def test_load_analysis_prompts(self, analysis_service):
        """Test that analysis prompts are loaded from YAML."""
        prompts = analysis_service._load_analysis_prompts()
        
        # Check main sections exist
        assert 'conversation_analysis' in prompts
        assert 'evaluation_criteria' in prompts
        assert 'response_format' in prompts
        
        # Check response format structure
        response_format = prompts['response_format']
        assert response_format['type'] == 'json'
        assert 'template' in response_format
        assert 'instructions' in response_format
        assert 'structure' in response_format
    
    def test_response_format_structure(self, analysis_service):
        """Test that response format has correct structure."""
        prompts = analysis_service._load_analysis_prompts()
        response_format = prompts['response_format']
        structure = response_format['structure']
        
        # Check required fields
        required_fields = [
            'overall_score', 'summary', 'strengths', 
            'areas_for_improvement', 'recommendations', 'metrics'
        ]
        
        for field in required_fields:
            assert field in structure, f"Missing field: {field}"
        
        # Check metrics structure
        metrics = structure['metrics']['properties']
        required_metrics = [
            'opening_qualification', 'needs_assessment', 'value_presentation',
            'objection_handling', 'closing_effectiveness', 'communication_rapport'
        ]
        
        for metric in required_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
            assert metrics[metric]['type'] == 'number'
            assert metrics[metric]['range'] == '0-10'
    
    def test_template_format(self, analysis_service):
        """Test that template contains correct JSON structure."""
        prompts = analysis_service._load_analysis_prompts()
        template = prompts['response_format']['template']
        
        # Check template contains required fields
        required_fields = [
            'overall_score', 'summary', 'strengths',
            'areas_for_improvement', 'recommendations', 'metrics'
        ]
        
        for field in required_fields:
            assert field in template, f"Template missing field: {field}"
        
        # Check metrics in template
        required_metrics = [
            'opening_qualification', 'needs_assessment', 'value_presentation',
            'objection_handling', 'closing_effectiveness', 'communication_rapport'
        ]
        
        for metric in required_metrics:
            assert metric in template, f"Template missing metric: {metric}"
    
    def test_prompt_building_uses_yaml(self, analysis_service):
        """Test that prompt building uses YAML configuration."""
        prompts = analysis_service._load_analysis_prompts()
        test_context = "Test conversation context"
        
        prompt = analysis_service._build_analysis_prompt(prompts, test_context)
        
        # Check that prompt contains YAML content
        assert "INSTRUCCIONES PARA ANÁLISIS" in prompt
        assert "CRITERIOS DE EVALUACIÓN" in prompt
        assert "FORMATO DE RESPUESTA REQUERIDO" in prompt
        assert "overall_score" in prompt
        assert "closing_effectiveness" in prompt  # Updated metric name
        assert "Responde ÚNICAMENTE con el JSON" in prompt
        assert test_context in prompt
    
    def test_evaluation_criteria_loaded(self, analysis_service):
        """Test that evaluation criteria are loaded from YAML."""
        prompts = analysis_service._load_analysis_prompts()
        criteria = prompts['evaluation_criteria']
        
        # Check that all criteria exist
        required_criteria = [
            'opening_qualification', 'needs_assessment', 'value_presentation',
            'objection_handling', 'closing_effectiveness', 'communication_rapport'
        ]
        
        for criterion in required_criteria:
            assert criterion in criteria, f"Missing criterion: {criterion}"
            assert 'name' in criteria[criterion]
            assert 'weight' in criteria[criterion]
            assert 'aspects' in criteria[criterion]
    
    def test_closing_effectiveness_naming(self, analysis_service):
        """Test that closing metric uses correct name."""
        prompts = analysis_service._load_analysis_prompts()
        criteria = prompts['evaluation_criteria']
        
        # Check that closing criterion is named correctly
        assert 'closing_effectiveness' in criteria
        assert criteria['closing_effectiveness']['name'] == 'Efectividad de Cierre'
        
        # Check that old name doesn't exist
        assert 'closing_next_steps' not in criteria
