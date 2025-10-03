"""
Enhanced message entity with intelligent text processing capabilities.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from src.shared.domain.value_objects import MessageContent
from src.shared.domain.events import MessageAdded


class MessageType(Enum):
    """Message type enumeration."""
    TEXT = "text"
    AUDIO = "audio"
    MIXED = "mixed"  # Audio with transcription


class ProcessingStatus(Enum):
    """Processing status for messages."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TextChunk:
    """Represents a text chunk with processing metadata."""
    
    def __init__(
        self,
        content: str,
        chunk_index: int,
        timestamp: datetime,
        is_final: bool = False,
        confidence: Optional[float] = None
    ):
        self._content = content
        self._chunk_index = chunk_index
        self._timestamp = timestamp
        self._is_final = is_final
        self._confidence = confidence
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def chunk_index(self) -> int:
        return self._chunk_index
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    @property
    def is_final(self) -> bool:
        return self._is_final
    
    @property
    def confidence(self) -> Optional[float]:
        return self._confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self._content,
            'chunk_index': self._chunk_index,
            'timestamp': self._timestamp.isoformat(),
            'is_final': self._is_final,
            'confidence': self._confidence
        }


class AudioMetadata:
    """Metadata for audio content."""
    
    def __init__(
        self,
        duration_ms: Optional[int] = None,
        format: Optional[str] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        file_size_bytes: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ):
        self._duration_ms = duration_ms
        self._format = format
        self._sample_rate = sample_rate
        self._channels = channels
        self._file_size_bytes = file_size_bytes
        self._processing_time_ms = processing_time_ms
    
    @property
    def duration_ms(self) -> Optional[int]:
        return self._duration_ms
    
    @property
    def format(self) -> Optional[str]:
        return self._format
    
    @property
    def sample_rate(self) -> Optional[int]:
        return self._sample_rate
    
    @property
    def channels(self) -> Optional[int]:
        return self._channels
    
    @property
    def file_size_bytes(self) -> Optional[int]:
        return self._file_size_bytes
    
    @property
    def processing_time_ms(self) -> Optional[int]:
        return self._processing_time_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'duration_ms': self._duration_ms,
            'format': self._format,
            'sample_rate': self._sample_rate,
            'channels': self._channels,
            'file_size_bytes': self._file_size_bytes,
            'processing_time_ms': self._processing_time_ms
        }


