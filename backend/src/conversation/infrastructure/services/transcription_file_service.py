"""
Transcription file service for managing transcription files.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class TranscriptionFileService:
    """Service for managing transcription files."""
    
    def __init__(self, conversations_dir: str = "data/conversations"):
        self.conversations_dir = Path(conversations_dir)
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_transcription(
        self,
        conversation_id: str,
        transcription_id: str,
        messages: List[Dict[str, Any]],
        persona_id: str,
        context_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save transcription to file.
        
        Args:
            conversation_id: The conversation ID
            transcription_id: The transcription file ID
            messages: List of message dictionaries
            persona_id: The persona ID
            context_id: The context ID
            metadata: Optional metadata
            
        Returns:
            The path to the saved transcription file
        """
        try:
            # Create transcription data structure
            transcription_data = {
                "transcription_id": transcription_id,
                "conversation_id": conversation_id,
                "persona_id": persona_id,
                "context_id": context_id,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "messages": messages,
                "metadata": metadata or {},
                "message_count": len(messages),
                "duration_seconds": self._calculate_duration(messages)
            }
            
            # Save to file
            transcription_file = self.conversations_dir / f"{transcription_id}.json"
            
            with open(transcription_file, 'w', encoding='utf-8') as f:
                json.dump(transcription_data, f, default=str, indent=2)
            
            logger.info(f"Transcription saved to file: {transcription_file}")
            return str(transcription_file)
            
        except Exception as e:
            logger.error(f"Failed to save transcription {transcription_id}: {e}")
            raise
    
    async def get_transcription(self, transcription_id: str) -> Optional[Dict[str, Any]]:
        """
        Get transcription from file.
        
        Args:
            transcription_id: The transcription file ID
            
        Returns:
            The transcription data or None if not found
        """
        try:
            transcription_file = self.conversations_dir / f"{transcription_id}.json"
            
            if not transcription_file.exists():
                return None
            
            with open(transcription_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to get transcription {transcription_id}: {e}")
            return None
    
    async def list_transcriptions(self) -> List[str]:
        """
        List all transcription file IDs.
        
        Returns:
            List of transcription IDs
        """
        try:
            transcription_files = list(self.conversations_dir.glob("*.json"))
            return [f.stem for f in transcription_files]
            
        except Exception as e:
            logger.error(f"Failed to list transcriptions: {e}")
            return []
    
    def _calculate_duration(self, messages: List[Dict[str, Any]]) -> Optional[int]:
        """Calculate conversation duration from messages."""
        if not messages:
            return None
        
        try:
            timestamps = []
            for message in messages:
                if 'timestamp' in message:
                    if isinstance(message['timestamp'], str):
                        timestamp = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                    else:
                        timestamp = message['timestamp']
                    timestamps.append(timestamp)
            
            if len(timestamps) >= 2:
                duration = (max(timestamps) - min(timestamps)).total_seconds()
                return int(duration)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to calculate duration: {e}")
            return None


