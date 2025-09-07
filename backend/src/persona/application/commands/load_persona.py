"""
Load persona command.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from src.persona.domain.value_objects.persona_id import PersonaId


@dataclass
class LoadPersonaCommand:
    """Command to load a persona."""
    persona_id: str
    
    def __post_init__(self):
        if not self.persona_id or not self.persona_id.strip():
            raise ValueError("Persona ID is required")


@dataclass
class LoadPersonaResult:
    """Result of loading a persona."""
    persona_id: Optional[PersonaId]
    success: bool
    message: Optional[str] = None


@dataclass
class CreatePersonaCommand:
    """Command to create a new persona."""
    name: str
    description: str
    background: str
    personality_traits: List[str]
    accent: str
    voice_id: str
    prompt_template: str
    conversation_goals: List[str]
    pain_points: List[str]
    objections: List[str]
    decision_factors: List[str]
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Name is required")
        if not self.description or not self.description.strip():
            raise ValueError("Description is required")
        if not self.background or not self.background.strip():
            raise ValueError("Background is required")
        if not self.personality_traits:
            raise ValueError("Personality traits are required")
        if not self.accent or not self.accent.strip():
            raise ValueError("Accent is required")
        if not self.voice_id or not self.voice_id.strip():
            raise ValueError("Voice ID is required")
        if not self.prompt_template or not self.prompt_template.strip():
            raise ValueError("Prompt template is required")
        if not self.conversation_goals:
            raise ValueError("Conversation goals are required")
        
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CreatePersonaResult:
    """Result of creating a persona."""
    persona_id: Optional[PersonaId]
    success: bool
    message: Optional[str] = None


@dataclass
class UpdatePersonaCommand:
    """Command to update a persona."""
    persona_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    background: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    accent: Optional[str] = None
    voice_id: Optional[str] = None
    prompt_template: Optional[str] = None
    conversation_goals: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None
    objections: Optional[List[str]] = None
    decision_factors: Optional[List[str]] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.persona_id or not self.persona_id.strip():
            raise ValueError("Persona ID is required")


@dataclass
class UpdatePersonaResult:
    """Result of updating a persona."""
    persona_id: Optional[PersonaId]
    success: bool
    message: Optional[str] = None


@dataclass
class DeletePersonaCommand:
    """Command to delete a persona."""
    persona_id: str
    
    def __post_init__(self):
        if not self.persona_id or not self.persona_id.strip():
            raise ValueError("Persona ID is required")


@dataclass
class DeletePersonaResult:
    """Result of deleting a persona."""
    success: bool
    message: Optional[str] = None
