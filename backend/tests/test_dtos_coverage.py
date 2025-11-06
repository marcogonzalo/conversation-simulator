"""
Tests for DTOs to improve coverage
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.conversation.application.dtos.conversation_dto import ConversationDTO


class TestConversationDTO:
    """Tests for ConversationDTO"""
    
    def test_dto_creation(self):
        """Test DTO creation"""
        dto = ConversationDTO(
            id=str(uuid4()),
            persona_id="test_persona",
            context_id="test_context",
            status="active",
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        assert dto is not None
        assert dto.persona_id == "test_persona"
    
    def test_dto_id_is_string(self):
        """Test DTO ID is string"""
        dto = ConversationDTO(
            id="test_id_123",
            persona_id="persona1",
            context_id="context1",
            status="active",
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        assert isinstance(dto.id, str)
        assert dto.id == "test_id_123"
    
    def test_dto_status(self):
        """Test DTO status field"""
        dto = ConversationDTO(
            id=str(uuid4()),
            persona_id="persona1",
            context_id="context1",
            status="completed",
            transcription_id="trans1",
            analysis_id="analysis1",
            metadata={},
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        assert dto.status == "completed"
    
    def test_dto_with_metadata(self):
        """Test DTO with metadata"""
        metadata = {"key": "value", "number": 42}
        dto = ConversationDTO(
            id=str(uuid4()),
            persona_id="persona1",
            context_id="context1",
            status="active",
            transcription_id="trans1",
            analysis_id=None,
            metadata=metadata,
            created_at=datetime.now(),
            completed_at=None
        )
        
        assert dto.metadata == metadata
    
    def test_dto_timestamps(self):
        """Test DTO timestamp fields"""
        created = datetime.now()
        dto = ConversationDTO(
            id=str(uuid4()),
            persona_id="persona1",
            context_id="context1",
            status="active",
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=created,
            completed_at=None
        )
        
        assert dto.created_at == created
        assert dto.completed_at is None
    
    def test_dto_with_analysis_id(self):
        """Test DTO with analysis ID"""
        dto = ConversationDTO(
            id=str(uuid4()),
            persona_id="persona1",
            context_id="context1",
            status="completed",
            transcription_id="trans1",
            analysis_id="analysis_123",
            metadata={},
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        assert dto.analysis_id == "analysis_123"
    
    def test_dto_fields_accessible(self):
        """Test all DTO fields are accessible"""
        dto = ConversationDTO(
            id="id1",
            persona_id="persona1",
            context_id="context1",
            status="active",
            transcription_id="trans1",
            analysis_id=None,
            metadata={},
            created_at=datetime.now(),
            completed_at=None
        )
        
        # All fields should be accessible
        assert dto.id is not None
        assert dto.persona_id is not None
        assert dto.context_id is not None
        assert dto.status is not None
        assert dto.transcription_id is not None
        assert dto.metadata is not None
        assert dto.created_at is not None

