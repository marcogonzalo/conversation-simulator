"""
Domain exceptions for the analysis bounded context.
"""
from src.shared.domain.exceptions import DomainException


class AnalysisException(DomainException):
    """Base class for analysis domain exceptions."""
    pass


class AnalysisValidationError(AnalysisException):
    """Raised when analysis validation fails."""
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Analysis validation error in field '{field}': {reason}")


class AnalysisNotFoundError(AnalysisException):
    """Raised when an analysis is not found."""
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        super().__init__(f"Analysis with ID {analysis_id} not found")


class AnalysisAlreadyExistsError(AnalysisException):
    """Raised when trying to create an analysis that already exists."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        super().__init__(f"Analysis for conversation {conversation_id} already exists")


class AnalysisInProgressError(AnalysisException):
    """Raised when trying to modify an analysis that is in progress."""
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        super().__init__(f"Analysis {analysis_id} is currently in progress")


class AnalysisCompletedError(AnalysisException):
    """Raised when trying to modify a completed analysis."""
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        super().__init__(f"Cannot modify completed analysis {analysis_id}")


class AnalysisFailedError(AnalysisException):
    """Raised when analysis processing fails."""
    
    def __init__(self, analysis_id: str, reason: str):
        self.analysis_id = analysis_id
        self.reason = reason
        super().__init__(f"Analysis {analysis_id} failed: {reason}")


class InvalidAnalysisDataError(AnalysisException):
    """Raised when analysis data is invalid."""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid analysis data: {reason}")
