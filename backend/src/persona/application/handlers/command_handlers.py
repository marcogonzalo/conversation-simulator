"""
Command handlers for persona bounded context.
"""
from typing import List
from uuid import UUID

from src.persona.application.commands.load_persona import (
    LoadPersonaCommand, LoadPersonaResult,
    CreatePersonaCommand, CreatePersonaResult,
    UpdatePersonaCommand, UpdatePersonaResult,
    DeletePersonaCommand, DeletePersonaResult
)
from src.persona.domain.entities.persona import Persona, AccentType
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.value_objects.personality_traits import PersonalityTraits
from src.persona.domain.services.persona_domain_service import PersonaDomainService
from src.persona.domain.repositories.persona_repository import PersonaRepository
from src.persona.domain.exceptions import PersonaNotFoundError, PersonaValidationError


class LoadPersonaCommandHandler:
    """Handler for load persona command."""
    
    def __init__(
        self,
        persona_repository: PersonaRepository,
        domain_service: PersonaDomainService
    ):
        self._persona_repository = persona_repository
        self._domain_service = domain_service
    
    async def handle(self, command: LoadPersonaCommand) -> LoadPersonaResult:
        """Handle load persona command."""
        try:
            persona_id = PersonaId(UUID(command.persona_id))
            persona = await self._persona_repository.get_by_id(persona_id)
            
            if not persona:
                return LoadPersonaResult(
                    persona_id=None,
                    success=False,
                    message="Persona not found"
                )
            
            return LoadPersonaResult(
                persona_id=persona_id,
                success=True,
                message="Persona loaded successfully"
            )
        
        except (ValueError, TypeError):
            return LoadPersonaResult(
                persona_id=None,
                success=False,
                message="Invalid persona ID"
            )
        except Exception as e:
            return LoadPersonaResult(
                persona_id=None,
                success=False,
                message=f"Failed to load persona: {str(e)}"
            )


class CreatePersonaCommandHandler:
    """Handler for create persona command."""
    
    def __init__(
        self,
        persona_repository: PersonaRepository,
        domain_service: PersonaDomainService
    ):
        self._persona_repository = persona_repository
        self._domain_service = domain_service
    
    async def handle(self, command: CreatePersonaCommand) -> CreatePersonaResult:
        """Handle create persona command."""
        try:
            # Validate persona data
            self._domain_service.validate_persona_data(
                command.name, command.description, command.background,
                command.voice_id, command.prompt_template
            )
            
            # Validate and create personality traits
            personality_traits = self._domain_service.validate_personality_traits(
                command.personality_traits
            )
            
            # Validate other fields
            conversation_goals = self._domain_service.validate_conversation_goals(
                command.conversation_goals
            )
            pain_points = self._domain_service.validate_pain_points(command.pain_points)
            objections = self._domain_service.validate_objections(command.objections)
            decision_factors = self._domain_service.validate_decision_factors(
                command.decision_factors
            )
            
            # Validate accent
            try:
                accent = AccentType(command.accent)
            except ValueError:
                return CreatePersonaResult(
                    persona_id=None,
                    success=False,
                    message=f"Invalid accent: {command.accent}"
                )
            
            # Create persona
            persona_id = PersonaId.generate()
            persona = Persona(
                persona_id=persona_id,
                name=command.name.strip(),
                description=command.description.strip(),
                background=command.background.strip(),
                personality_traits=personality_traits,
                accent=accent,
                voice_id=command.voice_id.strip(),
                prompt_template=command.prompt_template.strip(),
                conversation_goals=conversation_goals,
                pain_points=pain_points,
                objections=objections,
                decision_factors=decision_factors,
                budget_range=command.budget_range,
                timeline=command.timeline,
                company_size=command.company_size,
                industry=command.industry,
                metadata=command.metadata or {}
            )
            
            # Save persona
            await self._persona_repository.save(persona)
            
            return CreatePersonaResult(
                persona_id=persona_id,
                success=True,
                message="Persona created successfully"
            )
        
        except PersonaValidationError as e:
            return CreatePersonaResult(
                persona_id=None,
                success=False,
                message=str(e)
            )
        except Exception as e:
            return CreatePersonaResult(
                persona_id=None,
                success=False,
                message=f"Failed to create persona: {str(e)}"
            )


