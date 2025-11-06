"""
Expanded tests for PromptService to achieve high coverage
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.shared.application.prompt_service import PromptService
from src.shared.domain.prompt_builder import PromptBuilder


class TestPromptServiceExpanded:
    """Expanded tests for PromptService"""
    
    @pytest.fixture
    def prompt_service(self):
        """Create PromptService instance"""
        return PromptService(strict_validation=False)
    
    @pytest.fixture
    def strict_service(self):
        """Create PromptService with strict validation"""
        return PromptService(strict_validation=True)
    
    def test_service_initialization_default(self):
        """Test service initialization with defaults"""
        service = PromptService()
        assert service is not None
        assert service.prompt_builder is not None
        assert service.strict_validation is False
    
    def test_service_initialization_strict(self):
        """Test service initialization with strict validation"""
        service = PromptService(strict_validation=True)
        assert service.strict_validation is True
    
    def test_generate_prompt_calls_builder(self, prompt_service):
        """Test that generate_prompt calls the builder"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test prompt"
            
            result = prompt_service.generate_prompt(
                "industry", "situation", "psychology", "identity"
            )
            
            mock_build.assert_called_once_with(
                "industry", "situation", "psychology", "identity"
            )
            assert result == "Test prompt"
    
    def test_validate_combination_valid(self, prompt_service):
        """Test validate_combination with valid IDs"""
        with patch.object(prompt_service.prompt_builder, '_validate_layer_exists') as mock_validate:
            mock_validate.return_value = None  # No exception
            
            result = prompt_service.validate_combination(
                "industry", "situation", "psychology", "identity"
            )
            
            assert result is True
            assert mock_validate.call_count == 4
    
    def test_validate_combination_invalid(self, prompt_service):
        """Test validate_combination with invalid ID"""
        with patch.object(prompt_service.prompt_builder, '_validate_layer_exists') as mock_validate:
            mock_validate.side_effect = FileNotFoundError("Not found")
            
            result = prompt_service.validate_combination(
                "invalid", "situation", "psychology", "identity"
            )
            
            assert result is False
    
    def test_get_all_available_options(self, prompt_service):
        """Test getting all available options"""
        with patch.object(prompt_service.prompt_builder, 'get_available_industries') as mock_ind, \
             patch.object(prompt_service.prompt_builder, 'get_available_situations') as mock_sit, \
             patch.object(prompt_service.prompt_builder, 'get_available_psychologies') as mock_psy, \
             patch.object(prompt_service.prompt_builder, 'get_available_identities') as mock_ident:
            
            mock_ind.return_value = ['ind1']
            mock_sit.return_value = ['sit1']
            mock_psy.return_value = ['psy1']
            mock_ident.return_value = ['ident1']
            
            result = prompt_service.get_all_available_options()
            
            assert 'industries' in result
            assert 'situations' in result
            assert 'psychologies' in result
            assert 'identities' in result
            assert len(result['industries']) == 1
    
    def test_get_total_combinations(self, prompt_service):
        """Test calculating total combinations"""
        with patch.object(prompt_service.prompt_builder, 'get_available_industries') as mock_ind, \
             patch.object(prompt_service.prompt_builder, 'get_available_situations') as mock_sit, \
             patch.object(prompt_service.prompt_builder, 'get_available_psychologies') as mock_psy, \
             patch.object(prompt_service.prompt_builder, 'get_available_identities') as mock_ident:
            
            mock_ind.return_value = ['i1', 'i2']
            mock_sit.return_value = ['s1', 's2', 's3']
            mock_psy.return_value = ['p1', 'p2']
            mock_ident.return_value = ['id1', 'id2', 'id3']
            
            result = prompt_service.get_total_combinations()
            
            # 2 * 3 * 2 * 3 = 36
            assert result == 36
    
    def test_get_prompt_telemetry_exists(self, prompt_service):
        """Test getting telemetry for existing prompt"""
        with patch.object(prompt_service, 'generate_prompt') as mock_gen:
            mock_gen.return_value = "Test prompt" * 50  # ~600 chars
            
            result = prompt_service.get_prompt_telemetry(
                "industry", "situation", "psychology", "identity"
            )
            
            assert 'prompt_hash' in result
            assert 'prompt_length' in result
            assert 'word_count' in result
            assert 'generated_at' in result
            assert 'layer_ids' in result
            assert result['prompt_length'] > 0
    
    def test_get_prompt_telemetry_structure(self, prompt_service):
        """Test telemetry structure"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test prompt content"
            
            result = prompt_service.get_prompt_telemetry(
                "ind", "sit", "psy", "ident"
            )
            
            # Check all required fields
            assert 'prompt_hash' in result
            assert 'generated_at' in result
            assert 'layer_ids' in result
            assert 'prompt_length' in result
            assert 'word_count' in result
            assert 'validation_warnings' in result
            assert 'is_semantically_valid' in result
            assert 'strict_validation_enabled' in result
            
            # Check layer_ids structure
            assert result['layer_ids']['industry'] == 'ind'
            assert result['layer_ids']['situation'] == 'sit'
            assert result['layer_ids']['psychology'] == 'psy'
            assert result['layer_ids']['identity'] == 'ident'
    
    def test_clear_cache_delegates_to_builder(self, prompt_service):
        """Test that clear_cache delegates to builder"""
        with patch.object(prompt_service.prompt_builder, 'clear_cache') as mock_clear:
            prompt_service.clear_cache()
            mock_clear.assert_called_once()
    
    def test_prompt_hash_consistency(self, prompt_service):
        """Test that same prompt generates same hash"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Consistent prompt content"
            
            telemetry1 = prompt_service.get_prompt_telemetry("i", "s", "p", "id")
            telemetry2 = prompt_service.get_prompt_telemetry("i", "s", "p", "id")
            
            assert telemetry1['prompt_hash'] == telemetry2['prompt_hash']
    
    def test_prompt_hash_different_for_different_prompts(self, prompt_service):
        """Test that different prompts generate different hashes"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.side_effect = [
                "Prompt content 1",
                "Prompt content 2"
            ]
            
            telemetry1 = prompt_service.get_prompt_telemetry("i1", "s", "p", "id")
            telemetry2 = prompt_service.get_prompt_telemetry("i2", "s", "p", "id")
            
            assert telemetry1['prompt_hash'] != telemetry2['prompt_hash']
    
    def test_word_count_calculation(self, prompt_service):
        """Test word count calculation in telemetry"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "one two three four five"
            
            telemetry = prompt_service.get_prompt_telemetry("i", "s", "p", "id")
            
            assert telemetry['word_count'] == 5
    
    def test_validation_warnings_in_permissive_mode(self, prompt_service):
        """Test that warnings are captured in permissive mode"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test prompt"
            
            # This should not raise even with warnings
            result = prompt_service.generate_prompt("i", "s", "p", "id")
            
            assert result is not None
            assert isinstance(result, str)
    
    def test_strict_mode_attribute(self, strict_service):
        """Test that strict mode is set correctly"""
        assert strict_service.strict_validation is True
        
        telemetry = MagicMock()
        with patch.object(strict_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test"
            
            result = strict_service.get_prompt_telemetry("i", "s", "p", "id")
            
            assert result['strict_validation_enabled'] is True
    
    def test_permissive_mode_attribute(self, prompt_service):
        """Test that permissive mode is set correctly"""
        assert prompt_service.strict_validation is False
        
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test"
            
            result = prompt_service.get_prompt_telemetry("i", "s", "p", "id")
            
            assert result['strict_validation_enabled'] is False
    
    def test_generate_prompt_returns_string(self, prompt_service):
        """Test that generate_prompt always returns string"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test prompt"
            
            result = prompt_service.generate_prompt("i", "s", "p", "id")
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_telemetry_timestamp_format(self, prompt_service):
        """Test that generated_at is in ISO format"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.return_value = "Test"
            
            result = prompt_service.get_prompt_telemetry("i", "s", "p", "id")
            
            # Should be ISO format timestamp
            assert 'T' in result['generated_at']
            assert 'Z' in result['generated_at'] or '+' in result['generated_at']
    
    def test_service_with_custom_config_path(self):
        """Test service with custom config path"""
        service = PromptService(config_path="/custom/path")
        assert service is not None
        # Config path should be passed to builder
    
    def test_multiple_prompts_independent(self, prompt_service):
        """Test that multiple prompt generations are independent"""
        with patch.object(prompt_service.prompt_builder, 'build_prompt') as mock_build:
            mock_build.side_effect = ["Prompt 1", "Prompt 2", "Prompt 3"]
            
            result1 = prompt_service.generate_prompt("i1", "s1", "p1", "id1")
            result2 = prompt_service.generate_prompt("i2", "s2", "p2", "id2")
            result3 = prompt_service.generate_prompt("i3", "s3", "p3", "id3")
            
            assert result1 != result2
            assert result2 != result3
            assert mock_build.call_count == 3