class EnhancedMessage:
    """Enhanced message entity with intelligent text processing."""
    
    def __init__(
        self,
        message_id: UUID,
        conversation_id: UUID,
        role: str,  # 'user' or 'assistant'
        message_type: MessageType = MessageType.TEXT,
        processing_status: ProcessingStatus = ProcessingStatus.PENDING,
        timestamp: Optional[datetime] = None,
        audio_url: Optional[str] = None,
        audio_metadata: Optional[AudioMetadata] = None
    ):
        self._id = message_id
        self._conversation_id = conversation_id
        self._role = role
        self._message_type = message_type
        self._processing_status = processing_status
        self._timestamp = timestamp or datetime.utcnow()
        self._audio_url = audio_url
        self._audio_metadata = audio_metadata
        
        # Text processing fields
        self._text_chunks: List[TextChunk] = []
        self._processed_content = ""
        self._is_content_final = False
        
        # Additional metadata
        self._metadata: Dict[str, Any] = {}
        self._domain_events: List = []
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def conversation_id(self) -> UUID:
        return self._conversation_id
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def message_type(self) -> MessageType:
        return self._message_type
    
    @property
    def processing_status(self) -> ProcessingStatus:
        return self._processing_status
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    @property
    def audio_url(self) -> Optional[str]:
        return self._audio_url
    
    @property
    def audio_metadata(self) -> Optional[AudioMetadata]:
        return self._audio_metadata
    
    @property
    def text_chunks(self) -> List[TextChunk]:
        return self._text_chunks.copy()
    
    @property
    def processed_content(self) -> str:
        return self._processed_content
    
    @property
    def is_content_final(self) -> bool:
        return self._is_content_final
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    @property
    def domain_events(self) -> List:
        return self._domain_events.copy()
    
    def add_text_chunk(self, content: str, is_final: bool = False, confidence: Optional[float] = None) -> None:
        """Add a text chunk and update processed content."""
        chunk = TextChunk(
            content=content,
            chunk_index=len(self._text_chunks),
            timestamp=datetime.utcnow(),
            is_final=is_final,
            confidence=confidence
        )
        
        self._text_chunks.append(chunk)
        self._processed_content = self._process_text_chunks()
        
        if is_final:
            self._is_content_final = True
            self._processing_status = ProcessingStatus.COMPLETED
        
        # Add domain event for new chunk
        self._domain_events.append(
            MessageAdded(
                conversation_id=self._conversation_id,
                message_id=self._id,
                role=self._role,
                content=self._processed_content
            )
        )
    
    def set_processed_content(self, content: str, is_final: bool = True) -> None:
        """Set the final processed content."""
        self._processed_content = content
        self._is_content_final = is_final
        
        if is_final:
            self._processing_status = ProcessingStatus.COMPLETED
    
    def add_audio_url(self, audio_url: str, metadata: Optional[AudioMetadata] = None) -> None:
        """Add audio URL and metadata."""
        self._audio_url = audio_url
        if metadata:
            self._audio_metadata = metadata
        
        if self._message_type == MessageType.TEXT:
            self._message_type = MessageType.MIXED
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update message metadata."""
        self._metadata[key] = value
    
    def set_processing_status(self, status: ProcessingStatus) -> None:
        """Update processing status."""
        self._processing_status = status
    
    def is_user_message(self) -> bool:
        """Check if message is from user."""
        return self._role == "user"
    
    def is_assistant_message(self) -> bool:
        """Check if message is from assistant."""
        return self._role == "assistant"
    
    def has_audio(self) -> bool:
        """Check if message has audio."""
        return self._audio_url is not None
    
    def has_final_content(self) -> bool:
        """Check if message has final processed content."""
        return self._is_content_final
    
    def get_display_content(self) -> str:
        """Get content for display (processed content or raw chunks)."""
        if self._processed_content:
            return self._processed_content
        
        # Fallback to concatenated chunks
        return "".join(chunk.content for chunk in self._text_chunks)
    
    def _process_text_chunks(self) -> str:
        """Process text chunks using intelligent concatenation logic."""
        if not self._text_chunks:
            return ""
        
        # Sort chunks by index to ensure correct order
        sorted_chunks = sorted(self._text_chunks, key=lambda c: c.chunk_index)
        
        # Start with first chunk
        result = sorted_chunks[0].content
        
        # Process remaining chunks with intelligent concatenation
        for chunk in sorted_chunks[1:]:
            result = self._concatenate_text(result, chunk.content)
        
        return result
    
    def _concatenate_text(self, current: str, new_chunk: str) -> str:
        """Intelligent text concatenation similar to frontend logic."""
        current_trimmed = current.strip()
        new_trimmed = new_chunk.strip()
        
        if not current_trimmed:
            return new_trimmed
        if not new_trimmed:
            return current
        
        # Check if new chunk starts with space
        if new_chunk.startswith(' '):
            return current + new_chunk
        
        # Check for numbers and currency
        if new_trimmed.isdigit():
            last_char = current_trimmed[-1] if current_trimmed else ''
            if last_char in '$€£¥,':
                return current + new_chunk
            else:
                return current + ' ' + new_chunk
        
        # Check for currency symbols
        if new_trimmed.startswith(('$', '€', '£', '¥')):
            return current + new_chunk
        
        # Check for decimal separators
        if new_trimmed.startswith(('.', ',')):
            return current + new_chunk
        
        # Check for punctuation that should be attached
        if new_trimmed and new_trimmed[0] in '.,!?;:()"':
            return current + new_chunk
        
        # Check if current ends with space or new chunk starts with space
        if current.endswith(' ') or new_chunk.startswith(' '):
            return current + new_chunk
        
        # Default: concatenate without space (word continuation)
        return current + new_chunk
    
    def clear_domain_events(self):
        """Clear domain events after they've been processed."""
        self._domain_events.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': str(self._id),
            'conversation_id': str(self._conversation_id),
            'role': self._role,
            'message_type': self._message_type.value,
            'processing_status': self._processing_status.value,
            'timestamp': self._timestamp.isoformat(),
            'audio_url': self._audio_url,
            'audio_metadata': self._audio_metadata.to_dict() if self._audio_metadata else None,
            'text_chunks': [chunk.to_dict() for chunk in self._text_chunks],
            'processed_content': self._processed_content,
            'is_content_final': self._is_content_final,
            'metadata': self._metadata
        }
    
    @classmethod
    def create_user_message(
        cls,
        conversation_id: UUID,
        content: str = "",
        message_type: MessageType = MessageType.TEXT,
        audio_url: Optional[str] = None,
        audio_metadata: Optional[AudioMetadata] = None
    ) -> 'EnhancedMessage':
        """Create a user message."""
        message = cls(
            message_id=uuid4(),
            conversation_id=conversation_id,
            role="user",
            message_type=message_type,
            audio_url=audio_url,
            audio_metadata=audio_metadata
        )
        
        if content:
            message.set_processed_content(content, is_final=True)
        
        return message
    
    @classmethod
    def create_assistant_message(
        cls,
        conversation_id: UUID,
        content: str = "",
        message_type: MessageType = MessageType.TEXT,
        audio_url: Optional[str] = None,
        audio_metadata: Optional[AudioMetadata] = None
    ) -> 'EnhancedMessage':
        """Create an assistant message."""
        message = cls(
            message_id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            message_type=message_type,
            audio_url=audio_url,
            audio_metadata=audio_metadata
        )
        
        if content:
            message.set_processed_content(content, is_final=True)
        
        return message
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedMessage':
        """Create message from dictionary."""
        message = cls(
            message_id=UUID(data['id']),
            conversation_id=UUID(data['conversation_id']),
            role=data['role'],
            message_type=MessageType(data['message_type']),
            processing_status=ProcessingStatus(data['processing_status']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            audio_url=data.get('audio_url'),
            audio_metadata=AudioMetadata(**data['audio_metadata']) if data.get('audio_metadata') else None
        )
        
        # Restore text chunks
        for chunk_data in data.get('text_chunks', []):
            chunk = TextChunk(
                content=chunk_data['content'],
                chunk_index=chunk_data['chunk_index'],
                timestamp=datetime.fromisoformat(chunk_data['timestamp']),
                is_final=chunk_data['is_final'],
                confidence=chunk_data.get('confidence')
            )
            message._text_chunks.append(chunk)
        
        # Set processed content
        message._processed_content = data.get('processed_content', '')
        message._is_content_final = data.get('is_content_final', False)
        message._metadata = data.get('metadata', {})
        
        return message
