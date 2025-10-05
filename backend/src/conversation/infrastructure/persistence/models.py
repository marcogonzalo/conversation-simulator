"""
Database models for conversation domain.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

# Create base for conversation domain
Base = declarative_base()


class ConversationModel(Base):
    """Conversation model - Main aggregate root.
    References to Transcription, Analysis, Persona, and Context are file IDs.
    """
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True)  # ConversationId
    persona_id = Column(String(255), nullable=False)  # Reference to persona file
    context_id = Column(String(255), nullable=False)  # Reference to context file
    status = Column(String(50), nullable=False, default="created")  # ConversationStatus
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    transcription_id = Column(String(36), nullable=True)  # Reference to transcription file
    analysis_id = Column(String(36), nullable=True)  # Reference to analysis file
    conversation_metadata = Column(Text, nullable=True)  # JSON metadata
