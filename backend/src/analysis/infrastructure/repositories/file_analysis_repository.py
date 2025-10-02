"""
File-based analysis repository for storing conversation analyses.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid

logger = logging.getLogger(__name__)


class FileAnalysisRepository:
    """Repository for storing and retrieving conversation analyses from files."""
    
    def __init__(self, base_path: str = "/app/data/analyses"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_analysis(self, conversation_id: str, analysis_data: Dict[str, Any]) -> str:
        """Save analysis to file and return analysis ID."""
        try:
            # Generate unique analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Prepare analysis document
            analysis_doc = {
                "analysis_id": analysis_id,
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow().isoformat(),
                "analysis": analysis_data.get("analysis", ""),
                "metadata": {
                    "duration_seconds": analysis_data.get("duration_seconds", 0),
                    "persona_name": analysis_data.get("persona_name", "Cliente"),
                    "message_count": len(analysis_data.get("messages", [])),
                    "conversation_metadata": analysis_data.get("metadata", {})
                }
            }
            
            # Save to file
            file_path = self.base_path / f"{analysis_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_doc, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analysis saved: {analysis_id} for conversation {conversation_id}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by ID."""
        try:
            file_path = self.base_path / f"{analysis_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading analysis {analysis_id}: {e}")
            return None
    
    async def get_analyses_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all analyses for a conversation."""
        try:
            analyses = []
            for file_path in self.base_path.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                    if analysis.get("conversation_id") == conversation_id:
                        analyses.append(analysis)
            
            # Sort by creation date (newest first)
            analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return analyses
            
        except Exception as e:
            logger.error(f"Error loading analyses for conversation {conversation_id}: {e}")
            return []
    
    async def list_analyses(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all analyses with pagination."""
        try:
            analyses = []
            for file_path in self.base_path.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                    # Only include summary info for listing
                    analyses.append({
                        "analysis_id": analysis.get("analysis_id"),
                        "conversation_id": analysis.get("conversation_id"),
                        "created_at": analysis.get("created_at"),
                        "persona_name": analysis.get("metadata", {}).get("persona_name", "Cliente"),
                        "duration_seconds": analysis.get("metadata", {}).get("duration_seconds", 0),
                        "message_count": analysis.get("metadata", {}).get("message_count", 0)
                    })
            
            # Sort by creation date (newest first)
            analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Apply pagination
            return analyses[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error listing analyses: {e}")
            return []
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis by ID."""
        try:
            file_path = self.base_path / f"{analysis_id}.json"
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Analysis deleted: {analysis_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting analysis {analysis_id}: {e}")
            return False
