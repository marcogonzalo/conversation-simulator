"""
Prompt API Routes
Rutas para gestión de prompts dinámicos
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from ...shared.application.prompt_service import PromptService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])

# Dependencia para obtener el servicio de prompts
def get_prompt_service() -> PromptService:
    from src.shared.infrastructure.external_apis.api_config import APIConfig
    config = APIConfig()
    return PromptService(strict_validation=config.prompt_strict_validation)


class PromptRequest(BaseModel):
    """Request para generar un prompt"""
    conversation_context_id: str
    persona_id: str


class PromptResponse(BaseModel):
    """Response con el prompt generado"""
    prompt: str
    metadata: Dict[str, Any]


class CombinationResponse(BaseModel):
    """Response con combinaciones disponibles"""
    combinations: List[Dict[str, str]]


@router.post("/generate", response_model=PromptResponse)
async def generate_prompt(
    request: PromptRequest,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Genera un prompt dinámico combinando las tres capas
    """
    try:
        # Validar combinación
        if not prompt_service.validate_combination(
            request.conversation_context_id, 
            request.persona_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid combination of conversation context and persona"
            )
        
        # Generar prompt
        prompt = prompt_service.generate_prompt(
            request.conversation_context_id,
            request.persona_id
        )
        
        # Obtener metadatos
        metadata = prompt_service.get_prompt_metadata(
            request.conversation_context_id,
            request.persona_id
        )
        
        return PromptResponse(prompt=prompt, metadata=metadata)
        
    except Exception as e:
        logger.error(f"Error generating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/combinations", response_model=CombinationResponse)
async def get_available_combinations(
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Obtiene todas las combinaciones disponibles de contexto y persona
    """
    try:
        combinations = prompt_service.get_available_combinations()
        return CombinationResponse(combinations=combinations)
    except Exception as e:
        logger.error(f"Error getting combinations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options")
async def get_available_options(
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Obtiene todas las opciones disponibles de las 4 capas configurables:
    - Industries (Capa 2)
    - Situations (Capa 3)
    - Psychologies (Capa 4)
    - Identities (Capa 5)
    """
    try:
        options = prompt_service.get_all_available_options()
        return options
    except Exception as e:
        logger.error(f"Error getting available options: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_combination(
    industry_id: str,
    situation_id: str,
    psychology_id: str,
    identity_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Valida si una combinación de 4 capas es semánticamente coherente.
    Devuelve warnings si hay inconsistencias detectadas.
    """
    try:
        # Validar que los IDs existen
        if not prompt_service.validate_combination(
            industry_id, situation_id, psychology_id, identity_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid IDs: one or more configuration files not found"
            )
        
        # Realizar validación semántica
        from ...shared.domain.semantic_validator import SemanticValidator
        
        # Load configurations
        industry = prompt_service.prompt_builder._load_industry_context(industry_id)
        situation = prompt_service.prompt_builder._load_sales_situation(situation_id)
        psychology = prompt_service.prompt_builder._load_client_psychology(psychology_id)
        identity = prompt_service.prompt_builder._load_client_identity(identity_id)
        
        # Validate
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        return {
            "valid": True,  # IDs exist
            "semantically_coherent": is_valid,
            "warnings": warnings,
            "warning_count": len(warnings),
            "combination": {
                "industry_id": industry_id,
                "situation_id": situation_id,
                "psychology_id": psychology_id,
                "identity_id": identity_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating combination: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contexts")
async def get_available_contexts(
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Obtiene lista de contextos de conversación disponibles
    """
    try:
        contexts = prompt_service.get_available_contexts()
        return {"contexts": contexts}
    except Exception as e:
        logger.error(f"Error getting contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personas")
async def get_available_personas(
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Obtiene lista de personas disponibles
    """
    try:
        personas = prompt_service.get_available_personas()
        return {"personas": personas}
    except Exception as e:
        logger.error(f"Error getting personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/{conversation_context_id}/{persona_id}")
async def get_prompt_metadata(
    conversation_context_id: str,
    persona_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Obtiene metadatos de un prompt específico
    """
    try:
        metadata = prompt_service.get_prompt_metadata(
            conversation_context_id,
            persona_id
        )
        return metadata
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_prompt_cache(
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Limpia el cache de prompts
    """
    try:
        prompt_service.clear_cache()
        return {"message": "Prompt cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry")
async def get_prompt_telemetry(
    industry_id: str,
    situation_id: str,
    psychology_id: str,
    identity_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    """
    Obtiene telemetría de un prompt específico.
    
    Devuelve metadata incluyendo:
    - Prompt hash para reproducibilidad
    - Timestamp de generación
    - IDs de las 4 capas
    - Versiones de archivos YAML
    - Longitud y conteo de palabras
    - Warnings de validación semántica
    """
    try:
        metadata = prompt_service.get_prompt_telemetry(
            industry_id, situation_id, psychology_id, identity_id
        )
        
        if metadata is None:
            # Prompt not in cache, generate it to get metadata
            _ = prompt_service.generate_prompt(
                industry_id, situation_id, psychology_id, identity_id
            )
            metadata = prompt_service.get_prompt_telemetry(
                industry_id, situation_id, psychology_id, identity_id
            )
        
        return metadata if metadata else {
            "error": "Unable to generate prompt metadata"
        }
        
    except Exception as e:
        logger.error(f"Error getting prompt telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check para el servicio de prompts
    """
    return {"status": "healthy", "service": "prompt_service"}
