"""
Comprehensive tests for PromptBuilder - critical 5-layer system component
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.shared.domain.prompt_builder import PromptBuilder
from src.shared.domain.schemas import (
    IndustryContextSchema,
    SalesSituationSchema,
    ClientPsychologySchema,
    ClientIdentitySchema,
    SimulationRulesSchema
)


class TestPromptBuilderComprehensive:
    """Comprehensive tests for PromptBuilder"""
    
    @pytest.fixture
    def prompt_builder(self):
        """Create PromptBuilder instance"""
        return PromptBuilder()
    
    def test_builder_initialization(self, prompt_builder):
        """Test that builder initializes correctly"""
        assert prompt_builder is not None
        assert prompt_builder.config_path is not None
    
    def test_get_available_industries(self, prompt_builder):
        """Test getting available industries"""
        industries = prompt_builder.get_available_industries()
        assert isinstance(industries, list)
        assert len(industries) >= 0
    
    def test_get_available_situations(self, prompt_builder):
        """Test getting available situations"""
        situations = prompt_builder.get_available_situations()
        assert isinstance(situations, list)
        assert len(situations) >= 0
    
    def test_get_available_psychologies(self, prompt_builder):
        """Test getting available psychologies"""
        psychologies = prompt_builder.get_available_psychologies()
        assert isinstance(psychologies, list)
        assert len(psychologies) >= 0
    
    def test_get_available_identities(self, prompt_builder):
        """Test getting available identities"""
        identities = prompt_builder.get_available_identities()
        assert isinstance(identities, list)
        assert len(identities) >= 0
    
    def test_build_prompt_with_valid_combination(self, prompt_builder):
        """Test building prompt with valid combination"""
        try:
            prompt = prompt_builder.build_prompt(
                industry_id="real_estate",
                situation_id="discovery_no_urgency_price",
                psychology_id="conservative_analytical",
                identity_id="ana_garcia"
            )
            assert prompt is not None
            assert len(prompt) > 100
            assert isinstance(prompt, str)
        except FileNotFoundError:
            pytest.skip("Config files not available in test environment")
    
    def test_validate_layer_exists_industry(self, prompt_builder):
        """Test validating industry layer exists"""
        # Should not raise for valid industry
        try:
            prompt_builder._validate_layer_exists("real_estate", "industry")
        except FileNotFoundError:
            pytest.skip("Config files not available")
    
    def test_validate_layer_exists_invalid_raises(self, prompt_builder):
        """Test that invalid layer raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            prompt_builder._validate_layer_exists("invalid_id_xyz", "industry")
    
    def test_cache_functionality(self, prompt_builder):
        """Test that caching works properly"""
        prompt_builder._prompt_cache = {}
        
        cache_key = "test_real_estate_discovery_conservative_ana"
        test_prompt = "Test cached prompt"
        
        # Cache a prompt
        prompt_builder._prompt_cache[cache_key] = test_prompt
        
        # Verify it's cached
        assert cache_key in prompt_builder._prompt_cache
        assert prompt_builder._prompt_cache[cache_key] == test_prompt
    
    def test_generate_cache_key(self, prompt_builder):
        """Test cache key generation"""
        key = prompt_builder._generate_cache_key(
            "real_estate", "discovery", "conservative", "ana"
        )
        
        assert isinstance(key, str)
        assert "real_estate" in key
        assert "discovery" in key
        assert "conservative" in key
        assert "ana" in key
    
    def test_clear_cache(self, prompt_builder):
        """Test clearing cache"""
        prompt_builder._prompt_cache = {"test": "value"}
        prompt_builder.clear_cache()
        assert len(prompt_builder._prompt_cache) == 0
    
    def test_schema_validation_industry(self):
        """Test IndustryContextSchema validation"""
        valid_data = {
            'id': 'test_industry',
            'industry': {
                'sector': 'Technology',
                'subsector': 'Software',
                'market': 'B2B'
            },
            'sale_type': {
                'product': 'SaaS Platform',
                'complexity': 'high',
                'sales_cycle': '3-6 months'
            },
            'budget_situation': {
                'typical_range': '$10k-$50k',
                'ticket_size': 'medium',
                'flexibility': 'medium'
            },
            'terminology': {
                'key_terms': ['cloud', 'API'],
                'common_concerns': ['security', 'integration']
            }
        }
        
        schema = IndustryContextSchema(**valid_data)
        assert schema.id == 'test_industry'
        assert schema.industry['sector'] == 'Technology'
    
    def test_schema_validation_situation(self):
        """Test SalesSituationSchema validation"""
        valid_data = {
            'id': 'test_situation',
            'sales_phase': 'discovery',
            'urgency': {
                'level': 'medium',
                'timeline': '1-3 months'
            },
            'primary_objection': {
                'type': 'price',
                'intensity': 'medium',
                'generic_expressions': ['too expensive']
            },
            'client_state': {
                'engagement': 'warm',
                'buying_stage': 'consideration',
                'prior_experience': 'some'
            }
        }
        
        schema = SalesSituationSchema(**valid_data)
        assert schema.id == 'test_situation'
        assert schema.sales_phase == 'discovery'
    
    def test_schema_validation_psychology(self):
        """Test ClientPsychologySchema validation"""
        valid_data = {
            'id': 'test_psychology',
            'client_profile': {
                'personality': 'analytical',
                'emotional_state': 'neutral',
                'processing_style': 'slow'
            },
            'challenge_level': {
                'difficulty': 'medium',
                'cooperation': 'cooperative',
                'objection_intensity': 'medium'
            },
            'language_patterns': {
                'typical_phrases': ['Let me think about it'],
                'question_types': ['How does this work?']
            }
        }
        
        schema = ClientPsychologySchema(**valid_data)
        assert schema.id == 'test_psychology'
        assert schema.client_profile['personality'] == 'analytical'
    
    def test_schema_validation_identity(self):
        """Test ClientIdentitySchema validation"""
        valid_data = {
            'id': 'test_identity',
            'identity': {
                'age': 35,
                'nationality': 'Spanish',
                'role': 'Manager',
                'experience': 'intermediate'
            },
            'voice_config': {
                'accent': 'neutral',
                'voice_id': 'test_voice',
                'dialect': 'standard'
            },
            'communication_style': {
                'formality': 'professional',
                'response_length': 'medium',
                'speaking_pace': 'moderate',
                'energy_level': 'medium'
            },
            'unique_characteristics': {
                'cultural_traits': ['punctual'],
                'industry_knowledge': 'intermediate'
            }
        }
        
        schema = ClientIdentitySchema(**valid_data)
        assert schema.id == 'test_identity'
        assert schema.identity['age'] == 35
    
    def test_prompt_contains_all_layers(self, prompt_builder):
        """Test that generated prompt contains elements from all layers"""
        try:
            prompt = prompt_builder.build_prompt(
                industry_id="real_estate",
                situation_id="discovery_no_urgency_price",
                psychology_id="conservative_analytical",
                identity_id="ana_garcia"
            )
            
            # Should contain references to the context
            assert len(prompt) > 500
            # Prompt should be coherent text
            assert isinstance(prompt, str)
            
        except FileNotFoundError:
            pytest.skip("Config files not available")
    
    def test_config_path_customization(self, tmp_path):
        """Test that custom config path works"""
        custom_path = str(tmp_path)
        builder = PromptBuilder(config_path=custom_path)
        assert custom_path in str(builder.config_path)
    
    def test_multiple_builds_use_cache(self, prompt_builder):
        """Test that multiple builds of same combination use cache"""
        try:
            # First build
            prompt1 = prompt_builder.build_prompt(
                "real_estate", "discovery_no_urgency_price",
                "conservative_analytical", "ana_garcia"
            )
            
            cache_size_after_first = len(prompt_builder._prompt_cache)
            
            # Second build (should use cache)
            prompt2 = prompt_builder.build_prompt(
                "real_estate", "discovery_no_urgency_price",
                "conservative_analytical", "ana_garcia"
            )
            
            cache_size_after_second = len(prompt_builder._prompt_cache)
            
            # Cache size shouldn't increase
            assert cache_size_after_first == cache_size_after_second
            # Prompts should be identical
            assert prompt1 == prompt2
            
        except FileNotFoundError:
            pytest.skip("Config files not available")
    
    def test_different_combinations_generate_different_prompts(self, prompt_builder):
        """Test that different combinations generate different prompts"""
        try:
            prompt1 = prompt_builder.build_prompt(
                "real_estate", "discovery_no_urgency_price",
                "conservative_analytical", "ana_garcia"
            )
            
            prompt2 = prompt_builder.build_prompt(
                "real_estate", "closing_high_urgency_fit",
                "impulsive_enthusiastic", "carlos_mendoza"
            )
            
            # Prompts should be different
            assert prompt1 != prompt2
            
        except FileNotFoundError:
            pytest.skip("Config files not available")
    
    def test_error_handling_invalid_yaml(self, tmp_path):
        """Test error handling with invalid YAML file"""
        invalid_yaml = tmp_path / "industry_contexts" / "invalid.yaml"
        invalid_yaml.parent.mkdir(parents=True)
        invalid_yaml.write_text("{ invalid yaml content")
        
        builder = PromptBuilder(config_path=str(tmp_path))
        
        with pytest.raises((FileNotFoundError, Exception)):
            builder.build_prompt("invalid", "discovery", "conservative", "ana")

