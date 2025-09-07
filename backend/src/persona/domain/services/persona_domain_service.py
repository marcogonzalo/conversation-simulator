"""
Persona domain service.
"""
from typing import List, Optional
from src.persona.domain.entities.persona import Persona, AccentType
from src.persona.domain.value_objects.personality_traits import PersonalityTrait, PersonalityTraits
from src.persona.domain.exceptions import PersonaValidationError


class PersonaDomainService:
    """Domain service for persona business logic."""
    
    def validate_persona_data(
        self,
        name: str,
        description: str,
        background: str,
        voice_id: str,
        prompt_template: str
    ) -> bool:
        """Validate persona data."""
        if not name or not name.strip():
            raise PersonaValidationError("name", "Name cannot be empty")
        
        if not description or not description.strip():
            raise PersonaValidationError("description", "Description cannot be empty")
        
        if not background or not background.strip():
            raise PersonaValidationError("background", "Background cannot be empty")
        
        if not voice_id or not voice_id.strip():
            raise PersonaValidationError("voice_id", "Voice ID cannot be empty")
        
        if not prompt_template or not prompt_template.strip():
            raise PersonaValidationError("prompt_template", "Prompt template cannot be empty")
        
        if len(name) > 100:
            raise PersonaValidationError("name", "Name too long (max 100 characters)")
        
        if len(description) > 500:
            raise PersonaValidationError("description", "Description too long (max 500 characters)")
        
        if len(background) > 2000:
            raise PersonaValidationError("background", "Background too long (max 2000 characters)")
        
        if len(prompt_template) > 10000:
            raise PersonaValidationError("prompt_template", "Prompt template too long (max 10000 characters)")
        
        return True
    
    def validate_personality_traits(self, traits: List[str]) -> PersonalityTraits:
        """Validate and create personality traits."""
        if not traits:
            raise PersonaValidationError("personality_traits", "At least one personality trait is required")
        
        if len(traits) > 10:
            raise PersonaValidationError("personality_traits", "Too many personality traits (max 10)")
        
        try:
            return PersonalityTraits.from_strings(traits)
        except ValueError as e:
            raise PersonaValidationError("personality_traits", str(e))
    
    def validate_conversation_goals(self, goals: List[str]) -> List[str]:
        """Validate conversation goals."""
        if not goals:
            raise PersonaValidationError("conversation_goals", "At least one conversation goal is required")
        
        if len(goals) > 20:
            raise PersonaValidationError("conversation_goals", "Too many conversation goals (max 20)")
        
        validated_goals = []
        for goal in goals:
            if not goal or not goal.strip():
                continue
            if len(goal.strip()) > 200:
                raise PersonaValidationError("conversation_goals", f"Goal too long: {goal[:50]}...")
            validated_goals.append(goal.strip())
        
        if not validated_goals:
            raise PersonaValidationError("conversation_goals", "No valid conversation goals provided")
        
        return validated_goals
    
    def validate_pain_points(self, pain_points: List[str]) -> List[str]:
        """Validate pain points."""
        if not pain_points:
            return []
        
        if len(pain_points) > 15:
            raise PersonaValidationError("pain_points", "Too many pain points (max 15)")
        
        validated_points = []
        for point in pain_points:
            if not point or not point.strip():
                continue
            if len(point.strip()) > 200:
                raise PersonaValidationError("pain_points", f"Pain point too long: {point[:50]}...")
            validated_points.append(point.strip())
        
        return validated_points
    
    def validate_objections(self, objections: List[str]) -> List[str]:
        """Validate objections."""
        if not objections:
            return []
        
        if len(objections) > 15:
            raise PersonaValidationError("objections", "Too many objections (max 15)")
        
        validated_objections = []
        for objection in objections:
            if not objection or not objection.strip():
                continue
            if len(objection.strip()) > 200:
                raise PersonaValidationError("objections", f"Objection too long: {objection[:50]}...")
            validated_objections.append(objection.strip())
        
        return validated_objections
    
    def validate_decision_factors(self, factors: List[str]) -> List[str]:
        """Validate decision factors."""
        if not factors:
            return []
        
        if len(factors) > 15:
            raise PersonaValidationError("decision_factors", "Too many decision factors (max 15)")
        
        validated_factors = []
        for factor in factors:
            if not factor or not factor.strip():
                continue
            if len(factor.strip()) > 200:
                raise PersonaValidationError("decision_factors", f"Decision factor too long: {factor[:50]}...")
            validated_factors.append(factor.strip())
        
        return validated_factors
    
    def is_persona_compatible_with_accent(self, persona: Persona, accent: AccentType) -> bool:
        """Check if persona is compatible with accent."""
        return persona.is_compatible_with_accent(accent)
    
    def get_personas_by_trait_compatibility(
        self, 
        personas: List[Persona], 
        required_traits: List[PersonalityTrait]
    ) -> List[Persona]:
        """Get personas that have required traits."""
        compatible_personas = []
        for persona in personas:
            if persona.personality_traits.has_all_traits(required_traits):
                compatible_personas.append(persona)
        return compatible_personas
    
    def get_persona_summary(self, persona: Persona) -> dict:
        """Get a summary of the persona."""
        return {
            'id': str(persona.id.value),
            'name': persona.name,
            'description': persona.description,
            'accent': persona.accent.value,
            'personality_traits': persona.personality_traits.get_trait_names(),
            'conversation_goals_count': len(persona.conversation_goals),
            'pain_points_count': len(persona.pain_points),
            'objections_count': len(persona.objections),
            'decision_factors_count': len(persona.decision_factors),
            'has_budget_range': bool(persona.budget_range),
            'has_timeline': bool(persona.timeline),
            'has_company_size': bool(persona.company_size),
            'has_industry': bool(persona.industry)
        }
    
    def generate_persona_prompt(self, persona: Persona) -> str:
        """Generate a complete prompt for the persona."""
        prompt_parts = [
            f"Eres {persona.name}, {persona.description}",
            "",
            "INFORMACIÓN PERSONAL:",
            f"- Background: {persona.background}",
            f"- Rasgos de personalidad: {', '.join(persona.personality_traits.get_trait_names())}",
            f"- Acento: {persona.accent.value}",
            "",
            "OBJETIVOS DE LA CONVERSACIÓN:"
        ]
        
        for goal in persona.conversation_goals:
            prompt_parts.append(f"- {goal}")
        
        if persona.pain_points:
            prompt_parts.extend(["", "PUNTOS DE DOLOR:"])
            for pain in persona.pain_points:
                prompt_parts.append(f"- {pain}")
        
        if persona.objections:
            prompt_parts.extend(["", "OBJECIONES COMUNES:"])
            for objection in persona.objections:
                prompt_parts.append(f"- {objection}")
        
        if persona.decision_factors:
            prompt_parts.extend(["", "FACTORES DE DECISIÓN:"])
            for factor in persona.decision_factors:
                prompt_parts.append(f"- {factor}")
        
        if persona.budget_range:
            prompt_parts.extend(["", f"RANGO DE PRESUPUESTO: {persona.budget_range}"])
        
        if persona.timeline:
            prompt_parts.extend(["", f"CRONOGRAMA: {persona.timeline}"])
        
        if persona.company_size:
            prompt_parts.extend(["", f"TAMAÑO DE EMPRESA: {persona.company_size}"])
        
        if persona.industry:
            prompt_parts.extend(["", f"INDUSTRIA: {persona.industry}"])
        
        prompt_parts.extend([
            "",
            "INSTRUCCIONES:",
            "1. Mantén tu personalidad y acento consistentes",
            "2. Responde de manera natural y conversacional",
            "3. Haz preguntas relevantes para entender las necesidades",
            "4. Presenta objeciones cuando sea apropiado",
            "5. Mantén el foco en los objetivos de la conversación",
            f"6. Responde en español con el acento {persona.accent.value}",
            "7. Mantén las respuestas concisas (máximo 2-3 oraciones)",
            "",
            persona.prompt_template
        ])
        
        return "\n".join(prompt_parts)
