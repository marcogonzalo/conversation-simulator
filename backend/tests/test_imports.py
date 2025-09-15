"""
Test to verify all imports work correctly.
"""
import pytest


def test_import_persona():
    """Test importing Persona and related classes."""
    from src.persona.domain.entities.persona import Persona, AccentType
    from src.persona.domain.value_objects.personality_traits import PersonalityTraits
    from src.persona.domain.value_objects.persona_id import PersonaId
    
    # Test creating a persona
    persona_id = PersonaId("test-id")
    personality_traits = PersonalityTraits(["friendly"])
    
    persona = Persona(
        persona_id=persona_id,
        name="Test Persona",
        description="Test description",
        background="Test background",
        personality_traits=personality_traits,
        accent=AccentType.CARIBBEAN_SPANISH,
        voice_id="alloy",
        prompt_template="Test template",
        conversation_goals=["Test goal"],
        pain_points=["Test pain"],
        objections=["Test objection"],
        decision_factors=["Test factor"]
    )
    
    assert persona.name == "Test Persona"
    assert persona.accent == AccentType.CARIBBEAN_SPANISH


def test_import_conversation_service():
    """Test importing conversation service."""
    from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
    
    # Should be able to import without errors
    assert OpenAIVoiceConversationService is not None


def test_import_audio_service():
    """Test importing audio service."""
    from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
    
    # Should be able to import without errors
    assert OpenAIVoiceService is not None


def test_import_websocket_helpers():
    """Test importing WebSocket helpers."""
    from src.api.routes.websocket_helpers import send_error, send_transcribed_text
    
    # Should be able to import without errors
    assert send_error is not None
    assert send_transcribed_text is not None
