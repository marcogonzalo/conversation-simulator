"""
Persona loader service for infrastructure layer.
"""
import yaml
from typing import List, Dict, Any
from pathlib import Path
from uuid import UUID

from src.persona.domain.entities.persona import Persona, AccentType
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.value_objects.personality_traits import PersonalityTraits
from src.persona.domain.exceptions import PersonaConfigurationError


class PersonaLoaderService:
    """Service for loading personas from YAML configuration files."""
    
    def __init__(self, personas_dir: str = "config/persona_details"):
        self.personas_dir = Path(personas_dir)
        self.personas_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_personas_from_yaml(self) -> List[Persona]:
        """Load all personas from YAML files."""
        personas = []
        
        for yaml_file in self.personas_dir.glob("*.yaml"):
            try:
                persona = await self._load_persona_from_file(yaml_file)
                if persona:
                    personas.append(persona)
            except Exception as e:
                print(f"Error loading persona from {yaml_file}: {e}")
                continue
        
        return personas
    
    async def load_persona_from_file(self, file_path: str) -> Persona:
        """Load a specific persona from a YAML file."""
        yaml_file = Path(file_path)
        if not yaml_file.exists():
            raise PersonaConfigurationError(f"Persona file not found: {file_path}")
        
        return await self._load_persona_from_file(yaml_file)
    
    async def _load_persona_from_file(self, yaml_file: Path) -> Persona:
        """Load persona from YAML file."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return self._create_persona_from_data(data)
        
        except Exception as e:
            raise PersonaConfigurationError(f"Error loading persona from {yaml_file}: {e}")
    
    def _create_persona_from_data(self, data: Dict[str, Any]) -> Persona:
        """Create persona entity from YAML data."""
        try:
            # Validate required fields
            required_fields = ['id', 'name', 'description', 'background', 'personality_traits', 
                             'accent', 'voice_id', 'prompt_template', 'conversation_goals']
            
            for field in required_fields:
                if field not in data:
                    raise PersonaConfigurationError(f"Missing required field: {field}")
            
            # Create personality traits
            personality_traits = PersonalityTraits.from_strings(data['personality_traits'])
            
            # Create persona
            persona = Persona(
                persona_id=PersonaId(UUID(data['id'])),
                name=data['name'],
                description=data['description'],
                background=data['background'],
                personality_traits=personality_traits,
                accent=AccentType(data['accent']),
                voice_id=data['voice_id'],
                prompt_template=data['prompt_template'],
                conversation_goals=data['conversation_goals'],
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
            raise PersonaConfigurationError(f"Error creating persona from data: {e}")
    
    async def validate_persona_file(self, file_path: str) -> bool:
        """Validate a persona YAML file."""
        try:
            yaml_file = Path(file_path)
            if not yaml_file.exists():
                return False
            
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ['id', 'name', 'description', 'background', 'personality_traits', 
                             'accent', 'voice_id', 'prompt_template', 'conversation_goals']
            
            for field in required_fields:
                if field not in data:
                    return False
            
            # Validate accent
            try:
                AccentType(data['accent'])
            except ValueError:
                return False
            
            # Validate personality traits
            try:
                PersonalityTraits.from_strings(data['personality_traits'])
            except ValueError:
                return False
            
            return True
        
        except Exception:
            return False
    
    async def get_persona_file_paths(self) -> List[str]:
        """Get all persona YAML file paths."""
        yaml_files = list(self.personas_dir.glob("*.yaml"))
        return [str(f) for f in yaml_files]
    
    async def create_persona_from_template(
        self,
        template_data: Dict[str, Any],
        persona_id: str,
        name: str
    ) -> Persona:
        """Create a persona from a template."""
        try:
            # Merge template with specific data
            persona_data = template_data.copy()
            persona_data['id'] = persona_id
            persona_data['name'] = name
            
            return self._create_persona_from_data(persona_data)
        
        except Exception as e:
            raise PersonaConfigurationError(f"Error creating persona from template: {e}")
    
    async def export_persona_to_yaml(self, persona: Persona, file_path: str) -> None:
        """Export persona to YAML file."""
        try:
            yaml_file = Path(file_path)
            yaml_file.parent.mkdir(parents=True, exist_ok=True)
            
            persona_data = {
                'id': str(persona.id.value),
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
                'metadata': persona.metadata
            }
            
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(persona_data, f, default_flow_style=False, allow_unicode=True)
        
        except Exception as e:
            raise PersonaConfigurationError(f"Error exporting persona to YAML: {e}")
