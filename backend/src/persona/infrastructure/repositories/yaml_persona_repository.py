"""
YAML implementation of persona repository.
"""
import yaml
import json
from typing import List, Optional
from pathlib import Path
from uuid import UUID

from src.persona.domain.entities.persona import Persona, AccentType
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.value_objects.personality_traits import PersonalityTraits, PersonalityTrait
from src.persona.domain.repositories.persona_repository import PersonaRepository


class YAMLPersonaRepository(PersonaRepository):
    """YAML implementation of persona repository."""
    
    def __init__(self, personas_dir: str = "data/personas"):
        self.personas_dir = Path(personas_dir)
        self.personas_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, persona: Persona) -> None:
        """Save a persona to YAML file."""
        persona_data = self._persona_to_dict(persona)
        persona_file = self.personas_dir / f"{persona.id.value}.yaml"
        
        with open(persona_file, 'w', encoding='utf-8') as f:
            yaml.dump(persona_data, f, default_flow_style=False, allow_unicode=True)
    
    async def get_by_id(self, persona_id: PersonaId) -> Optional[Persona]:
        """Get persona by ID."""
        persona_file = self.personas_dir / f"{persona_id.value}.yaml"
        
        if not persona_file.exists():
            return None
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = yaml.safe_load(f)
                return self._dict_to_persona(persona_data)
        except Exception as e:
            print(f"Error loading persona {persona_id.value}: {e}")
            return None
    
    async def get_all(self) -> List[Persona]:
        """Get all personas."""
        personas = []
        
        for yaml_file in self.personas_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    persona_data = yaml.safe_load(f)
                    persona = self._dict_to_persona(persona_data)
                    if persona:
                        personas.append(persona)
            except Exception as e:
                print(f"Error loading persona from {yaml_file}: {e}")
                continue
        
        return personas
    
    async def get_by_accent(self, accent: str) -> List[Persona]:
        """Get personas by accent type."""
        all_personas = await self.get_all()
        return [p for p in all_personas if p.accent.value == accent]
    
    async def get_by_traits(self, traits: List[str]) -> List[Persona]:
        """Get personas by personality traits."""
        all_personas = await self.get_all()
        return [
            p for p in all_personas 
            if any(trait in p.personality_traits.get_trait_names() for trait in traits)
        ]
    
    async def delete(self, persona_id: PersonaId) -> bool:
        """Delete a persona."""
        persona_file = self.personas_dir / f"{persona_id.value}.yaml"
        
        if persona_file.exists():
            persona_file.unlink()
            return True
        return False
    
    async def exists(self, persona_id: PersonaId) -> bool:
        """Check if persona exists."""
        persona_file = self.personas_dir / f"{persona_id.value}.yaml"
        return persona_file.exists()
    
    def _persona_to_dict(self, persona: Persona) -> dict:
        """Convert persona entity to dictionary."""
        return {
            'id': persona.id.value,
            'name': persona.name,
            'description': persona.description,
            'background': persona.background,
            'personality_traits': persona.personality_traits.get_trait_names(),
            'accent': persona.accent.value,
            'voice_id': persona.voice_id,
            'prompt_template': persona.prompt_template,
            'conversation_goals': persona.conversation_goals,
            'pain_points': persona.pain_points,
            'objections': persona.objections,
            'decision_factors': persona.decision_factors,
            'budget_range': persona.budget_range,
            'timeline': persona.timeline,
            'company_size': persona.company_size,
            'industry': persona.industry,
            'metadata': persona.metadata,
            'created_at': persona.created_at.isoformat(),
            'updated_at': persona.updated_at.isoformat()
        }
    
    def _dict_to_persona(self, data: dict) -> Optional[Persona]:
        """Convert dictionary to persona entity."""
        try:
            from datetime import datetime
            
            # Create personality traits
            personality_traits = PersonalityTraits.from_strings(data.get('personality_traits', []))
            
            # Create persona
            persona = Persona(
                persona_id=PersonaId.from_string(data['id']),
                name=data['name'],
                description=data['description'],
                background=data['background'],
                personality_traits=personality_traits,
                accent=AccentType(data['accent']),
                voice_id=data['voice_id'],
                prompt_template=data['prompt_template'],
                conversation_goals=data.get('conversation_goals', []),
                pain_points=data.get('pain_points', []),
                objections=data.get('objections', []),
                decision_factors=data.get('decision_factors', []),
                budget_range=data.get('budget_range'),
                timeline=data.get('timeline'),
                company_size=data.get('company_size'),
                industry=data.get('industry'),
                metadata=data.get('metadata', {})
            )
            
            return persona
        
        except Exception as e:
            print(f"Error converting dict to persona: {e}")
            return None
