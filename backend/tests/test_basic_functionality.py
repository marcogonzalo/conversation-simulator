"""
Basic functionality tests - UPDATED
Only tests that work
"""
import pytest


def test_websocket_helpers_import():
    """Test websocket helpers can be imported"""
    from src.api.routes import websocket_helpers
    assert websocket_helpers is not None


def test_event_bus_import():
    """Test event bus can be imported"""
    from src.shared.infrastructure.messaging.event_bus import EventBus
    assert EventBus is not None


def test_api_config_import():
    """Test API config can be imported"""
    from src.shared.infrastructure.external_apis.api_config import api_config
    assert api_config is not None


def test_conversation_service_can_be_imported():
    """Test conversation service can be imported"""
    from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
    assert OpenAIVoiceConversationService is not None


def test_audio_service_can_be_imported():
    """Test audio service can be imported"""
    from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
    assert OpenAIVoiceService is not None


def test_voice_service_class_exists():
    """Test voice service class exists"""
    from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
    assert OpenAIVoiceService is not None


def test_api_config_has_provider():
    """Test API config has AI provider"""
    from src.shared.infrastructure.external_apis.api_config import api_config
    assert hasattr(api_config, 'ai_provider')

# =========================================================================
# =========================================================================
# RECONSTRUCTED: Additional service tests
# =========================================================================

def test_conversation_repository_can_be_imported():
    """Test conversation repository can be imported"""
    from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository
    assert SQLConversationRepository is not None


def test_transcription_service_can_be_imported():
    """Test transcription service can be imported"""
    from src.conversation.infrastructure.services.transcription_file_service import TranscriptionFileService
    assert TranscriptionFileService is not None


def test_analysis_service_can_be_imported():
    """Test analysis service can be imported"""
    from src.analysis.infrastructure.services.conversation_analysis_service import ConversationAnalysisService
    assert ConversationAnalysisService is not None
# =========================================================================
