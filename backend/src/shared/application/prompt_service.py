"""
Prompt Service - Aplicación
Servicio de aplicación para gestión de prompts dinámicos (5 capas)
"""

from typing import Dict, Any, List, Optional
from ..domain.prompt_builder import PromptBuilder
import logging

logger = logging.getLogger(__name__)


class PromptService:
    """Servicio de aplicación para gestión de prompts (5 capas)"""

    def __init__(
        self, 
        config_path: str = "/app/src/shared/infrastructure/config",
        strict_validation: bool = False
    ):
        self.prompt_builder = PromptBuilder(config_path, strict_validation=strict_validation)

    def generate_prompt(
        self,
        industry_id: str,
        situation_id: str,
        psychology_id: str,
        identity_id: str
    ) -> str:
        """
        Genera un prompt dinámico combinando las 5 capas

        Args:
            industry_id: ID del contexto de industria (ej: "real_estate")
            situation_id: ID de la situación de venta (ej: "discovery_no_urgency_price")
            psychology_id: ID de la psicología del cliente (ej: "conservative_analytical")
            identity_id: ID de la identidad del cliente (ej: "ana_garcia")

        Returns:
            Prompt final generado
        """
        try:
            prompt = self.prompt_builder.build_prompt(
                industry_id,
                situation_id,
                psychology_id,
                identity_id
            )
            logger.info(
                f"Prompt generated: {industry_id} + {situation_id} + "
                f"{psychology_id} + {identity_id}"
            )
            return prompt
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            raise

    def get_available_industries(self) -> List[Dict[str, str]]:
        """Obtiene lista de industrias disponibles"""
        industries = self.prompt_builder.get_available_industries()
        return [
            {
                "id": ind,
                "name": ind.replace("_", " ").title()
            }
            for ind in industries
        ]

    def get_available_situations(self) -> List[Dict[str, str]]:
        """Obtiene lista de situaciones de venta disponibles"""
        situations = self.prompt_builder.get_available_situations()
        return [
            {
                "id": sit,
                "name": sit.replace("_", " ").title()
            }
            for sit in situations
        ]

    def get_available_psychologies(self) -> List[Dict[str, str]]:
        """Obtiene lista de psicologías de cliente disponibles"""
        psychologies = self.prompt_builder.get_available_psychologies()
        return [
            {
                "id": psy,
                "name": psy.replace("_", " ").title()
            }
            for psy in psychologies
        ]

    def get_available_identities(self) -> List[Dict[str, str]]:
        """Obtiene lista de identidades de cliente disponibles"""
        identities = self.prompt_builder.get_available_identities()
        return [
            {
                "id": ident,
                "name": ident.replace("_", " ").title()
            }
            for ident in identities
        ]

    def get_all_available_options(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Obtiene todas las opciones disponibles de cada capa

        Returns:
            Diccionario con todas las opciones por capa
        """
        return {
            "industries": self.get_available_industries(),
            "situations": self.get_available_situations(),
            "psychologies": self.get_available_psychologies(),
            "identities": self.get_available_identities()
        }

    def validate_combination(
        self,
        industry_id: str,
        situation_id: str,
        psychology_id: str,
        identity_id: str
    ) -> bool:
        """
        Valida si una combinación de 4 capas es válida

        Returns:
            True si la combinación es válida, False en caso contrario
        """
        try:
            available_industries = self.prompt_builder.get_available_industries()
            available_situations = self.prompt_builder.get_available_situations()
            available_psychologies = self.prompt_builder.get_available_psychologies()
            available_identities = self.prompt_builder.get_available_identities()

            return (
                industry_id in available_industries and
                situation_id in available_situations and
                psychology_id in available_psychologies and
                identity_id in available_identities
            )
        except Exception as e:
            logger.error(f"Error validating combination: {e}")
            return False

    def get_prompt_metadata(
        self,
        industry_id: str,
        situation_id: str,
        psychology_id: str,
        identity_id: str
    ) -> Dict[str, Any]:
        """
        Obtiene metadatos del prompt generado

        Returns:
            Metadatos del prompt
        """
        try:
            prompt = self.generate_prompt(
                industry_id, situation_id, psychology_id, identity_id)

            return {
                "industry_id": industry_id,
                "situation_id": situation_id,
                "psychology_id": psychology_id,
                "identity_id": identity_id,
                "prompt_length": len(prompt),
                "prompt_word_count": len(prompt.split()),
                "available": True
            }
        except Exception as e:
            logger.error(f"Error getting prompt metadata: {e}")
            return {
                "industry_id": industry_id,
                "situation_id": situation_id,
                "psychology_id": psychology_id,
                "identity_id": identity_id,
                "available": False,
                "error": str(e)
            }

    def get_total_combinations(self) -> int:
        """Calcula el número total de combinaciones posibles"""
        industries_count = len(self.prompt_builder.get_available_industries())
        situations_count = len(self.prompt_builder.get_available_situations())
        psychologies_count = len(
            self.prompt_builder.get_available_psychologies())
        identities_count = len(self.prompt_builder.get_available_identities())

        return industries_count * situations_count * psychologies_count * identities_count

    def clear_cache(self):
        """Limpia el cache de prompts"""
        self.prompt_builder.clear_cache()
        logger.info("Prompt cache cleared")
