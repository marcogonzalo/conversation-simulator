"""
Prompt Service - Aplicación
Servicio de aplicación para gestión de prompts dinámicos
"""

from typing import Dict, Any, List, Optional
from ..domain.prompt_builder import PromptBuilder
import logging

logger = logging.getLogger(__name__)


class PromptService:
    """Servicio de aplicación para gestión de prompts"""
    
    def __init__(self, config_path: str = "/app/config"):
        self.prompt_builder = PromptBuilder(config_path)
    
    def generate_prompt(self, conversation_context_id: str, persona_id: str) -> str:
        """
        Genera un prompt dinámico combinando las tres capas
        
        Args:
            conversation_context_id: ID del contexto de conversación
            persona_id: ID de la persona
            
        Returns:
            Prompt final generado
        """
        try:
            prompt = self.prompt_builder.build_prompt(conversation_context_id, persona_id)
            logger.info(f"Prompt generated for context: {conversation_context_id}, persona: {persona_id}")
            return prompt
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            raise
    
    def get_available_combinations(self) -> List[Dict[str, str]]:
        """
        Obtiene todas las combinaciones disponibles de contexto y persona
        
        Returns:
            Lista de combinaciones disponibles
        """
        contexts = self.prompt_builder.get_available_contexts()
        personas = self.prompt_builder.get_available_personas()
        
        combinations = []
        for context in contexts:
            for persona in personas:
                combinations.append({
                    "conversation_context_id": context,
                    "persona_id": persona,
                    "name": f"{context} - {persona}"
                })
        
        return combinations
    
    def get_available_contexts(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de contextos de conversación disponibles
        
        Returns:
            Lista de contextos con metadatos
        """
        contexts = self.prompt_builder.get_available_contexts()
        return [{"id": ctx, "name": ctx.replace("_", " ").title()} for ctx in contexts]
    
    def get_available_personas(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de personas disponibles
        
        Returns:
            Lista de personas con metadatos
        """
        personas = self.prompt_builder.get_available_personas()
        return [{"id": persona, "name": persona.replace("_", " ").title()} for persona in personas]
    
    def validate_combination(self, conversation_context_id: str, persona_id: str) -> bool:
        """
        Valida si una combinación de contexto y persona es válida
        
        Args:
            conversation_context_id: ID del contexto de conversación
            persona_id: ID de la persona
            
        Returns:
            True si la combinación es válida, False en caso contrario
        """
        try:
            available_contexts = self.prompt_builder.get_available_contexts()
            available_personas = self.prompt_builder.get_available_personas()
            
            return (conversation_context_id in available_contexts and 
                    persona_id in available_personas)
        except Exception as e:
            logger.error(f"Error validating combination: {e}")
            return False
    
    def get_prompt_metadata(self, conversation_context_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Obtiene metadatos del prompt generado
        
        Args:
            conversation_context_id: ID del contexto de conversación
            persona_id: ID de la persona
            
        Returns:
            Metadatos del prompt
        """
        try:
            # Generar prompt para obtener metadatos
            prompt = self.generate_prompt(conversation_context_id, persona_id)
            
            return {
                "conversation_context_id": conversation_context_id,
                "persona_id": persona_id,
                "prompt_length": len(prompt),
                "prompt_word_count": len(prompt.split()),
                "available": True
            }
        except Exception as e:
            logger.error(f"Error getting prompt metadata: {e}")
            return {
                "conversation_context_id": conversation_context_id,
                "persona_id": persona_id,
                "available": False,
                "error": str(e)
            }
    
    def clear_cache(self):
        """Limpia el cache de prompts"""
        self.prompt_builder.clear_cache()
        logger.info("Prompt cache cleared")
