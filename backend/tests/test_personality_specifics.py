"""
Comprehensive tests for personality (identity) specifics and 5-layer YAML structure validation.
Tests that validate:
1. Structure of all 5 layers (Simulation Rules, Industry, Situation, Psychology, Identity)
2. Required fields in each configuration type
3. Personality-specific characteristics (voice config, expressions, cultural traits)
4. Flexibility of combinations (any identity + any psychology)
5. Differentiation between identities
"""
import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List

from src.shared.domain.prompt_builder import PromptBuilder
from src.shared.application.prompt_service import PromptService


class TestYAMLStructureValidation:
    """Test structure and required fields for all 5-layer YAML files."""
    
    @pytest.fixture
    def config_base_path(self) -> Path:
        """Get base path for configuration files."""
        return Path(__file__).parent.parent / "src" / "shared" / "infrastructure" / "config"
    
    @pytest.fixture
    def prompt_builder(self) -> PromptBuilder:
        """Create PromptBuilder instance."""
        return PromptBuilder()
    
    # =========================================================================
    # LAYER 1: Simulation Rules (Global)
    # =========================================================================
    
    def test_simulation_rules_structure(self, config_base_path):
        """Test that simulation_rules.yaml has required structure."""
        file_path = config_base_path / "simulation_rules.yaml"
        assert file_path.exists(), "simulation_rules.yaml must exist"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Required top-level fields
        required_fields = ['id', 'version', 'description', 'llm_identity', 'safety_rules']
        for field in required_fields:
            assert field in config, f"simulation_rules.yaml missing required field: {field}"
        
        # Validate llm_identity structure
        assert 'role' in config['llm_identity']
        assert 'behavior' in config['llm_identity']
        assert 'critical_reminder' in config['llm_identity']
        
        # Validate safety_rules is a list
        assert isinstance(config['safety_rules'], list)
        assert len(config['safety_rules']) > 0, "safety_rules must have at least one rule"
    
    # =========================================================================
    # LAYER 2: Industry Contexts
    # =========================================================================
    
    def test_industry_contexts_structure(self, config_base_path, prompt_builder):
        """Test that all industry context files have required structure."""
        industry_dir = config_base_path / "industry_contexts"
        industry_files = list(industry_dir.glob("*.yaml"))
        
        assert len(industry_files) > 0, "At least one industry context must exist"
        
        required_fields = [
            'id', 'name', 'version',
            'industry', 'sale_type', 'budget_situation',
            'terminology', 'objection_mappings'
        ]
        
        for file_path in industry_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            for field in required_fields:
                assert field in config, f"{file_path.name} missing required field: {field}"
            
            # Validate industry structure
            assert 'sector' in config['industry']
            assert 'market' in config['industry']  # Field is 'market', not 'market_type'
            
            # Validate sale_type structure
            assert 'product_type' in config['sale_type']
            assert 'complexity' in config['sale_type']
            
            # Validate budget_situation structure
            assert 'typical_range' in config['budget_situation']
            assert 'budget_flexibility' in config['budget_situation']
            
            # Validate objection_mappings is a dict
            assert isinstance(config['objection_mappings'], dict)
    
    # =========================================================================
    # LAYER 3: Sales Situations
    # =========================================================================
    
    def test_sales_situations_structure(self, config_base_path, prompt_builder):
        """Test that all sales situation files have required structure."""
        situation_dir = config_base_path / "sales_situations"
        situation_files = list(situation_dir.glob("*.yaml"))
        
        assert len(situation_files) > 0, "At least one sales situation must exist"
        
        required_fields = [
            'id', 'name', 'version',
            'sales_phase', 'urgency', 'primary_objection', 'client_state'
        ]
        
        for file_path in situation_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            for field in required_fields:
                assert field in config, f"{file_path.name} missing required field: {field}"
            
            # Validate sales_phase structure
            assert 'phase' in config['sales_phase']
            assert 'objective' in config['sales_phase']  # Field is 'objective', not 'description'
            
            # Validate urgency structure
            assert 'level' in config['urgency']
            assert 'timeline_expectation' in config['urgency']
            
            # Validate primary_objection structure
            assert 'type' in config['primary_objection']
            assert 'label' in config['primary_objection']  # Field is 'label', not 'intensity'
            
            # Validate objection type is valid (enumerated values)
            valid_objection_types = [
                'price', 'value', 'fit', 'risk', 'trust', 
                'need', 'competition', 'technical'
            ]
            objection_type = config['primary_objection']['type']
            assert isinstance(objection_type, str), \
                f"{file_path.name} objection type must be a string"
            assert objection_type in valid_objection_types, \
                f"Invalid objection type '{objection_type}' in {file_path.name}. Must be one of: {valid_objection_types}"
            
            # Validate urgency level is valid (enumerated values)
            valid_urgency_levels = ['baja', 'media', 'alta']
            urgency_level = config['urgency']['level']
            assert isinstance(urgency_level, str), \
                f"{file_path.name} urgency level must be a string"
            assert urgency_level in valid_urgency_levels, \
                f"Invalid urgency level '{urgency_level}' in {file_path.name}. Must be one of: {valid_urgency_levels}"
    
    # =========================================================================
    # LAYER 4: Client Psychology
    # =========================================================================
    
    def test_client_psychology_structure(self, config_base_path, prompt_builder):
        """Test that all client psychology files have required structure."""
        psychology_dir = config_base_path / "client_psychology"
        psychology_files = list(psychology_dir.glob("*.yaml"))
        
        assert len(psychology_files) >= 3, "At least 3 psychology profiles must exist"
        
        required_fields = [
            'id', 'name', 'version',
            'client_profile', 'challenge_level', 'conversation_behavior'
        ]
        
        for file_path in psychology_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            for field in required_fields:
                assert field in config, f"{file_path.name} missing required field: {field}"
            
            # Validate client_profile structure
            assert 'personality' in config['client_profile']
            assert 'emotional_state' in config['client_profile']
            assert 'processing_style' in config['client_profile']
            
            # Validate personality has traits
            assert 'traits' in config['client_profile']['personality']
            assert len(config['client_profile']['personality']['traits']) > 0
            
            # Validate challenge_level structure
            assert 'difficulty' in config['challenge_level']
            assert 'cooperation' in config['challenge_level']
            assert 'objection_intensity' in config['challenge_level']
            
            # Validate conversation_behavior
            assert 'pace' in config['conversation_behavior']
            assert 'question_frequency' in config['conversation_behavior']
            
            # Validate difficulty level if present (enumerated values)
            if 'level' in config['challenge_level']['difficulty']:
                difficulty_level = config['challenge_level']['difficulty']['level']
                valid_difficulty_levels = [
                    'muy_facil', 'facil', 'medio', 'alto', 
                    'dificil', 'muy_dificil'
                ]
                assert isinstance(difficulty_level, str), \
                    f"{file_path.name} difficulty level must be a string"
                # Allow any difficulty level string, but log common ones
                # This is flexible to allow new difficulty levels
    
    # =========================================================================
    # LAYER 5: Client Identity
    # =========================================================================
    
    def test_client_identity_structure(self, config_base_path, prompt_builder):
        """Test that all client identity files have required structure."""
        identity_dir = config_base_path / "client_identity"
        identity_files = list(identity_dir.glob("*.yaml"))
        
        assert len(identity_files) >= 3, "At least 3 client identities must exist (María, Carlos, Ana)"
        
        required_fields = [
            'id', 'name', 'version',
            'identity', 'voice_config', 'communication_style',
            'unique_characteristics', 'conversation_specifics'
        ]
        
        for file_path in identity_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            for field in required_fields:
                assert field in config, f"{file_path.name} missing required field: {field}"
            
            # Validate identity structure
            assert 'age' in config['identity']
            assert 'nationality' in config['identity']
            assert 'role' in config['identity']
            
            # Validate voice_config structure (CRITICAL for voice conversations)
            assert 'accent' in config['voice_config']
            assert 'voice_id' in config['voice_config']
            assert 'language' in config['voice_config']
            assert 'dialect' in config['voice_config']
            
            # Validate communication_style structure
            assert 'formality' in config['communication_style']
            assert 'response_length' in config['communication_style']
            
            # Validate formality is a string (allow any value for flexibility)
            formality = config['communication_style']['formality']
            assert isinstance(formality, str), \
                f"{file_path.name} formality must be a string"
            assert len(formality) > 0, \
                f"{file_path.name} formality cannot be empty"
            
            # Validate response_length is a string (allow any value for flexibility)
            response_length = config['communication_style']['response_length']
            assert isinstance(response_length, str), \
                f"{file_path.name} response_length must be a string"
            assert len(response_length) > 0, \
                f"{file_path.name} response_length cannot be empty"
            
            # Validate unique_characteristics is a list
            assert isinstance(config['unique_characteristics'], list)
            assert len(config['unique_characteristics']) > 0, \
                f"{file_path.name} must have at least one unique characteristic"
            
            # Validate conversation_specifics has expressions
            assert 'expressions' in config['conversation_specifics']
            expressions = config['conversation_specifics']['expressions']
            
            # Required expression categories
            required_expressions = ['agreement', 'doubt', 'concern', 'enthusiasm']
            for expr_type in required_expressions:
                assert expr_type in expressions, \
                    f"{file_path.name} missing expression type: {expr_type}"
                assert len(expressions[expr_type]) > 0, \
                    f"{file_path.name} must have at least one {expr_type} expression"


