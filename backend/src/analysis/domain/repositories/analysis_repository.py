"""
Analysis repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.analysis.domain.entities.analysis import Analysis
from src.analysis.domain.value_objects.analysis_id import AnalysisId


class AnalysisRepository(ABC):
    """Abstract repository for analysis entities."""
    
    @abstractmethod
    async def save(self, analysis: Analysis) -> None:
        """Save an analysis."""
        pass
    
    @abstractmethod
    async def get_by_id(self, analysis_id: AnalysisId) -> Optional[Analysis]:
        """Get analysis by ID."""
        pass
    
    @abstractmethod
    async def get_by_conversation_id(self, conversation_id: str) -> Optional[Analysis]:
        """Get analysis by conversation ID."""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Analysis]:
        """Get all analyses with pagination."""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str, limit: int = 100, offset: int = 0) -> List[Analysis]:
        """Get analyses by status."""
        pass
    
    @abstractmethod
    async def delete(self, analysis_id: AnalysisId) -> bool:
        """Delete an analysis."""
        pass
    
    @abstractmethod
    async def exists(self, analysis_id: AnalysisId) -> bool:
        """Check if analysis exists."""
        pass