class UpdatePersonaCommandHandler:
    """Handler for update persona command."""
    
    def __init__(
        self,
        persona_repository: PersonaRepository,
        domain_service: PersonaDomainService
    ):
        self._persona_repository = persona_repository
        self._domain_service = domain_service
    
    async def handle(self, command: UpdatePersonaCommand) -> UpdatePersonaResult:
        """Handle update persona command."""
        try:
            persona_id = PersonaId(UUID(command.persona_id))
            persona = await self._persona_repository.get_by_id(persona_id)
            
            if not persona:
                return UpdatePersonaResult(
                    persona_id=None,
                    success=False,
                    message="Persona not found"
                )
            
            # Update fields if provided
            if command.name is not None:
                persona.update_name(command.name)
            
            if command.description is not None:
                persona.update_description(command.description)
            
            if command.background is not None:
                persona.update_background(command.background)
            
            if command.personality_traits is not None:
                traits = self._domain_service.validate_personality_traits(
                    command.personality_traits
                )
                persona.update_personality_traits(traits)
            
            if command.accent is not None:
                try:
                    accent = AccentType(command.accent)
                    persona.update_accent(accent)
                except ValueError:
                    return UpdatePersonaResult(
                        persona_id=None,
                        success=False,
                        message=f"Invalid accent: {command.accent}"
                    )
            
            if command.voice_id is not None:
                persona.update_voice_id(command.voice_id)
            
            if command.prompt_template is not None:
                persona.update_prompt_template(command.prompt_template)
            
            if command.conversation_goals is not None:
                # Clear existing goals and add new ones
                for goal in persona.conversation_goals:
                    persona.remove_conversation_goal(goal)
                for goal in self._domain_service.validate_conversation_goals(
                    command.conversation_goals
                ):
                    persona.add_conversation_goal(goal)
            
            if command.pain_points is not None:
                # Clear existing pain points and add new ones
                for point in persona.pain_points:
                    persona.remove_pain_point(point)
                for point in self._domain_service.validate_pain_points(
                    command.pain_points
                ):
                    persona.add_pain_point(point)
            
            if command.objections is not None:
                # Clear existing objections and add new ones
                for objection in persona.objections:
                    persona.remove_objection(objection)
                for objection in self._domain_service.validate_objections(
                    command.objections
                ):
                    persona.add_objection(objection)
            
            if command.decision_factors is not None:
                # Clear existing decision factors and add new ones
                for factor in persona.decision_factors:
                    persona.remove_decision_factor(factor)
                for factor in self._domain_service.validate_decision_factors(
                    command.decision_factors
                ):
                    persona.add_decision_factor(factor)
            
            if command.budget_range is not None:
                persona.update_metadata('budget_range', command.budget_range)
            
            if command.timeline is not None:
                persona.update_metadata('timeline', command.timeline)
            
            if command.company_size is not None:
                persona.update_metadata('company_size', command.company_size)
            
            if command.industry is not None:
                persona.update_metadata('industry', command.industry)
            
            if command.metadata is not None:
                for key, value in command.metadata.items():
                    persona.update_metadata(key, value)
            
            # Save updated persona
            await self._persona_repository.save(persona)
            
            return UpdatePersonaResult(
                persona_id=persona_id,
                success=True,
                message="Persona updated successfully"
            )
        
        except (ValueError, TypeError):
            return UpdatePersonaResult(
                persona_id=None,
                success=False,
                message="Invalid persona ID"
            )
        except PersonaValidationError as e:
            return UpdatePersonaResult(
                persona_id=None,
                success=False,
                message=str(e)
            )
        except Exception as e:
            return UpdatePersonaResult(
                persona_id=None,
                success=False,
                message=f"Failed to update persona: {str(e)}"
            )


class DeletePersonaCommandHandler:
    """Handler for delete persona command."""
    
    def __init__(
        self,
        persona_repository: PersonaRepository,
        domain_service: PersonaDomainService
    ):
        self._persona_repository = persona_repository
        self._domain_service = domain_service
    
    async def handle(self, command: DeletePersonaCommand) -> DeletePersonaResult:
        """Handle delete persona command."""
        try:
            persona_id = PersonaId(UUID(command.persona_id))
            
            # Check if persona exists
            if not await self._persona_repository.exists(persona_id):
                return DeletePersonaResult(
                    success=False,
                    message="Persona not found"
                )
            
            # Delete persona
            success = await self._persona_repository.delete(persona_id)
            
            if success:
                return DeletePersonaResult(
                    success=True,
                    message="Persona deleted successfully"
                )
            else:
                return DeletePersonaResult(
                    success=False,
                    message="Failed to delete persona"
                )
        
        except (ValueError, TypeError):
            return DeletePersonaResult(
                success=False,
                message="Invalid persona ID"
            )
        except Exception as e:
            return DeletePersonaResult(
                success=False,
                message=f"Failed to delete persona: {str(e)}"
            )
