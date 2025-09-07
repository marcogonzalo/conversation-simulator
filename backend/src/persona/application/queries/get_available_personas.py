"""
Get available personas query.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.entities.persona import AccentType


@dataclass
class GetAvailablePersonasQuery:
    """Query to get all available personas."""
    accent_filter: Optional[str] = None
    trait_filter: Optional[List[str]] = None


@dataclass
class PersonaDto:
    """Persona data transfer object."""
    id: str
    name: str
    description: str
    background: str
    personality_traits: List[str]
    accent: str
    voice_id: str
    conversation_goals: List[str]
    pain_points: List[str]
    objections: List[str]
    decision_factors: List[str]
    budget_range: Optional[str]
    timeline: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class GetAvailablePersonasResult:
    """Result of getting available personas."""
    personas: List[PersonaDto]
    total_count: int
    success: bool
    message: Optional[str] = None


@dataclass
class GetPersonaByIdQuery:
    """Query to get a persona by ID."""
    persona_id: str


@dataclass
class GetPersonaByIdResult:
    """Result of getting a persona by ID."""
    persona: Optional[PersonaDto]
    success: bool
    message: Optional[str] = None


@dataclass
class GetPersonasByAccentQuery:
    """Query to get personas by accent."""
    accent: str


@dataclass
class GetPersonasByAccentResult:
    """Result of getting personas by accent."""
    personas: List[PersonaDto]
    success: bool
    message: Optional[str] = None


@dataclass
class GetPersonasByTraitsQuery:
    """Query to get personas by traits."""
    traits: List[str]


@dataclass
class GetPersonasByTraitsResult:
    """Result of getting personas by traits."""
    personas: List[PersonaDto]
    success: bool
    message: Optional[str] = None
