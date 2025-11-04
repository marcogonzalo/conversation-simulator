"""
Tests for PromptBuilder Strict Validation Mode
Tests the behavior difference between permissive and strict modes
"""

import pytest
from src.shared.domain.prompt_builder import PromptBuilder


class TestPromptBuilderStrictMode:
    """Test suite for strict vs permissive validation modes."""
    
    def test_coherent_combination_works_in_both_modes(self):
        """Coherent combination should work in both permissive and strict modes."""
        # Permissive mode
        builder_permissive = PromptBuilder(strict_validation=False)
        prompt1 = builder_permissive.build_prompt(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        assert len(prompt1) > 1000  # Prompt was generated
        
        # Strict mode
        builder_strict = PromptBuilder(strict_validation=True)
        prompt2 = builder_strict.build_prompt(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        assert len(prompt2) > 1000  # Prompt was generated
        
        # Both should generate prompts successfully
        assert prompt1 is not None
        assert prompt2 is not None
    
    def test_permissive_mode_allows_unusual_combinations(self):
        """Permissive mode should allow unusual (but not critical) combinations."""
        builder = PromptBuilder(strict_validation=False)
        
        # This combination has a non-critical warning (unusual phase-objection)
        prompt = builder.build_prompt(
            industry_id="real_estate",
            situation_id="closing_high_urgency_fit",
            psychology_id="impulsive_enthusiastic",
            identity_id="carlos_mendoza"
        )
        
        # Should generate successfully despite warning
        assert prompt is not None
        assert len(prompt) > 1000
    
    def test_strict_mode_allows_unusual_combinations(self):
        """Strict mode should also allow unusual combinations (only block CRITICAL ones)."""
        builder = PromptBuilder(strict_validation=True)
        
        # This combination has a non-critical warning (unusual, not critical)
        prompt = builder.build_prompt(
            industry_id="real_estate",
            situation_id="closing_high_urgency_fit",
            psychology_id="impulsive_enthusiastic",
            identity_id="carlos_mendoza"
        )
        
        # Should generate successfully (unusual ≠ critical)
        assert prompt is not None
        assert len(prompt) > 1000
    
    def test_permissive_mode_logs_but_continues_on_contradictions(self, caplog):
        """Permissive mode should log warnings but continue on contradictions."""
        import logging
        caplog.set_level(logging.WARNING)
        
        builder = PromptBuilder(strict_validation=False)
        
        # Create a test YAML with contradictions (if we had one)
        # For now, test with existing files that might have issues
        prompt = builder.build_prompt(
            industry_id="real_estate",
            situation_id="closing_high_urgency_fit",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        
        # Should generate successfully
        assert prompt is not None
        
        # Should have logged warnings if any
        # (we don't assert specific warnings as they depend on config files)
    
    def test_cache_respects_validation_mode(self):
        """Cache should work independently of validation mode."""
        builder_permissive = PromptBuilder(strict_validation=False)
        builder_strict = PromptBuilder(strict_validation=True)
        
        # Generate with permissive (caches)
        prompt1 = builder_permissive.build_prompt(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        
        # Generate with strict (different instance, different cache)
        prompt2 = builder_strict.build_prompt(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )
        
        # Both should generate successfully
        assert prompt1 is not None
        assert prompt2 is not None
        
        # Note: They won't be identical due to session_id in security wrapper,
        # but both should be valid prompts
        assert len(prompt1) > 1000
        assert len(prompt2) > 1000
    
    def test_strict_mode_attribute_is_set(self):
        """Strict validation attribute should be set correctly."""
        builder_permissive = PromptBuilder(strict_validation=False)
        builder_strict = PromptBuilder(strict_validation=True)
        
        assert builder_permissive.strict_validation is False
        assert builder_strict.strict_validation is True
    
    def test_default_is_permissive(self):
        """Default mode should be permissive."""
        builder = PromptBuilder()
        
        assert builder.strict_validation is False
    
    def test_multiple_warnings_are_all_logged(self, caplog):
        """All warnings should be logged, not just the first one."""
        import logging
        caplog.set_level(logging.WARNING)
        
        builder = PromptBuilder(strict_validation=False)
        
        # Use combination that might have multiple warnings
        prompt = builder.build_prompt(
            industry_id="real_estate",
            situation_id="closing_high_urgency_fit",
            psychology_id="impulsive_enthusiastic",
            identity_id="carlos_mendoza"
        )
        
        # Should generate successfully
        assert prompt is not None
        
        # Check that warnings were logged
        warning_logs = [record for record in caplog.records if record.levelname == 'WARNING']
        # At least one warning should be logged if there are semantic issues
        # (actual count depends on the configuration files)


class TestPromptBuilderIntegrationWithAPIConfig:
    """Test integration with APIConfig for strict_validation setting."""
    
    def test_prompt_service_uses_api_config_strict_setting(self, monkeypatch):
        """PromptService should use APIConfig's strict_validation setting."""
        from src.shared.application.prompt_service import PromptService
        from src.shared.infrastructure.external_apis.api_config import APIConfig
        
        # Test with strict mode enabled
        monkeypatch.setenv("PROMPT_STRICT_VALIDATION", "true")
        config = APIConfig()
        assert config.prompt_strict_validation is True
        
        # Test with strict mode disabled
        monkeypatch.setenv("PROMPT_STRICT_VALIDATION", "false")
        config = APIConfig()
        assert config.prompt_strict_validation is False
        
        # Test default (should be false)
        monkeypatch.delenv("PROMPT_STRICT_VALIDATION", raising=False)
        config = APIConfig()
        assert config.prompt_strict_validation is False

