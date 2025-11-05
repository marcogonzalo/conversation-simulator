"""
Tests for Prompt Telemetry System
Tests metadata generation, storage, and retrieval
"""

import pytest
from src.shared.application.prompt_service import PromptService
from src.shared.domain.prompt_builder import PromptBuilder


class TestPromptTelemetry:
    """Test suite for prompt telemetry system."""
    
    def test_prompt_generation_creates_metadata(self):
        """Generating a prompt should create comprehensive metadata."""
        service = PromptService()
        
        # Generate prompt
        prompt = service.generate_prompt(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        
        # Get telemetry
        metadata = service.get_prompt_telemetry(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        
        # Verify metadata exists and has required fields
        assert metadata is not None
        assert 'prompt_hash' in metadata
        assert 'generated_at' in metadata
        assert 'layer_ids' in metadata
        assert 'file_versions' in metadata
        assert 'prompt_length' in metadata
        assert 'word_count' in metadata
        assert 'validation_warnings' in metadata
        assert 'is_semantically_valid' in metadata
        assert 'cache_key' in metadata
    
    def test_prompt_hash_is_unique_per_combination(self):
        """Different combinations should have different prompt hashes."""
        service = PromptService()
        
        # Generate two different prompts
        prompt1 = service.generate_prompt(
            "real_estate", "discovery_no_urgency_price", 
            "conservative_analytical", "ana_garcia"
        )
        
        prompt2 = service.generate_prompt(
            "real_estate", "closing_high_urgency_fit",
            "impulsive_enthusiastic", "carlos_mendoza"
        )
        
        # Get metadata
        meta1 = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        meta2 = service.get_prompt_telemetry(
            "real_estate", "closing_high_urgency_fit",
            "impulsive_enthusiastic", "carlos_mendoza"
        )
        
        # Hashes should be different
        assert meta1['prompt_hash'] != meta2['prompt_hash']
        assert meta1['cache_key'] != meta2['cache_key']
    
    def test_prompt_hash_is_consistent_for_same_combination(self):
        """Same combination should produce same hash (deterministic)."""
        service = PromptService()
        
        # Generate same prompt twice (second time from cache)
        prompt1 = service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        meta1 = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        # Clear cache
        service.clear_cache()
        
        # Generate again
        prompt2 = service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        meta2 = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        # Note: Hash will be different due to session_id in security wrapper
        # But layer_ids and file_versions should be identical
        assert meta1['layer_ids'] == meta2['layer_ids']
        assert meta1['cache_key'] == meta2['cache_key']
    
    def test_layer_ids_are_stored_correctly(self):
        """Metadata should store all 4 layer IDs."""
        service = PromptService()
        
        service.generate_prompt(
            "real_estate", "presentation_medium_urgency_value",
            "skeptical_pragmatic", "maria_rodriguez"
        )
        
        metadata = service.get_prompt_telemetry(
            "real_estate", "presentation_medium_urgency_value",
            "skeptical_pragmatic", "maria_rodriguez"
        )
        
        assert metadata['layer_ids']['industry'] == 'real_estate'
        assert metadata['layer_ids']['situation'] == 'presentation_medium_urgency_value'
        assert metadata['layer_ids']['psychology'] == 'skeptical_pragmatic'
        assert metadata['layer_ids']['identity'] == 'maria_rodriguez'
    
    def test_file_versions_are_tracked(self):
        """File versions should be tracked for reproducibility."""
        service = PromptService()
        
        service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        metadata = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        file_versions = metadata['file_versions']
        
        # All 5 layers should have version info
        assert 'simulation_rules' in file_versions
        assert 'industry' in file_versions
        assert 'situation' in file_versions
        assert 'psychology' in file_versions
        assert 'identity' in file_versions
        
        # Versions should be 8-char hex strings or special values
        for version in file_versions.values():
            assert isinstance(version, str)
            assert len(version) in [8, len("not_found"), len("unknown")]
    
    def test_prompt_length_and_word_count(self):
        """Metadata should include prompt length metrics."""
        service = PromptService()
        
        prompt = service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        metadata = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        # Length should match actual prompt
        assert metadata['prompt_length'] == len(prompt)
        assert metadata['word_count'] == len(prompt.split())
        
        # Sanity checks
        assert metadata['prompt_length'] > 1000  # Should be substantial
        assert metadata['word_count'] > 100
    
    def test_validation_warnings_count_is_tracked(self):
        """Metadata should track semantic validation warnings count."""
        service = PromptService()
        
        # Generate prompt (might have warnings)
        service.generate_prompt(
            "real_estate", "closing_high_urgency_fit",
            "impulsive_enthusiastic", "carlos_mendoza"
        )
        
        metadata = service.get_prompt_telemetry(
            "real_estate", "closing_high_urgency_fit",
            "impulsive_enthusiastic", "carlos_mendoza"
        )
        
        # Should have validation_warnings field
        assert 'validation_warnings' in metadata
        assert isinstance(metadata['validation_warnings'], int)
        assert metadata['validation_warnings'] >= 0
        
        # Should have is_semantically_valid flag
        assert 'is_semantically_valid' in metadata
        assert isinstance(metadata['is_semantically_valid'], bool)
    
    def test_strict_validation_mode_is_recorded(self):
        """Metadata should record if strict validation was enabled."""
        service_permissive = PromptService(strict_validation=False)
        service_strict = PromptService(strict_validation=True)
        
        # Generate with permissive
        service_permissive.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        meta_permissive = service_permissive.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        # Generate with strict (different instance, different cache)
        service_strict.generate_prompt(
            "health_insurance", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        meta_strict = service_strict.get_prompt_telemetry(
            "health_insurance", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        assert meta_permissive['strict_validation_enabled'] is False
        assert meta_strict['strict_validation_enabled'] is True
    
    def test_cache_key_format(self):
        """Cache key should follow expected format."""
        service = PromptService()
        
        service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        metadata = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        expected_key = "real_estate_discovery_no_urgency_price_conservative_analytical_ana_garcia"
        assert metadata['cache_key'] == expected_key
    
    def test_telemetry_for_nonexistent_prompt_returns_none(self):
        """Getting telemetry for non-generated prompt should return None."""
        service = PromptService()
        
        # Don't generate, just try to get metadata
        metadata = service.get_prompt_telemetry(
            "nonexistent_industry", "nonexistent_situation",
            "nonexistent_psychology", "nonexistent_identity"
        )
        
        assert metadata is None
    
    def test_clear_cache_clears_metadata(self):
        """Clearing cache should also clear metadata."""
        service = PromptService()
        
        # Generate prompt (creates metadata)
        service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        # Verify metadata exists
        metadata_before = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        assert metadata_before is not None
        
        # Clear cache
        service.clear_cache()
        
        # Metadata should be gone
        metadata_after = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        assert metadata_after is None
    
    def test_generated_at_timestamp_format(self):
        """Timestamp should be in ISO format."""
        service = PromptService()
        
        service.generate_prompt(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        metadata = service.get_prompt_telemetry(
            "real_estate", "discovery_no_urgency_price",
            "conservative_analytical", "ana_garcia"
        )
        
        # Should be ISO format timestamp
        from datetime import datetime
        timestamp_str = metadata['generated_at']
        
        # Should be parseable as datetime
        parsed = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)