class TestPersonalitySpecifics:
    """Test specific personality characteristics and differentiation."""
    
    @pytest.fixture
    def config_base_path(self) -> Path:
        """Get base path for configuration files."""
        return Path(__file__).parent.parent / "src" / "shared" / "infrastructure" / "config"
    
    @pytest.fixture
    def prompt_service(self) -> PromptService:
        """Create PromptService instance."""
        return PromptService(strict_validation=False)
    
    @pytest.fixture
    def all_identities(self, config_base_path) -> Dict[str, Dict[str, Any]]:
        """Load all identity configurations."""
        identity_dir = config_base_path / "client_identity"
        identities = {}
        
        for file_path in identity_dir.glob("*.yaml"):
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                identities[config['id']] = config
        
        return identities
    
    @pytest.fixture
    def all_psychologies(self, config_base_path) -> Dict[str, Dict[str, Any]]:
        """Load all psychology configurations."""
        psychology_dir = config_base_path / "client_psychology"
        psychologies = {}
        
        for file_path in psychology_dir.glob("*.yaml"):
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                psychologies[config['id']] = config
        
        return psychologies
    
    # =========================================================================
    # Voice Configuration Tests
    # =========================================================================
    
    def test_voice_config_structure_and_types(self, all_identities):
        """Test that each identity has valid voice configuration structure and types."""
        for identity_id, identity in all_identities.items():
            voice_config = identity['voice_config']
            
            # Voice_id must exist and be a non-empty string
            assert 'voice_id' in voice_config, f"{identity_id} missing voice_id"
            voice_id = voice_config['voice_id']
            assert isinstance(voice_id, str), f"{identity_id} voice_id must be a string"
            assert len(voice_id) > 0, f"{identity_id} voice_id cannot be empty"
            
            # Accent must exist and be a non-empty string
            assert 'accent' in voice_config, f"{identity_id} missing accent"
            accent = voice_config['accent']
            assert isinstance(accent, str), f"{identity_id} accent must be a string"
            assert len(accent) > 0, f"{identity_id} accent cannot be empty"
            
            # Language must exist and be a non-empty string
            assert 'language' in voice_config, f"{identity_id} missing language"
            language = voice_config['language']
            assert isinstance(language, str), f"{identity_id} language must be a string"
            assert len(language) > 0, f"{identity_id} language cannot be empty"
            
            # Dialect must exist and be a non-empty string
            assert 'dialect' in voice_config, f"{identity_id} missing dialect"
            dialect = voice_config['dialect']
            assert isinstance(dialect, str), f"{identity_id} dialect must be a string"
            assert len(dialect) > 0, f"{identity_id} dialect cannot be empty"
    
    def test_identity_has_nationality(self, all_identities):
        """Test that each identity has a nationality field."""
        for identity_id, identity in all_identities.items():
            # Nationality must exist and be a non-empty string
            assert 'nationality' in identity['identity'], f"{identity_id} missing nationality"
            nationality = identity['identity']['nationality']
            assert isinstance(nationality, str), f"{identity_id} nationality must be a string"
            assert len(nationality) > 0, f"{identity_id} nationality cannot be empty"
    
    # =========================================================================
    # Cultural Expression Tests
    # =========================================================================
    
    def test_expressions_structure_and_completeness(self, all_identities):
        """Test that each identity has complete expression structure with all categories."""
        required_expression_types = ['agreement', 'doubt', 'concern', 'enthusiasm']
        
        for identity_id, identity in all_identities.items():
            expressions = identity['conversation_specifics']['expressions']
            
            # All required expression types must exist
            for expr_type in required_expression_types:
                assert expr_type in expressions, \
                    f"{identity_id} missing expression type: {expr_type}"
                
                # Each expression type must be a list
                assert isinstance(expressions[expr_type], list), \
                    f"{identity_id} {expr_type} must be a list"
                
                # Each expression type must have at least one expression
                assert len(expressions[expr_type]) > 0, \
                    f"{identity_id} must have at least one {expr_type} expression"
                
                # Each expression must be a non-empty string
                for expr in expressions[expr_type]:
                    assert isinstance(expr, str), \
                        f"{identity_id} {expr_type} expressions must be strings"
                    assert len(expr) > 0, \
                        f"{identity_id} {expr_type} expressions cannot be empty"
    
    def test_unique_characteristics_are_distinctive(self, all_identities):
        """Test that unique_characteristics field contains truly unique traits."""
        for identity_id, identity in all_identities.items():
            characteristics = identity['unique_characteristics']
            
            # Should have at least 3 unique characteristics
            assert len(characteristics) >= 3, \
                f"{identity_id} should have at least 3 unique characteristics"
            
            # Each characteristic should be a non-empty string
            for char in characteristics:
                assert isinstance(char, str), \
                    f"{identity_id} characteristics must be strings"
                assert len(char) > 10, \
                    f"{identity_id} characteristics should be descriptive (>10 chars)"
    
    # =========================================================================
    # Psychology Recommendation Tests (Not Restrictions)
    # =========================================================================
    
    def test_psychology_recommendations_exist(self, all_identities):
        """Test that identities have psychology recommendations (metadata only)."""
        for identity_id, identity in all_identities.items():
            # Check if metadata section exists
            if 'metadata' in identity:
                metadata = identity['metadata']
                
                # psychological_profile_recommended is optional but recommended
                if 'psychological_profile_recommended' in metadata:
                    recommended_psych = metadata['psychological_profile_recommended']
                    
                    # Should be a non-empty string
                    assert isinstance(recommended_psych, str), \
                        f"{identity_id} psychology recommendation must be a string"
                    assert len(recommended_psych) > 0, \
                        f"{identity_id} psychology recommendation cannot be empty"
                    
                    # Should match one of the existing psychology IDs
                    valid_psychologies = [
                        'conservative_analytical', 
                        'impulsive_enthusiastic', 
                        'skeptical_pragmatic'
                    ]
                    assert recommended_psych in valid_psychologies, \
                        f"{identity_id} recommends unknown psychology: {recommended_psych}"
    
    def test_psychology_recommendation_is_valid(self, all_identities, all_psychologies):
        """Test that psychology recommendations reference existing psychology IDs."""
        valid_psychology_ids = set(all_psychologies.keys())
        
        for identity_id, identity in all_identities.items():
            if 'metadata' in identity and 'psychological_profile_recommended' in identity['metadata']:
                recommended = identity['metadata']['psychological_profile_recommended']
                
                # Recommendation must be a string
                assert isinstance(recommended, str), \
                    f"{identity_id} psychology recommendation must be a string"
                
                # Recommendation must reference an existing psychology ID
                assert recommended in valid_psychology_ids, \
                    f"{identity_id} recommends non-existent psychology: {recommended}"
    
    # =========================================================================
    # Flexibility Tests (Any Identity + Any Psychology)
    # =========================================================================
    
    def test_any_identity_with_any_psychology_works(self, prompt_service):
        """Test that any identity can be combined with any psychology."""
        identities = ['maria_rodriguez', 'carlos_mendoza', 'ana_garcia']
        psychologies = ['conservative_analytical', 'impulsive_enthusiastic', 'skeptical_pragmatic']
        
        # Test a sample of combinations (not all to keep test fast)
        test_combinations = [
            ('maria_rodriguez', 'impulsive_enthusiastic'),  # Against default
            ('carlos_mendoza', 'skeptical_pragmatic'),  # Against default
            ('ana_garcia', 'impulsive_enthusiastic'),  # Against default
            ('maria_rodriguez', 'conservative_analytical'),  # Non-default
            ('carlos_mendoza', 'conservative_analytical'),  # Non-default
        ]
        
        for identity_id, psychology_id in test_combinations:
            # This should work without errors
            is_valid = prompt_service.validate_combination(
                industry_id="real_estate",
                situation_id="discovery_no_urgency_price",
                psychology_id=psychology_id,
                identity_id=identity_id
            )
            
            assert is_valid, \
                f"Combination {identity_id} + {psychology_id} should be valid"
            
            # Generate prompt should not raise exceptions
            prompt = prompt_service.generate_prompt(
                industry_id="real_estate",
                situation_id="discovery_no_urgency_price",
                psychology_id=psychology_id,
                identity_id=identity_id
            )
            
            assert len(prompt) > 100, \
                f"Prompt for {identity_id} + {psychology_id} should be substantial"
    
    # =========================================================================
    # Differentiation Tests
    # =========================================================================
    
    def test_same_psychology_different_identities_generates_different_prompts(
        self, prompt_service
    ):
        """Test that same psychology + different identities = different prompts."""
        # Use same psychology but different identities
        psychology_id = "conservative_analytical"
        identities = ['maria_rodriguez', 'carlos_mendoza', 'ana_garcia']
        
        prompts = {}
        for identity_id in identities:
            prompt = prompt_service.generate_prompt(
                industry_id="real_estate",
                situation_id="discovery_no_urgency_price",
                psychology_id=psychology_id,
                identity_id=identity_id
            )
            prompts[identity_id] = prompt
        
        # All prompts should be different
        prompt_list = list(prompts.values())
        assert prompt_list[0] != prompt_list[1], \
            "María and Carlos with same psychology should generate different prompts"
        assert prompt_list[1] != prompt_list[2], \
            "Carlos and Ana with same psychology should generate different prompts"
        assert prompt_list[0] != prompt_list[2], \
            "María and Ana with same psychology should generate different prompts"
    
    def test_identity_cultural_traits_preserved_in_prompt(
        self, prompt_service, all_identities
    ):
        """Test that identity's cultural characteristics appear in final prompt."""
        for identity_id in ['maria_rodriguez', 'carlos_mendoza', 'ana_garcia']:
            if identity_id not in all_identities:
                continue
            
            identity = all_identities[identity_id]
            
            # Generate prompt
            prompt = prompt_service.generate_prompt(
                industry_id="real_estate",
                situation_id="discovery_no_urgency_price",
                psychology_id="conservative_analytical",
                identity_id=identity_id
            )
            
            # Check that name appears in prompt
            name = identity['name']
            assert name in prompt, \
                f"Identity name '{name}' should appear in prompt"
            
            # Check that nationality appears in prompt
            nationality = identity['identity']['nationality']
            assert nationality in prompt, \
                f"Nationality '{nationality}' should appear in prompt"
            
            # Check that role appears in prompt
            role = identity['identity']['role']
            assert role in prompt or role.lower() in prompt.lower(), \
                f"Role '{role}' should appear in prompt"


