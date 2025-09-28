"""
Service for loading conversation instructions from external configuration files.
"""
import logging
import yaml
import os
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class InstructionLoaderService:
    """Service to load conversation instructions from external configuration."""
    
    def __init__(self):
        self._instructions_cache: Dict[str, Any] = {}
        self._config_path = self._get_config_path()
    
    def _get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        # Get the backend directory (parent of src)
        backend_dir = Path(__file__).parent.parent.parent.parent
        config_path = backend_dir / "config" / "conversation_instructions.yaml"
        return config_path
    
    def load_instructions(self) -> Dict[str, Any]:
        """Load conversation instructions from YAML file."""
        if not self._instructions_cache:
            try:
                if not self._config_path.exists():
                    logger.warning(f"Configuration file not found: {self._config_path}")
                    return self._get_default_instructions()
                
                with open(self._config_path, 'r', encoding='utf-8') as file:
                    self._instructions_cache = yaml.safe_load(file)
                
                logger.info("Conversation instructions loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading conversation instructions: {e}")
                return self._get_default_instructions()
        
        return self._instructions_cache
    
    def get_core_simulation_instructions(self) -> str:
        """Get the core simulation instructions."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('core_simulation_instructions', '')
    
    def get_conversation_purpose(self) -> str:
        """Get the conversation purpose text."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('purpose', '')
    
    def get_additional_instructions(self) -> List[str]:
        """Get the list of additional instructions."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('additional_instructions', [])
    
    def get_behavior_guidelines(self) -> List[str]:
        """Get the behavior guidelines."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('behavior_guidelines', [])
    
    def get_conversation_flow(self) -> List[str]:
        """Get the conversation flow guidelines."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('conversation_flow', [])
    
    def get_response_style(self) -> Dict[str, Any]:
        """Get the response style configuration."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('response_style', {})
    
    def get_context_awareness(self) -> List[str]:
        """Get the context awareness guidelines."""
        instructions = self.load_instructions()
        return instructions.get('conversation', {}).get('context_awareness', [])
    
    def _get_default_instructions(self) -> Dict[str, Any]:
        """Get default instructions if configuration file is not available."""
        return {
            'conversation': {
                'purpose': 'Esta conversación tiene como objetivo la compra de un inmueble para uso residencial personal (vivienda).',
                'role_definition': 'Eres un simulador de conversación de ventas. Tu función es SIMULAR ser una persona específica que es un CLIENTE POTENCIAL.',
                'additional_instructions': [
                    'Responde naturalmente en español',
                    'Mantén tu personalidad y acento consistentes',
                    'Responde de manera natural y conversacional'
                ],
                'behavior_guidelines': [
                    'Sé natural y auténtico en tus respuestas',
                    'Muestra interés genuino en encontrar la vivienda adecuada'
                ],
                'conversation_flow': [
                    'Inicia con interés general en comprar una vivienda',
                    'Progresivamente revela más detalles sobre tus necesidades'
                ],
                'response_style': {
                    'max_sentences': 3,
                    'language': 'spanish',
                    'tone': 'conversational',
                    'formality': 'casual'
                },
                'context_awareness': [
                    'Considera el historial de la conversación',
                    'Mantén coherencia con mensajes anteriores'
                ]
            }
        }
    
    def format_instructions_for_persona(self, persona_config: Dict[str, Any]) -> str:
        """Format the instructions for a specific persona."""
        instructions = self.load_instructions()
        conversation_config = instructions.get('conversation', {})
        
        name = persona_config.get("name", "Assistant")
        accent = persona_config.get("accent", "neutral")
        
        # Build the instruction text
        instruction_parts = []
        
        # Add core simulation instructions first (most important)
        core_instructions = conversation_config.get('core_simulation_instructions', '')
        if core_instructions:
            instruction_parts.append(core_instructions)
        
        # Add purpose
        purpose = conversation_config.get('purpose', '')
        if purpose:
            instruction_parts.extend(['', 'PROPÓSITO DE LA CONVERSACIÓN:', purpose])
        
        # Add additional instructions
        additional = conversation_config.get('additional_instructions', [])
        if additional:
            instruction_parts.extend(['', 'INSTRUCCIONES ADICIONALES:'])
            for instruction in additional:
                if '{accent}' in instruction:
                    instruction = instruction.format(accent=accent)
                instruction_parts.append(f"- {instruction}")
        
        # Add behavior guidelines
        behavior = conversation_config.get('behavior_guidelines', [])
        if behavior:
            instruction_parts.extend(['', 'GUÍAS DE COMPORTAMIENTO:'])
            for guideline in behavior:
                instruction_parts.append(f"- {guideline}")
        
        # Add conversation flow
        flow = conversation_config.get('conversation_flow', [])
        if flow:
            instruction_parts.extend(['', 'FLUJO DE CONVERSACIÓN:'])
            for step in flow:
                instruction_parts.append(f"- {step}")
        
        return '\n'.join(instruction_parts)
