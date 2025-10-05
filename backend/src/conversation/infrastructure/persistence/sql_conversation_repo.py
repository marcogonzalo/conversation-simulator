"""
SQL implementation of conversation repository.
This is an ADAPTER in Hexagonal Architecture - it implements the port interface.
"""
import json
import logging
from typing import List, Optional
from uuid import UUID

from src.conversation.domain.entities.conversation import Conversation, ConversationStatus
from src.conversation.domain.value_objects.conversation_id import ConversationId
from src.conversation.domain.ports.conversation_repository import IConversationRepository
from src.conversation.infrastructure.persistence.models import ConversationModel
from src.shared.infrastructure.database.database_config import db_config

logger = logging.getLogger(__name__)


class SQLConversationRepository(IConversationRepository):
    """SQL implementation of conversation repository.
    
    This is an ADAPTER - it implements the port interface and handles
    the mapping between domain entities and database models.
    """
    
    def __init__(self):
        self.db_config = db_config
    
    async def save(self, conversation: Conversation) -> None:
        """Save a conversation."""
        try:
            with self.db_config.get_session() as session:
                # Check if conversation exists
                existing = session.query(ConversationModel).filter(
                    ConversationModel.id == str(conversation.id.value)
                ).first()
                
                if existing:
                    # Update existing conversation
                    existing.persona_id = conversation.persona_id
                    existing.context_id = conversation.context_id
                    existing.status = conversation.status.value
                    existing.completed_at = conversation.completed_at
                    existing.transcription_id = conversation.transcription_id
                    existing.analysis_id = conversation.analysis_id
                    existing.conversation_metadata = json.dumps(conversation.metadata) if conversation.metadata else None
                else:
                    # Create new conversation
                    conversation_model = ConversationModel(
                        id=str(conversation.id.value),
                        persona_id=conversation.persona_id,
                        context_id=conversation.context_id,
                        status=conversation.status.value,
                        created_at=conversation.created_at,
                        completed_at=conversation.completed_at,
                        transcription_id=conversation.transcription_id,
                        analysis_id=conversation.analysis_id,
                        conversation_metadata=json.dumps(conversation.metadata) if conversation.metadata else None
                    )
                    session.add(conversation_model)
                
                session.commit()
                logger.info(f"Conversation {str(conversation.id.value)} saved successfully")
                
        except Exception as e:
            logger.error(f"Failed to save conversation {str(conversation.id.value)}: {e}")
            raise
    
    async def get_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """Get conversation by ID."""
        try:
            with self.db_config.get_session() as session:
                conversation_model = session.query(ConversationModel).filter(
                    ConversationModel.id == str(conversation_id.value)
                ).first()
                
                if not conversation_model:
                    return None
                
                return self._model_to_entity(conversation_model)
                
        except Exception as e:
            logger.error(f"Failed to get conversation {str(conversation_id.value)}: {e}")
            raise
    
    async def get_by_persona_id(
        self, 
        persona_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Conversation]:
        """Get conversations by persona ID with pagination."""
        try:
            with self.db_config.get_session() as session:
                conversation_models = session.query(ConversationModel).filter(
                    ConversationModel.persona_id == persona_id
                ).order_by(ConversationModel.created_at.desc()).offset(offset).limit(limit).all()
                
                return [self._model_to_entity(model) for model in conversation_models]
                
        except Exception as e:
            logger.error(f"Failed to get conversations for persona {persona_id}: {e}")
            raise
    
    async def get_all(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Conversation]:
        """Get all conversations with pagination."""
        try:
            with self.db_config.get_session() as session:
                conversation_models = session.query(ConversationModel).order_by(
                    ConversationModel.created_at.desc()
                ).offset(offset).limit(limit).all()
                
                return [self._model_to_entity(model) for model in conversation_models]
                
        except Exception as e:
            logger.error(f"Failed to get all conversations: {e}")
            raise
    
    async def delete(self, conversation_id: ConversationId) -> bool:
        """Delete a conversation."""
        try:
            with self.db_config.get_session() as session:
                deleted_count = session.query(ConversationModel).filter(
                    ConversationModel.id == str(conversation_id.value)
                ).delete()
                
                session.commit()
                success = deleted_count > 0
                
                if success:
                    logger.info(f"Conversation {str(conversation_id.value)} deleted successfully")
                else:
                    logger.warning(f"Conversation {str(conversation_id.value)} not found for deletion")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete conversation {str(conversation_id.value)}: {e}")
            raise
    
    async def exists(self, conversation_id: ConversationId) -> bool:
        """Check if conversation exists."""
        try:
            with self.db_config.get_session() as session:
                count = session.query(ConversationModel).filter(
                    ConversationModel.id == str(conversation_id.value)
                ).count()
                
                return count > 0
                
        except Exception as e:
            logger.error(f"Failed to check if conversation {str(conversation_id.value)} exists: {e}")
            raise
    
    async def update_status(
        self, 
        conversation_id: ConversationId, 
        status: str,
        transcription_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> bool:
        """Update conversation status and related fields."""
        try:
            with self.db_config.get_session() as session:
                conversation_model = session.query(ConversationModel).filter(
                    ConversationModel.id == str(conversation_id.value)
                ).first()
                
                if not conversation_model:
                    return False
                
                conversation_model.status = status
                
                if transcription_id:
                    conversation_model.transcription_id = transcription_id
                
                if analysis_id:
                    conversation_model.analysis_id = analysis_id
                
                if status == ConversationStatus.COMPLETED.value:
                    from datetime import datetime
                    conversation_model.completed_at = datetime.utcnow()
                
                if metadata:
                    current_metadata = json.loads(conversation_model.conversation_metadata) if conversation_model.conversation_metadata else {}
                    current_metadata.update(metadata)
                    conversation_model.conversation_metadata = json.dumps(current_metadata)
                
                session.commit()
                logger.info(f"Conversation {str(conversation_id.value)} updated successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update conversation {str(conversation_id.value)}: {e}")
            raise
    
    def _model_to_entity(self, conversation_model: ConversationModel) -> Conversation:
        """Convert ConversationModel to domain entity."""
        try:
            return Conversation(
                conversation_id=ConversationId(value=UUID(conversation_model.id)),
                persona_id=conversation_model.persona_id,
                context_id=conversation_model.context_id,
                status=ConversationStatus(conversation_model.status),
                created_at=conversation_model.created_at,
                completed_at=conversation_model.completed_at,
                transcription_id=conversation_model.transcription_id,
                analysis_id=conversation_model.analysis_id,
                metadata=json.loads(conversation_model.conversation_metadata) if conversation_model.conversation_metadata else {}
            )
        except Exception as e:
            logger.error(f"Failed to convert model to domain entity: {e}")
            raise
