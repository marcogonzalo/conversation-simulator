"""
Basic functionality tests that work with the actual implementation.
"""
import pytest


@pytest.mark.skip(reason="Legacy persona module removed")
def test_persona_creation():
    """Test creating a persona - LEGACY."""
    pass


def test_persona_id_removed():
    """Persona ID test - LEGACY REMOVED"""
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


def test_persona_id():
    """Test persona ID functionality."""
    from src.persona.domain.value_objects.persona_id import PersonaId
    
    persona_id = PersonaId("test-id-123")
    
    assert str(persona_id) == "test-id-123"
    assert persona_id.value == "test-id-123"


def test_personality_traits_creation():
    """Test personality traits creation."""
    from src.persona.domain.value_objects.personality_traits import PersonalityTraits
    
    traits = PersonalityTraits(["friendly", "analytical"])
    
    # Test that traits were created
    assert traits is not None
    assert len(traits.traits) == 2


def test_websocket_helpers_import():
    """Test that WebSocket helpers can be imported."""
    from src.api.routes.websocket_helpers import send_error, send_transcribed_text
    
    # Test that functions exist and are callable
    assert callable(send_error)
    assert callable(send_transcribed_text)


def test_event_bus_import():
    """Test that event bus can be imported."""
    from src.shared.infrastructure.messaging.event_bus import event_bus
    
    # Test that event bus exists
    assert event_bus is not None


def test_api_config_import():
    """Test that API config can be imported."""
    from src.shared.infrastructure.external_apis.api_config import api_config
    
    # Test that config exists
    assert api_config is not None


def test_conversation_service_creation():
    """Test creating conversation service with mocks."""
    from unittest.mock import Mock
    from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
    
    # Create mocks for dependencies
    mock_conversation_service = Mock()
    mock_voice_service = Mock()
    
    # Create service instance
    service = OpenAIVoiceConversationService(
        conversation_service=mock_conversation_service,
        voice_service=mock_voice_service
    )
    
    assert service.conversation_service == mock_conversation_service
    assert service.voice_service == mock_voice_service


def test_audio_service_creation():
    """Test creating audio service with mocks."""
    from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
    from src.shared.infrastructure.external_apis.api_config import api_config
    
    # Create service instance
    service = OpenAIVoiceService(api_config)
    
    assert service.api_config == api_config
    assert service.is_connected is False


def test_audio_chunks_initialization():
    """Test that audio chunks dictionary is initialized."""
    from unittest.mock import Mock
    from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
    
    # Create mocks for dependencies
    mock_conversation_service = Mock()
    mock_voice_service = Mock()
    
    service = OpenAIVoiceConversationService(
        conversation_service=mock_conversation_service,
        voice_service=mock_voice_service
    )
    
    # Test that audio_chunks is initialized
    assert hasattr(service, 'audio_chunks')
    assert isinstance(service.audio_chunks, dict)
    assert len(service.audio_chunks) == 0


def test_active_conversations_initialization():
    """Test that active_conversations dictionary is initialized."""
    from unittest.mock import Mock
    from src.conversation.application.services.openai_voice_conversation_service import OpenAIVoiceConversationService
    
    # Create mocks for dependencies
    mock_conversation_service = Mock()
    mock_voice_service = Mock()
    
    service = OpenAIVoiceConversationService(
        conversation_service=mock_conversation_service,
        voice_service=mock_voice_service
    )
    
    # Test that active_conversations is initialized
    assert hasattr(service, 'active_conversations')
    assert isinstance(service.active_conversations, dict)
    assert len(service.active_conversations) == 0


def test_voice_service_properties():
    """Test that voice service has expected properties."""
    from src.audio.infrastructure.services.openai_voice_service import OpenAIVoiceService
    from src.shared.infrastructure.external_apis.api_config import api_config
    
    service = OpenAIVoiceService(api_config)
    
    # Test basic properties
    assert hasattr(service, 'api_config')
    assert hasattr(service, 'is_connected')
    assert hasattr(service, 'websocket')
    assert service.is_connected is False
    assert service.websocket is None


def test_api_config_properties():
    """Test that API config has expected properties."""
    from src.shared.infrastructure.external_apis.api_config import api_config
    
    # Test that config has expected attributes
    assert hasattr(api_config, 'openai_api_key')
    assert hasattr(api_config, 'openai_voice_model')
    assert hasattr(api_config, 'audio_playback_sample_rate')
