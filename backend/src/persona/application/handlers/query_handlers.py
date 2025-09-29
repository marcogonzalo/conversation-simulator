"""
Query handlers for persona bounded context.
"""
from typing import List
from uuid import UUID

from src.persona.application.queries.get_available_personas import (
    GetAvailablePersonasQuery, GetAvailablePersonasResult, PersonaDto,
    GetPersonaByIdQuery, GetPersonaByIdResult,
    GetPersonasByAccentQuery, GetPersonasByAccentResult,
    GetPersonasByTraitsQuery, GetPersonasByTraitsResult
)
from src.persona.domain.entities.persona import AccentType
from src.persona.domain.repositories.persona_repository import PersonaRepository
from src.persona.domain.exceptions import PersonaNotFoundError


class GetAvailablePersonasQueryHandler:
    """Handler for get available personas query."""
    
    def __init__(self, persona_repository: PersonaRepository):
        self._persona_repository = persona_repository
    
    async def handle(self, query: GetAvailablePersonasQuery) -> GetAvailablePersonasResult:
        """Handle get available personas query."""
        try:
            # Get all personas
            personas = await self._persona_repository.get_all()
            
            # Apply filters
            if query.accent_filter:
                personas = [p for p in personas if p.accent.value == query.accent_filter]
            
            if query.trait_filter:
                personas = [
                    p for p in personas 
                    if any(trait in p.personality_traits.get_trait_names() for trait in query.trait_filter)
                ]
            
            # Convert to DTOs
            persona_dtos = [self._persona_to_dto(persona) for persona in personas]
            
            return GetAvailablePersonasResult(
                personas=persona_dtos,
                total_count=len(persona_dtos),
                success=True,
                message="Personas retrieved successfully"
            )
        
        except Exception as e:
            return GetAvailablePersonasResult(
                personas=[],
                total_count=0,
                success=False,
                message=f"Failed to get personas: {str(e)}"
            )
    
    def _persona_to_dto(self, persona) -> PersonaDto:
        """Convert persona entity to DTO."""
        return PersonaDto(
            id=str(persona.id.value),
            name=persona.name,
            description=persona.description,
            background=persona.background,
            personality_traits=persona.personality_traits.get_trait_names(),
            accent=persona.accent.value,
            voice_id=persona.voice_id,
            conversation_goals=persona.conversation_goals,
            pain_points=persona.pain_points,
            objections=persona.objections,
            decision_factors=persona.decision_factors,
            budget_range=persona.budget_range,
            timeline=persona.timeline,
            company_size=persona.company_size,
            industry=persona.industry,
            metadata=persona.metadata,
            created_at=persona.created_at,
            updated_at=persona.updated_at
        )


class GetPersonaByIdQueryHandler:
    """Handler for get persona by ID query."""
    
    def __init__(self, persona_repository: PersonaRepository):
        self._persona_repository = persona_repository
    
    async def handle(self, query: GetPersonaByIdQuery) -> GetPersonaByIdResult:
        """Handle get persona by ID query."""
        try:
            from src.persona.domain.value_objects.persona_id import PersonaId
            
            persona_id = PersonaId.from_string(query.persona_id)
            persona = await self._persona_repository.get_by_id(persona_id)
            
            if not persona:
                return GetPersonaByIdResult(
                    persona=None,
                    success=False,
                    message="Persona not found"
                )
            
            # Convert to DTO
            persona_dto = PersonaDto(
                id=persona.id.value,
                name=persona.name,
                description=persona.description,
                background=persona.background,
                personality_traits=persona.personality_traits.get_trait_names(),
                accent=persona.accent.value,
                voice_id=persona.voice_id,
                conversation_goals=persona.conversation_goals,
                pain_points=persona.pain_points,
                objections=persona.objections,
                decision_factors=persona.decision_factors,
                budget_range=persona.budget_range,
                timeline=persona.timeline,
                company_size=persona.company_size,
                industry=persona.industry,
                metadata=persona.metadata,
                created_at=persona.created_at,
                updated_at=persona.updated_at
            )
            
            return GetPersonaByIdResult(
                persona=persona_dto,
                success=True,
                message="Persona retrieved successfully"
            )
        
        except (ValueError, TypeError):
            return GetPersonaByIdResult(
                persona=None,
                success=False,
                message="Invalid persona ID"
            )
        except Exception as e:
            return GetPersonaByIdResult(
                persona=None,
                success=False,
                message=f"Failed to get persona: {str(e)}"
            )


