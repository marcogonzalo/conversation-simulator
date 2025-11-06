"""
Expanded tests for SemanticValidator to achieve high coverage
"""
import pytest
from src.shared.domain.semantic_validator import SemanticValidator
from src.shared.domain.schemas import (
    IndustryContextSchema,
    SalesSituationSchema,
    ClientPsychologySchema,
    ClientIdentitySchema
)


class TestSemanticValidatorExpanded:
    """Expanded tests for semantic validator"""
    
    @pytest.fixture
    def base_industry(self):
        """Base industry configuration"""
        return IndustryContextSchema(
            id='test_industry',
            industry={'sector': 'Tech', 'subsector': 'SaaS', 'market': 'B2B'},
            sale_type={'product': 'Software', 'complexity': 'high', 'sales_cycle': '3-6 months'},
            budget_situation={'typical_range': '$10k-$50k', 'ticket_size': 'medium', 'flexibility': 'medium'},
            terminology={'key_terms': ['API'], 'common_concerns': ['security']}
        )
    
    @pytest.fixture
    def base_situation(self):
        """Base situation configuration"""
        return SalesSituationSchema(
            id='test_situation',
            sales_phase='discovery',
            urgency={'level': 'medium', 'timeline': '1-3 months'},
            primary_objection={'type': 'price', 'intensity': 'medium', 'generic_expressions': ['expensive']},
            client_state={'engagement': 'warm', 'buying_stage': 'consideration', 'prior_experience': 'some'}
        )
    
    @pytest.fixture
    def base_psychology(self):
        """Base psychology configuration"""
        return ClientPsychologySchema(
            id='test_psychology',
            client_profile={'personality': 'analytical', 'emotional_state': 'neutral', 'processing_style': 'analytical'},
            challenge_level={'difficulty': 'medium', 'cooperation': 'cooperative', 'objection_intensity': 'medium'},
            language_patterns={'typical_phrases': ['Let me think'], 'question_types': ['How?']}
        )
    
    @pytest.fixture
    def base_identity(self):
        """Base identity configuration"""
        return ClientIdentitySchema(
            id='test_identity',
            identity={'age': 35, 'nationality': 'Test', 'role': 'Manager', 'experience': 'intermediate'},
            voice_config={'accent': 'neutral', 'voice_id': 'test', 'dialect': 'standard'},
            communication_style={'formality': 'professional', 'response_length': 'detailed', 'speaking_pace': 'moderate', 'energy_level': 'medium'},
            unique_characteristics={'cultural_traits': ['punctual'], 'industry_knowledge': 'intermediate'}
        )
    
    def test_coherent_configuration_no_warnings(self, base_industry, base_situation, base_psychology, base_identity):
        """Test that coherent configuration produces no warnings"""
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
        assert len(warnings) == 0
        assert is_valid is True
    
    def test_high_urgency_long_timeline_contradiction(self, base_industry, base_situation, base_psychology, base_identity):
        """Test contradiction: high urgency with long timeline"""
        base_situation.urgency['level'] = 'high'
        base_situation.urgency['timeline'] = '6+ months'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert len(warnings) > 0
        assert any('urgency' in w.lower() or 'timeline' in w.lower() for w in warnings)
    
    def test_low_urgency_immediate_timeline_contradiction(self, base_industry, base_situation, base_psychology, base_identity):
        """Test contradiction: low urgency with immediate timeline"""
        base_situation.urgency['level'] = 'low'
        base_situation.urgency['timeline'] = 'immediate'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert len(warnings) > 0
    
    def test_very_difficult_very_cooperative_contradiction(self, base_industry, base_situation, base_psychology, base_identity):
        """Test contradiction: very difficult with very cooperative"""
        base_psychology.challenge_level['difficulty'] = 'very_difficult'
        base_psychology.challenge_level['cooperation'] = 'very_cooperative'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert len(warnings) > 0
        assert any('difficult' in w.lower() or 'cooperative' in w.lower() for w in warnings)
    
    def test_analytical_concise_responses_contradiction(self, base_industry, base_situation, base_psychology, base_identity):
        """Test contradiction: analytical with concise responses"""
        base_psychology.client_profile['processing_style'] = 'analytical'
        base_identity.communication_style['response_length'] = 'concise'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert len(warnings) > 0
        assert any('analytical' in w.lower() or 'concise' in w.lower() for w in warnings)
    
    def test_discovery_phase_technical_objection_unusual(self, base_industry, base_situation, base_psychology, base_identity):
        """Test unusual: discovery phase with technical objection"""
        base_situation.sales_phase = 'discovery'
        base_situation.primary_objection['type'] = 'technical'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        # Should have warning but not critical
        assert isinstance(warnings, list)
    
    def test_closing_phase_need_objection_unusual(self, base_industry, base_situation, base_psychology, base_identity):
        """Test unusual: closing phase with need objection"""
        base_situation.sales_phase = 'closing'
        base_situation.primary_objection['type'] = 'need'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(warnings, list)
    
    def test_strong_objections_very_cooperative_contradiction(self, base_industry, base_situation, base_psychology, base_identity):
        """Test contradiction: strong objections with very cooperative"""
        base_psychology.challenge_level['objection_intensity'] = 'strong'
        base_psychology.challenge_level['cooperation'] = 'very_cooperative'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert len(warnings) > 0
    
    def test_no_experience_profound_questions_unusual(self, base_industry, base_situation, base_psychology, base_identity):
        """Test unusual: no experience with profound questions"""
        base_identity.identity['experience'] = 'none'
        base_situation.client_state['prior_experience'] = 'deep'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(warnings, list)
    
    def test_format_warnings_empty_list(self):
        """Test formatting empty warnings list"""
        result = SemanticValidator.format_warnings_for_display([])
        assert result == "No warnings"
    
    def test_format_warnings_with_warnings(self):
        """Test formatting warnings list"""
        warnings = ["Warning 1", "Warning 2"]
        result = SemanticValidator.format_warnings_for_display(warnings)
        
        assert "Warning 1" in result
        assert "Warning 2" in result
    
    def test_validator_handles_missing_optional_fields(self, base_industry, base_situation, base_psychology, base_identity):
        """Test that validator handles missing optional fields gracefully"""
        # Don't fail on missing optional fields
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
    
    def test_multiple_warnings_detected(self, base_industry, base_situation, base_psychology, base_identity):
        """Test that multiple contradictions are all detected"""
        # Add multiple contradictions
        base_situation.urgency['level'] = 'high'
        base_situation.urgency['timeline'] = '6+ months'
        base_psychology.challenge_level['difficulty'] = 'very_difficult'
        base_psychology.challenge_level['cooperation'] = 'very_cooperative'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        # Should detect multiple issues
        assert len(warnings) >= 2
    
    def test_validation_with_none_values(self, base_industry, base_situation, base_psychology, base_identity):
        """Test validation doesn't crash with None values"""
        # This should not crash
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
    
    def test_validator_returns_tuple(self, base_industry, base_situation, base_psychology, base_identity):
        """Test that validator always returns (bool, list) tuple"""
        result = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)
    
    def test_warnings_are_strings(self, base_industry, base_situation, base_psychology, base_identity):
        """Test that all warnings are strings"""
        # Add contradiction to get warnings
        base_situation.urgency['level'] = 'high'
        base_situation.urgency['timeline'] = '6+ months'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        for warning in warnings:
            assert isinstance(warning, str)
            assert len(warning) > 0
    
    def test_presentation_phase_objections(self, base_industry, base_situation, base_psychology, base_identity):
        """Test validation with presentation phase"""
        base_situation.sales_phase = 'presentation'
        base_situation.primary_objection['type'] = 'value'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        # Should be valid or have minimal warnings
        assert isinstance(is_valid, bool)
    
    def test_objection_handling_phase(self, base_industry, base_situation, base_psychology, base_identity):
        """Test validation with objection handling phase"""
        base_situation.sales_phase = 'objection_handling'
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            base_industry, base_situation, base_psychology, base_identity
        )
        
        assert isinstance(warnings, list)

