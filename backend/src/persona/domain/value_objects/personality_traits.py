"""
Personality traits value object.
"""
from dataclasses import dataclass
from typing import List, Set
from enum import Enum


class PersonalityTrait(Enum):
    """Personality trait enumeration."""
    FRIENDLY = "friendly"
    SKEPTICAL = "skeptical"
    IMPATIENT = "impatient"
    ANALYTICAL = "analytical"
    EMOTIONAL = "emotional"
    PRAGMATIC = "pragmatic"
    CONSERVATIVE = "conservative"
    INNOVATIVE = "innovative"


@dataclass(frozen=True)
class PersonalityTraits:
    """Value object for personality traits."""
    traits: Set[PersonalityTrait]
    
    def __post_init__(self):
        if not self.traits:
            raise ValueError("Personality traits cannot be empty")
        
        if len(self.traits) > 10:
            raise ValueError("Too many personality traits (max 10)")
    
    def has_trait(self, trait: PersonalityTrait) -> bool:
        """Check if persona has a specific trait."""
        return trait in self.traits
    
    def has_any_trait(self, traits: List[PersonalityTrait]) -> bool:
        """Check if persona has any of the specified traits."""
        return bool(self.traits.intersection(set(traits)))
    
    def has_all_traits(self, traits: List[PersonalityTrait]) -> bool:
        """Check if persona has all of the specified traits."""
        return set(traits).issubset(self.traits)
    
    def get_trait_names(self) -> List[str]:
        """Get list of trait names."""
        return [trait.value for trait in self.traits]
    
    def is_compatible_with(self, other: 'PersonalityTraits') -> bool:
        """Check if traits are compatible with another set."""
        # Basic compatibility check - can be extended with business rules
        return len(self.traits.intersection(other.traits)) > 0
    
    def get_primary_traits(self) -> List[PersonalityTrait]:
        """Get primary traits (first 3)."""
        return list(self.traits)[:3]
    
    def get_secondary_traits(self) -> List[PersonalityTrait]:
        """Get secondary traits (remaining)."""
        return list(self.traits)[3:]
    
    @classmethod
    def from_strings(cls, trait_strings: List[str]) -> 'PersonalityTraits':
        """Create from list of string trait names."""
        traits = set()
        for trait_str in trait_strings:
            try:
                trait = PersonalityTrait(trait_str.lower())
                traits.add(trait)
            except ValueError:
                raise ValueError(f"Invalid personality trait: {trait_str}")
        
        return cls(traits)
    
    def __str__(self) -> str:
        return ", ".join(trait.value for trait in sorted(self.traits, key=lambda x: x.value))