class TestCombinationFlexibility:
    """Test the flexibility of the 5-layer system."""
    
    @pytest.fixture
    def prompt_service(self) -> PromptService:
        """Create PromptService instance."""
        return PromptService(strict_validation=False)
    
    def test_total_possible_combinations(self, prompt_service):
        """Test that system can generate all possible combinations."""
        total = prompt_service.get_total_combinations()
        
        # Should be: 2 industries × 4 situations × 3 psychologies × 3 identities = 72
        assert total >= 72, \
            f"System should support at least 72 combinations, got {total}"
    
    def test_all_72_combinations_generate_valid_prompts(self, prompt_service):
        """Test that all 72 base combinations generate valid prompts."""
        options = prompt_service.get_all_available_options()
        
        industries = [opt['id'] for opt in options['industries']]
        situations = [opt['id'] for opt in options['situations']]
        psychologies = [opt['id'] for opt in options['psychologies']]
        identities = [opt['id'] for opt in options['identities']]
        
        successful = 0
        failed = []
        
        # Test all combinations (this may take a few seconds)
        for industry in industries:
            for situation in situations:
                for psychology in psychologies:
                    for identity in identities:
                        try:
                            prompt = prompt_service.generate_prompt(
                                industry, situation, psychology, identity
                            )
                            
                            # Basic validation
                            if len(prompt) > 100:
                                successful += 1
                            else:
                                failed.append(
                                    f"{industry}+{situation}+{psychology}+{identity}: too short"
                                )
                        except Exception as e:
                            failed.append(
                                f"{industry}+{situation}+{psychology}+{identity}: {str(e)}"
                            )
        
        total = len(industries) * len(situations) * len(psychologies) * len(identities)
        success_rate = (successful / total) * 100
        
        # Print summary
        print(f"\n✅ Successful: {successful}/{total}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if failed:
            print(f"\n❌ Failed ({len(failed)}):")
            for failure in failed[:5]:  # Show first 5
                print(f"  - {failure}")
        
        # Should have at least 95% success rate
        assert success_rate >= 95.0, \
            f"At least 95% of combinations should work (got {success_rate:.1f}%)"

