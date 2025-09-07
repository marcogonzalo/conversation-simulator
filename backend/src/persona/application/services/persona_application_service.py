"""
Persona application service.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.persona.application.commands.load_persona import (
    LoadPersonaCommand, LoadPersonaResult,
    CreatePersonaCommand, CreatePersonaResult,
    UpdatePersonaCommand, UpdatePersonaResult,
    DeletePersonaCommand, DeletePersonaResult
)
from src.persona.application.queries.get_available_personas import (
    GetAvailablePersonasQuery, GetAvailablePersonasResult, PersonaDto,
    GetPersonaByIdQuery, GetPersonaByIdResult,
    GetPersonasByAccentQuery, GetPersonasByAccentResult,
    GetPersonasByTraitsQuery, GetPersonasByTraitsResult
)
from src.persona.application.handlers.command_handlers import (
    LoadPersonaCommandHandler, CreatePersonaCommandHandler,
    UpdatePersonaCommandHandler, DeletePersonaCommandHandler
)
from src.persona.application.handlers.query_handlers import (
    GetAvailablePersonasQueryHandler, GetPersonaByIdQueryHandler,
    GetPersonasByAccentQueryHandler, GetPersonasByTraitsQueryHandler
)
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.services.persona_domain_service import PersonaDomainService
from src.persona.domain.repositories.persona_repository import PersonaRepository


class PersonaApplicationService:
    """Application service for persona operations."""
    
    def __init__(
        self,
        persona_repository: PersonaRepository,
        domain_service: PersonaDomainService
    ):
        self._persona_repository = persona_repository
        self._domain_service = domain_service
        
        # Initialize handlers
        self._load_persona_handler = LoadPersonaCommandHandler(
            persona_repository, domain_service
        )
        self._create_persona_handler = CreatePersonaCommandHandler(
            persona_repository, domain_service
        )
        self._update_persona_handler = UpdatePersonaCommandHandler(
            persona_repository, domain_service
        )
        self._delete_persona_handler = DeletePersonaCommandHandler(
            persona_repository, domain_service
        )
        
        self._get_available_personas_handler = GetAvailablePersonasQueryHandler(
            persona_repository
        )
        self._get_persona_by_id_handler = GetPersonaByIdQueryHandler(
            persona_repository
        )
        self._get_personas_by_accent_handler = GetPersonasByAccentQueryHandler(
            persona_repository
        )
        self._get_personas_by_traits_handler = GetPersonasByTraitsQueryHandler(
            persona_repository
        )
    
    # Command operations
    async def load_persona(self, persona_id: str) -> LoadPersonaResult:
        """Load a persona by ID."""
        command = LoadPersonaCommand(persona_id=persona_id)
        return await self._load_persona_handler.handle(command)
    
    async def create_persona(
        self,
        name: str,
        description: str,
        background: str,
        personality_traits: List[str],
        accent: str,
        voice_id: str,
        prompt_template: str,
        conversation_goals: List[str],
        pain_points: List[str] = None,
        objections: List[str] = None,
        decision_factors: List[str] = None,
        budget_range: Optional[str] = None,
        timeline: Optional[str] = None,
        company_size: Optional[str] = None,
        industry: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CreatePersonaResult:
        """Create a new persona."""
        command = CreatePersonaCommand(
            name=name,
            description=description,
            background=background,
            personality_traits=personality_traits,
            accent=accent,
            voice_id=voice_id,
            prompt_template=prompt_template,
            conversation_goals=conversation_goals,
            pain_points=pain_points or [],
            objections=objections or [],
            decision_factors=decision_factors or [],
            budget_range=budget_range,
            timeline=timeline,
            company_size=company_size,
            industry=industry,
            metadata=metadata
        )
        return await self._create_persona_handler.handle(command)
    
    async def update_persona(
        self,
        persona_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        background: Optional[str] = None,
        personality_traits: Optional[List[str]] = None,
        accent: Optional[str] = None,
        voice_id: Optional[str] = None,
        prompt_template: Optional[str] = None,
        conversation_goals: Optional[List[str]] = None,
        pain_points: Optional[List[str]] = None,
        objections: Optional[List[str]] = None,
        decision_factors: Optional[List[str]] = None,
        budget_range: Optional[str] = None,
        timeline: Optional[str] = None,
        company_size: Optional[str] = None,
        industry: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UpdatePersonaResult:
        """Update an existing persona."""
        command = UpdatePersonaCommand(
            persona_id=persona_id,
            name=name,
            description=description,
            background=background,
            personality_traits=personality_traits,
            accent=accent,
            voice_id=voice_id,
            prompt_template=prompt_template,
            conversation_goals=conversation_goals,
            pain_points=pain_points,
            objections=objections,
            decision_factors=decision_factors,
            budget_range=budget_range,
            timeline=timeline,
            company_size=company_size,
            industry=industry,
            metadata=metadata
        )
        return await self._update_persona_handler.handle(command)
    
    async def delete_persona(self, persona_id: str) -> DeletePersonaResult:
        """Delete a persona."""
        command = DeletePersonaCommand(persona_id=persona_id)
        return await self._delete_persona_handler.handle(command)
    
    # Query operations
    async def get_available_personas(
        self,
        accent_filter: Optional[str] = None,
        trait_filter: Optional[List[str]] = None
    ) -> GetAvailablePersonasResult:
        """Get all available personas with optional filters."""
        query = GetAvailablePersonasQuery(
            accent_filter=accent_filter,
            trait_filter=trait_filter
        )
        return await self._get_available_personas_handler.handle(query)
    
    async def get_persona_by_id(self, persona_id: str) -> GetPersonaByIdResult:
        """Get a persona by ID."""
        query = GetPersonaByIdQuery(persona_id=persona_id)
        return await self._get_persona_by_id_handler.handle(query)
    
    async def get_personas_by_accent(self, accent: str) -> GetPersonasByAccentResult:
        """Get personas by accent."""
        query = GetPersonasByAccentQuery(accent=accent)
        return await self._get_personas_by_accent_handler.handle(query)
    
    async def get_personas_by_traits(self, traits: List[str]) -> GetPersonasByTraitsResult:
        """Get personas by traits."""
        query = GetPersonasByTraitsQuery(traits=traits)
        return await self._get_personas_by_traits_handler.handle(query)
    
    # Domain service operations
    async def get_persona_summary(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Get persona summary."""
        try:
            persona_id_obj = PersonaId(UUID(persona_id))
            persona = await self._persona_repository.get_by_id(persona_id_obj)
            
            if not persona:
                return None
            
            return self._domain_service.get_persona_summary(persona)
        
        except Exception:
            return None
    
    async def generate_persona_prompt(self, persona_id: str) -> Optional[str]:
        """Generate persona prompt."""
        try:
            persona_id_obj = PersonaId(UUID(persona_id))
            persona = await self._persona_repository.get_by_id(persona_id_obj)
            
            if not persona:
                return None
            
            return self._domain_service.generate_persona_prompt(persona)
        
        except Exception:
            return None
    
    async def validate_persona_compatibility(
        self,
        persona_id: str,
        accent: str
    ) -> bool:
        """Validate persona compatibility with accent."""
        try:
            from src.persona.domain.entities.persona import AccentType
            
            persona_id_obj = PersonaId(UUID(persona_id))
            persona = await self._persona_repository.get_by_id(persona_id_obj)
            
            if not persona:
                return False
            
            accent_type = AccentType(accent)
            return self._domain_service.is_persona_compatible_with_accent(
                persona, accent_type
            )
        
        except Exception:
            return False
