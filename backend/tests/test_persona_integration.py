"""
Integration tests for persona loading and conversation integration.
These tests use REAL implementations, not mocks, to catch integration issues.
"""

import pytest
import asyncio
import os
from pathlib import Path

from src.persona.infrastructure.repositories.yaml_persona_repository import YAMLPersonaRepository
from src.persona.domain.value_objects.persona_id import PersonaId
from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService


@pytest.mark.integration
@pytest.mark.skip(reason="Legacy persona system - replaced by 5-layer system with client_identity")
class TestPersonaIntegration:
    """Integration tests for persona system with real implementations."""
    
    @pytest.fixture
    def persona_repository(self):
        """Create real persona repository."""
        return YAMLPersonaRepository()
    
    @pytest.fixture
    def conversation_repository(self):
        """Create real conversation repository."""
        return SQLConversationRepository()
    
    @pytest.fixture
    def conversation_domain_service(self):
        """Create real conversation domain service."""
        return ConversationDomainService()
    
    @pytest.fixture
    def conversation_service(self, conversation_repository, conversation_domain_service):
        """Create real conversation application service."""
        return ConversationApplicationService(conversation_repository, conversation_domain_service)
    
    @pytest.mark.asyncio
    async def test_persona_repository_loads_real_files(self, persona_repository):
        """Test that persona repository can load real YAML files."""
        # This test will fail if personas can't be loaded from actual files
        personas = await persona_repository.get_all()
        
        # Should load personas from config/persona_details/
        assert len(personas) > 0, "No personas loaded from real files"
        
        # Verify persona structure
        for persona in personas:
            assert persona.name is not None
            assert persona.description is not None
            assert persona.accent is not None
            assert persona.personality_traits is not None
    
    @pytest.mark.asyncio
    async def test_persona_accent_mapping(self, persona_repository):
        """Test that persona accents are mapped correctly."""
        personas = await persona_repository.get_all()
        
        # Check that all personas have valid accents
        valid_accents = {'caribbean_spanish', 'peruvian_spanish', 'venezuelan_spanish', 'florida_english'}
        
        for persona in personas:
            assert persona.accent.value in valid_accents, f"Invalid accent: {persona.accent.value}"
    
    @pytest.mark.asyncio
    async def test_specific_persona_loading(self, persona_repository):
        """Test loading specific personas by ID."""
        # Test loading Carlos Mendoza
        carlos_id = PersonaId.from_string("carlos_mendoza")
        carlos = await persona_repository.get_by_id(carlos_id)
        
        assert carlos is not None, "Carlos Mendoza should be loadable"
        assert carlos.name == "Carlos Mendoza"
        assert carlos.accent.value == "venezuelan_spanish"
    
    @pytest.mark.asyncio
    async def test_persona_filtering_by_accent(self, persona_repository):
        """Test filtering personas by accent."""
        # Test Venezuelan personas
        venezuelan_personas = await persona_repository.get_by_accent("venezuelan_spanish")
        assert len(venezuelan_personas) > 0, "Should find Venezuelan personas"
        
        for persona in venezuelan_personas:
            assert persona.accent.value == "venezuelan_spanish"
    
    @pytest.mark.asyncio
    async def test_conversation_with_real_persona(self, conversation_service, persona_repository):
        """Test starting conversation with real persona."""
        # Skip this test if database is not available
        pytest.skip("Database integration test - requires database setup")
    
    @pytest.mark.asyncio
    async def test_conversation_retrieval_with_real_persona(self, conversation_service):
        """Test retrieving conversation with real persona."""
        # Skip this test if database is not available
        pytest.skip("Database integration test - requires database setup")
    
    @pytest.mark.asyncio
    async def test_persona_validation_with_real_data(self, conversation_domain_service):
        """Test persona validation with real persona IDs."""
        # Test with real persona ID
        can_start = conversation_domain_service.can_start_conversation("carlos_mendoza")
        assert can_start, "Should be able to start conversation with real persona"
    
    def test_config_files_exist(self):
        """Test that configuration files exist and are readable."""
        config_dir = Path("config/persona_details")
        assert config_dir.exists(), "Persona details directory should exist"
        
        # Check for specific persona files
        expected_files = ["carlos_mendoza.yaml", "ana_garcia.yaml", "maria_rodriguez.yaml"]
        for file_name in expected_files:
            file_path = config_dir / file_name
            assert file_path.exists(), f"Persona file should exist: {file_name}"
            assert file_path.is_file(), f"Persona file should be a file: {file_name}"
    
    def test_yaml_files_are_valid(self):
        """Test that YAML files are valid and readable."""
        import yaml
        
        config_dir = Path("config/persona_details")
        for yaml_file in config_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    assert data is not None, f"YAML file should be loadable: {yaml_file.name}"
                    assert 'id' in data, f"YAML file should have 'id' field: {yaml_file.name}"
                    assert 'name' in data, f"YAML file should have 'name' field: {yaml_file.name}"
            except Exception as e:
                pytest.fail(f"YAML file {yaml_file.name} is invalid: {e}")
    
    @pytest.mark.asyncio
    async def test_persona_adapter_conversion(self, persona_repository):
        """Test that persona adapter correctly converts new format to legacy."""
        personas = await persona_repository.get_all()
        
        for persona in personas:
            # Test that adapter conversion worked
            assert hasattr(persona, 'id')
            assert hasattr(persona, 'name')
            assert hasattr(persona, 'accent')
            assert hasattr(persona, 'personality_traits')
            
            # Test that accent is valid
            valid_accents = {'caribbean_spanish', 'peruvian_spanish', 'venezuelan_spanish', 'florida_english'}
            assert persona.accent.value in valid_accents
            
            # Test that personality traits are valid
            assert len(persona.personality_traits.get_trait_names()) > 0
