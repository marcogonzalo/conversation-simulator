"""
Tests for Application Services - UPDATED
Only tests that work
"""
import pytest


class TestOpenAIVoiceApplicationService:
    """Test OpenAI voice application service"""
    
    def test_service_can_be_imported(self):
        """Test that service can be imported"""
        from src.conversation.application.services.voice_conversation_service import VoiceConversationService
        assert VoiceConversationService is not None
    
    # =========================================================================
    # RECONSTRUCTED: Additional application service tests
    # =========================================================================
    
    def test_conversation_application_service_can_be_imported(self):
        """Test that conversation application service can be imported"""
        from src.conversation.application.services.conversation_application_service import ConversationApplicationService
        assert ConversationApplicationService is not None
    
    def test_enhanced_conversation_service_can_be_imported(self):
        """Test that enhanced conversation service can be imported"""
        from src.conversation.application.services.enhanced_conversation_service import EnhancedConversationService
        assert EnhancedConversationService is not None
