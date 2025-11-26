"""
Test to verify all imports work correctly.
"""
import pytest


@pytest.mark.skip(reason="Legacy persona module removed - replaced by 5-layer system")
def test_import_persona():
    """Test importing Persona and related classes - LEGACY."""
    pass


def test_import_conversation_service():
    """Test importing conversation service."""
    from src.conversation.application.services.voice_conversation_service import VoiceConversationService
    
    # Should be able to import without errors
    assert VoiceConversationService is not None


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
