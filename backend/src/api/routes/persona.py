"""
Persona API routes with DDD architecture.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from src.persona.application.services.persona_application_service import PersonaApplicationService
from src.persona.domain.repositories.persona_repository import PersonaRepository
from src.persona.domain.services.persona_domain_service import PersonaDomainService
from src.persona.infrastructure.repositories.yaml_persona_repository import YAMLPersonaRepository

logger = logging.getLogger(__name__)

# Dependency injection
def get_persona_repository() -> PersonaRepository:
    """Get persona repository instance."""
    return YAMLPersonaRepository()

def get_persona_domain_service() -> PersonaDomainService:
    """Get persona domain service instance."""
    return PersonaDomainService()

def get_persona_application_service(
    repository: PersonaRepository = Depends(get_persona_repository),
    domain_service: PersonaDomainService = Depends(get_persona_domain_service)
) -> PersonaApplicationService:
    """Get persona application service instance."""
    return PersonaApplicationService(repository, domain_service)

# Router
router = APIRouter()

@router.get("/")
async def get_available_personas(
    accent_filter: Optional[str] = Query(None, description="Filter by accent type"),
    trait_filter: Optional[List[str]] = Query(None, description="Filter by personality traits"),
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Get all available personas with optional filters."""
    try:
        result = await service.get_available_personas(
            accent_filter=accent_filter,
            trait_filter=trait_filter
        )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "personas": result.personas,
            "total_count": result.total_count,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personas: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{persona_id}")
async def get_persona_by_id(
    persona_id: str,
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Get a persona by ID."""
    try:
        result = await service.get_persona_by_id(persona_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return {
            "persona": result.persona,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/accent/{accent}")
async def get_personas_by_accent(
    accent: str,
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Get personas by accent type."""
    try:
        result = await service.get_personas_by_accent(accent)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "personas": result.personas,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personas by accent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/traits/{traits}")
async def get_personas_by_traits(
    traits: str,
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Get personas by traits (comma-separated)."""
    try:
        trait_list = [t.strip() for t in traits.split(",")]
        result = await service.get_personas_by_traits(trait_list)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "personas": result.personas,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personas by traits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{persona_id}/summary")
async def get_persona_summary(
    persona_id: str,
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Get persona summary."""
    try:
        summary = await service.get_persona_summary(persona_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{persona_id}/prompt")
async def get_persona_prompt(
    persona_id: str,
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Get persona prompt."""
    try:
        prompt = await service.generate_persona_prompt(persona_id)
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        return {
            "prompt": prompt,
            "persona_id": persona_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{persona_id}/compatibility/{accent}")
async def check_persona_compatibility(
    persona_id: str,
    accent: str,
    service: PersonaApplicationService = Depends(get_persona_application_service)
):
    """Check persona compatibility with accent."""
    try:
        compatible = await service.validate_persona_compatibility(persona_id, accent)
        
        return {
            "persona_id": persona_id,
            "accent": accent,
            "compatible": compatible
        }
    
    except Exception as e:
        logger.error(f"Error checking persona compatibility: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")