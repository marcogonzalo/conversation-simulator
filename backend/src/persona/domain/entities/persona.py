"""
Persona entity for the persona bounded context.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from src.shared.domain.value_objects import EntityId
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.value_objects.personality_traits import PersonalityTraits


class AccentType(Enum):
    """Accent type enumeration."""
    CARIBBEAN_SPANISH = "caribbean_spanish"  # Cuban
    PERUVIAN_SPANISH = "peruvian_spanish"
    VENEZUELAN_SPANISH = "venezuelan_spanish"
    FLORIDA_ENGLISH = "florida_english"


class Persona:
    """Persona aggregate root."""
    
    def __init__(
        self,
        persona_id: PersonaId,
        name: str,
        description: str,
        background: str,
        personality_traits: PersonalityTraits,
        accent: AccentType,
        voice_id: str,
        prompt_template: str,
        conversation_goals: List[str],
        pain_points: List[str],
        objections: List[str],
        decision_factors: List[str],
        budget_range: Optional[str] = None,
        timeline: Optional[str] = None,
        company_size: Optional[str] = None,
        industry: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._id = persona_id
        self._name = name
        self._description = description
        self._background = background
        self._personality_traits = personality_traits
        self._accent = accent
        self._voice_id = voice_id
        self._prompt_template = prompt_template
        self._conversation_goals = conversation_goals
        self._pain_points = pain_points
        self._objections = objections
        self._decision_factors = decision_factors
        self._budget_range = budget_range
        self._timeline = timeline
        self._company_size = company_size
        self._industry = industry
        self._metadata = metadata or {}
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    @property
    def id(self) -> PersonaId:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def background(self) -> str:
        return self._background
    
    @property
    def personality_traits(self) -> PersonalityTraits:
        return self._personality_traits
    
    @property
    def accent(self) -> AccentType:
        return self._accent
    
    @property
    def voice_id(self) -> str:
        return self._voice_id
    
    @property
    def prompt_template(self) -> str:
        return self._prompt_template
    
    @property
    def conversation_goals(self) -> List[str]:
        return self._conversation_goals.copy()
    
    @property
    def pain_points(self) -> List[str]:
        return self._pain_points.copy()
    
    @property
    def objections(self) -> List[str]:
        return self._objections.copy()
    
    @property
    def decision_factors(self) -> List[str]:
        return self._decision_factors.copy()
    
    @property
    def budget_range(self) -> Optional[str]:
        return self._budget_range
    
    @property
    def timeline(self) -> Optional[str]:
        return self._timeline
    
    @property
    def company_size(self) -> Optional[str]:
        return self._company_size
    
    @property
    def industry(self) -> Optional[str]:
        return self._industry
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def update_name(self, name: str) -> None:
        """Update persona name."""
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        self._name = name.strip()
        self._updated_at = datetime.utcnow()
    
    def update_description(self, description: str) -> None:
        """Update persona description."""
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        self._description = description.strip()
        self._updated_at = datetime.utcnow()
    
    def update_background(self, background: str) -> None:
        """Update persona background."""
        if not background or not background.strip():
            raise ValueError("Background cannot be empty")
        self._background = background.strip()
        self._updated_at = datetime.utcnow()
    
    def update_personality_traits(self, traits: PersonalityTraits) -> None:
        """Update personality traits."""
        self._personality_traits = traits
        self._updated_at = datetime.utcnow()
    
    def update_accent(self, accent: AccentType) -> None:
        """Update accent type."""
        self._accent = accent
        self._updated_at = datetime.utcnow()
    
    def update_voice_id(self, voice_id: str) -> None:
        """Update voice ID."""
        if not voice_id or not voice_id.strip():
            raise ValueError("Voice ID cannot be empty")
        self._voice_id = voice_id.strip()
        self._updated_at = datetime.utcnow()
    
    def update_prompt_template(self, template: str) -> None:
        """Update prompt template."""
        if not template or not template.strip():
            raise ValueError("Prompt template cannot be empty")
        self._prompt_template = template.strip()
        self._updated_at = datetime.utcnow()
    
    def add_conversation_goal(self, goal: str) -> None:
        """Add a conversation goal."""
        if goal and goal.strip() and goal not in self._conversation_goals:
            self._conversation_goals.append(goal.strip())
            self._updated_at = datetime.utcnow()
    
    def remove_conversation_goal(self, goal: str) -> None:
        """Remove a conversation goal."""
        if goal in self._conversation_goals:
            self._conversation_goals.remove(goal)
            self._updated_at = datetime.utcnow()
    
    def add_pain_point(self, pain_point: str) -> None:
        """Add a pain point."""
        if pain_point and pain_point.strip() and pain_point not in self._pain_points:
            self._pain_points.append(pain_point.strip())
            self._updated_at = datetime.utcnow()
    
    def remove_pain_point(self, pain_point: str) -> None:
        """Remove a pain point."""
        if pain_point in self._pain_points:
            self._pain_points.remove(pain_point)
            self._updated_at = datetime.utcnow()
    
    def add_objection(self, objection: str) -> None:
        """Add an objection."""
        if objection and objection.strip() and objection not in self._objections:
            self._objections.append(objection.strip())
            self._updated_at = datetime.utcnow()
    
    def remove_objection(self, objection: str) -> None:
        """Remove an objection."""
        if objection in self._objections:
            self._objections.remove(objection)
            self._updated_at = datetime.utcnow()
    
    def add_decision_factor(self, factor: str) -> None:
        """Add a decision factor."""
        if factor and factor.strip() and factor not in self._decision_factors:
            self._decision_factors.append(factor.strip())
            self._updated_at = datetime.utcnow()
    
    def remove_decision_factor(self, factor: str) -> None:
        """Remove a decision factor."""
        if factor in self._decision_factors:
            self._decision_factors.remove(factor)
            self._updated_at = datetime.utcnow()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata."""
        self._metadata[key] = value
        self._updated_at = datetime.utcnow()
    
    def is_compatible_with_accent(self, accent: AccentType) -> bool:
        """Check if persona is compatible with accent."""
        return self._accent == accent
    
    def has_trait(self, trait: str) -> bool:
        """Check if persona has a specific trait."""
        return trait in self._personality_traits.traits
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice settings for TTS."""
        return {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
