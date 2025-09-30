"""
Persona adapter for converting between new format and legacy entity format.
"""

from typing import Dict, Any, Optional
from src.persona.domain.entities.persona import Persona, AccentType
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.value_objects.personality_traits import PersonalityTraits
from datetime import datetime


class PersonaAdapter:
    """Adapter for converting between new persona format and legacy entity format."""
    
    @staticmethod
    def new_format_to_legacy_entity(data: Dict[str, Any]) -> Optional[Persona]:
        """Convert new persona format to legacy Persona entity."""
        try:
            # Extract data from new format
            identity = data.get('identity', {})
            personality = data.get('personality', {})
            communication = data.get('communication', {})
            knowledge = data.get('knowledge', {})
            
            # Map new format to legacy format
            legacy_data = {
                'id': data.get('id'),
                'name': data.get('name'),
                'description': data.get('description'),
                'background': f"{identity.get('role', '')} - {identity.get('experience', '')}",
                'personality_traits': personality.get('traits', []),
                'accent': PersonaAdapter._map_accent(communication.get('accent', 'neutral')),
                'voice_id': identity.get('voice_id', ''),
                'prompt_template': PersonaAdapter._build_prompt_template(data),
                'conversation_goals': PersonaAdapter._extract_conversation_goals(data),
                'pain_points': PersonaAdapter._extract_pain_points(data),
                'objections': PersonaAdapter._extract_objections(data),
                'decision_factors': PersonaAdapter._extract_decision_factors(data),
                'budget_range': None,  # Not in new format
                'timeline': None,  # Not in new format
                'company_size': identity.get('company_size'),
                'industry': None,  # Not in new format
                'metadata': {
                    'age': identity.get('age'),
                    'nationality': identity.get('nationality'),
                    'team_size': identity.get('team_size'),
                    'experience_level': knowledge.get('experience_level'),
                    'decision_authority': knowledge.get('decision_authority'),
                    'risk_tolerance': personality.get('risk_tolerance'),
                    'enthusiasm_level': personality.get('enthusiasm_level'),
                    'decision_style': personality.get('decision_style'),
                    'learning_preference': personality.get('learning_preference'),
                    'response_length': communication.get('response_length'),
                    'formality': communication.get('formality'),
                    'question_style': communication.get('question_style'),
                    'energy_level': communication.get('energy_level'),
                    'domain_expertise': knowledge.get('domain_expertise'),
                    'technical_comfort': knowledge.get('technical_comfort')
                }
            }
            
            # Create personality traits
            personality_traits = PersonalityTraits.from_strings(legacy_data['personality_traits'])
            
            # Create persona entity
            persona = Persona(
                persona_id=PersonaId.from_string(legacy_data['id']),
                name=legacy_data['name'],
                description=legacy_data['description'],
                background=legacy_data['background'],
                personality_traits=personality_traits,
                accent=AccentType(legacy_data['accent']),
                voice_id=legacy_data['voice_id'],
                prompt_template=legacy_data['prompt_template'],
                conversation_goals=legacy_data['conversation_goals'],
                pain_points=legacy_data['pain_points'],
                objections=legacy_data['objections'],
                decision_factors=legacy_data['decision_factors'],
                budget_range=legacy_data['budget_range'],
                timeline=legacy_data['timeline'],
                company_size=legacy_data['company_size'],
                industry=legacy_data['industry'],
                metadata=legacy_data['metadata']
            )
            
            return persona
            
        except Exception as e:
            print(f"Error converting new format to legacy entity: {e}")
            return None
    
    @staticmethod
    def _build_prompt_template(data: Dict[str, Any]) -> str:
        """Build prompt template from new format data."""
        name = data.get('name', 'Assistant')
        description = data.get('description', '')
        characteristics = data.get('characteristics', [])
        behavior = data.get('behavior', [])
        instructions = data.get('instructions', [])
        
        template_parts = [
            f"Eres {name}, {description}",
            "",
            "CARACTERÍSTICAS:"
        ]
        
        for char in characteristics:
            template_parts.append(f"- {char}")
        
        template_parts.extend(["", "COMPORTAMIENTO:"])
        
        for beh in behavior:
            template_parts.append(f"- {beh}")
        
        template_parts.extend(["", "INSTRUCCIONES:"])
        
        for instruction in instructions:
            template_parts.append(f"- {instruction}")
        
        return "\n".join(template_parts)
    
    @staticmethod
    def _extract_conversation_goals(data: Dict[str, Any]) -> list:
        """Extract conversation goals from new format."""
        # For now, return empty list as goals are not in the new format
        # This could be extended if needed
        return []
    
    @staticmethod
    def _extract_pain_points(data: Dict[str, Any]) -> list:
        """Extract pain points from new format."""
        # For now, return empty list as pain points are not in the new format
        # This could be extended if needed
        return []
    
    @staticmethod
    def _extract_objections(data: Dict[str, Any]) -> list:
        """Extract objections from new format."""
        # For now, return empty list as objections are not in the new format
        # This could be extended if needed
        return []
    
    @staticmethod
    def _extract_decision_factors(data: Dict[str, Any]) -> list:
        """Extract decision factors from new format."""
        # For now, return empty list as decision factors are not in the new format
        # This could be extended if needed
        return []
    
    @staticmethod
    def _map_accent(accent: str) -> str:
        """Map new format accent to legacy AccentType value."""
        accent_mapping = {
            'venezolano': 'venezuelan_spanish',
            'peruano': 'peruvian_spanish', 
            'cubano': 'caribbean_spanish',
            'mexicano': 'caribbean_spanish',  # Map Mexican to Caribbean as closest
            'neutral': 'caribbean_spanish'    # Default fallback
        }
        return accent_mapping.get(accent.lower(), 'caribbean_spanish')