class GetPersonasByAccentQueryHandler:
    """Handler for get personas by accent query."""
    
    def __init__(self, persona_repository: PersonaRepository):
        self._persona_repository = persona_repository
    
    async def handle(self, query: GetPersonasByAccentQuery) -> GetPersonasByAccentResult:
        """Handle get personas by accent query."""
        try:
            # Validate accent
            try:
                AccentType(query.accent)
            except ValueError:
                return GetPersonasByAccentResult(
                    personas=[],
                    success=False,
                    message=f"Invalid accent: {query.accent}"
                )
            
            # Get personas by accent
            personas = await self._persona_repository.get_by_accent(query.accent)
            
            # Convert to DTOs
            persona_dtos = [
                PersonaDto(
                    id=str(persona.id.value),
                    name=persona.name,
                    description=persona.description,
                    background=persona.background,
                    personality_traits=persona.personality_traits.get_trait_names(),
                    accent=persona.accent.value,
                    voice_id=persona.voice_id,
                    conversation_goals=persona.conversation_goals,
                    pain_points=persona.pain_points,
                    objections=persona.objections,
                    decision_factors=persona.decision_factors,
                    budget_range=persona.budget_range,
                    timeline=persona.timeline,
                    company_size=persona.company_size,
                    industry=persona.industry,
                    metadata=persona.metadata,
                    created_at=persona.created_at,
                    updated_at=persona.updated_at
                )
                for persona in personas
            ]
            
            return GetPersonasByAccentResult(
                personas=persona_dtos,
                success=True,
                message="Personas retrieved successfully"
            )
        
        except Exception as e:
            return GetPersonasByAccentResult(
                personas=[],
                success=False,
                message=f"Failed to get personas by accent: {str(e)}"
            )


class GetPersonasByTraitsQueryHandler:
    """Handler for get personas by traits query."""
    
    def __init__(self, persona_repository: PersonaRepository):
        self._persona_repository = persona_repository
    
    async def handle(self, query: GetPersonasByTraitsQuery) -> GetPersonasByTraitsResult:
        """Handle get personas by traits query."""
        try:
            # Get personas by traits
            personas = await self._persona_repository.get_by_traits(query.traits)
            
            # Convert to DTOs
            persona_dtos = [
                PersonaDto(
                    id=str(persona.id.value),
                    name=persona.name,
                    description=persona.description,
                    background=persona.background,
                    personality_traits=persona.personality_traits.get_trait_names(),
                    accent=persona.accent.value,
                    voice_id=persona.voice_id,
                    conversation_goals=persona.conversation_goals,
                    pain_points=persona.pain_points,
                    objections=persona.objections,
                    decision_factors=persona.decision_factors,
                    budget_range=persona.budget_range,
                    timeline=persona.timeline,
                    company_size=persona.company_size,
                    industry=persona.industry,
                    metadata=persona.metadata,
                    created_at=persona.created_at,
                    updated_at=persona.updated_at
                )
                for persona in personas
            ]
            
            return GetPersonasByTraitsResult(
                personas=persona_dtos,
                success=True,
                message="Personas retrieved successfully"
            )
        
        except Exception as e:
            return GetPersonasByTraitsResult(
                personas=[],
                success=False,
                message=f"Failed to get personas by traits: {str(e)}"
            )
