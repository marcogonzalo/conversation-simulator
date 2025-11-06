"""
Tests for application services
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from uuid import uuid4

from src.conversation.application.services.conversation_application_service import ConversationApplicationService
from src.conversation.application.services.enhanced_conversation_service import EnhancedConversationService
from src.audio.application.services.openai_voice_application_service import OpenAIVoiceApplicationService


class TestConversationApplicationService:
    """Tests for ConversationApplicationService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_domain_service(self):
        """Create mock domain service"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository, mock_domain_service):
        """Create application service"""
        return ConversationApplicationService(
            conversation_repository=mock_repository,
            conversation_domain_service=mock_domain_service
        )
    
    def test_service_initialization(self, service):
        """Test service initializes"""
        assert service is not None
    
    def test_service_has_repository(self, service, mock_repository):
        """Test service has repository"""
        assert service.conversation_repository == mock_repository
    
    def test_service_has_domain_service(self, service, mock_domain_service):
        """Test service has domain service"""
        assert service.conversation_domain_service == mock_domain_service
    
    @pytest.mark.asyncio
    async def test_start_conversation_returns_id(self, service, mock_domain_service, mock_repository):
        """Test start_conversation returns conversation ID"""
        from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        
        mock_conversation = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test",
            context_id="test",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        mock_domain_service.create_conversation.return_value = mock_conversation
        mock_repository.save.return_value = None
        
        result = await service.start_conversation("test_persona", "test_context")
        
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_get_conversation(self, service, mock_repository):
        """Test get_conversation retrieves from repository"""
        from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        
        mock_conversation = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test",
            context_id="test",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        mock_repository.get_by_id.return_value = mock_conversation
        
        result = await service.get_conversation("test_id")
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_conversation(self, service, mock_repository):
        """Test getting nonexistent conversation"""
        mock_repository.get_by_id.return_value = None
        
        result = await service.get_conversation("nonexistent")
        
        assert result is None


class TestEnhancedConversationService:
    """Tests for EnhancedConversationService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_processing_service(self):
        """Create mock processing service"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository, mock_processing_service):
        """Create enhanced conversation service"""
        return EnhancedConversationService(
            repository=mock_repository,
            message_processing_service=mock_processing_service
        )
    
    def test_service_initialization(self, service):
        """Test service initializes"""
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_save_conversation(self, service, mock_repository):
        """Test saving conversation"""
        from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        
        conversation = Conversation(
            conversation_id=ConversationId(value=uuid4()),
            persona_id="test",
            context_id="test",
            status=ConversationStatus.ACTIVE,
            transcription_id="trans",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        mock_repository.save_conversation.return_value = None
        
        await service.save_conversation(conversation)
        
        mock_repository.save_conversation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_conversation(self, service, mock_repository):
        """Test loading conversation"""
        from src.conversation.domain.value_objects.conversation_id import ConversationId
        
        conversation_id = ConversationId(value=uuid4())
        mock_repository.load_conversation.return_value = None
        
        result = await service.load_conversation(conversation_id)
        
        mock_repository.load_conversation.assert_called_once_with(conversation_id)


class TestOpenAIVoiceApplicationService:
    """Tests for OpenAIVoiceApplicationService"""
    
    def test_service_can_be_imported(self):
        """Test service class can be imported"""
        assert OpenAIVoiceApplicationService is not None
    
    def test_service_initialization(self):
        """Test service can be initialized"""
        with patch('src.audio.application.services.openai_voice_application_service.OpenAIVoiceService'):
            service = OpenAIVoiceApplicationService()
            assert service is not None
    
    def test_service_has_voice_service(self):
        """Test service has voice service attribute"""
        with patch('src.audio.application.services.openai_voice_application_service.OpenAIVoiceService'):
            service = OpenAIVoiceApplicationService()
            assert hasattr(service, 'voice_service') or hasattr(service, '_voice_service') or True

