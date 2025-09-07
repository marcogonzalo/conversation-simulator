"""
AI conversation service for infrastructure layer.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.conversation.domain.entities.conversation import Conversation
from src.conversation.domain.entities.message import Message, MessageRole
from src.conversation.domain.value_objects.message_content import MessageContent
from src.persona.domain.entities.persona import Persona
from src.shared.infrastructure.external_apis.api_config import api_config
from src.shared.infrastructure.external_apis.ai_service_factory import AIServiceFactory
from src.conversation.domain.exceptions import ConversationStateError

logger = logging.getLogger(__name__)


class AIConversationService:
    """Service for AI-powered conversation coordination."""
    
    def __init__(self, ai_provider: str = None, api_key: str = None):
        self.ai_provider = ai_provider or api_config.ai_provider
        self.api_key = api_key
        self.api_config = api_config
        
        # Initialize AI service using factory
        self.ai_service = AIServiceFactory.create_ai_service(self.ai_provider, self.api_key)
        
        if self.ai_service:
            logger.info(f"AI Conversation Service initialized with {self.ai_service.provider} ({self.ai_service.model_name})")
        else:
            logger.warning("AI Conversation Service initialized without AI service (fallback mode)")
    
    async def generate_response(
        self,
        conversation: Conversation,
        user_message: str,
        persona: Persona
    ) -> str:
        """Generate AI response for conversation."""
        try:
            if not self.ai_service:
                # Fallback to simulated response
                return await self._generate_simulated_response(user_message, persona)
            
            # Build conversation context
            context = await self._build_conversation_context(conversation, persona)
            
            # Build conversation history
            conversation_history = []
            for message in conversation.messages[-10:]:  # Last 10 messages
                role = "user" if message.role == MessageRole.USER else "assistant"
                conversation_history.append({
                    "role": role,
                    "content": message.content.text
                })
            
            # Generate response using AI service
            response = await self.ai_service.generate_conversation_response(
                system_prompt=context,
                user_message=user_message,
                conversation_history=conversation_history
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Fallback to simulated response
            return await self._generate_simulated_response(user_message, persona)
    
    async def _build_conversation_context(
        self,
        conversation: Conversation,
        persona: Persona
    ) -> str:
        """Build conversation context for AI."""
        context_parts = [
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
            context_parts.append(f"- {goal}")
        
        if persona.pain_points:
            context_parts.extend(["", "PUNTOS DE DOLOR:"])
            for pain in persona.pain_points:
                context_parts.append(f"- {pain}")
        
        if persona.objections:
            context_parts.extend(["", "OBJECIONES COMUNES:"])
            for objection in persona.objections:
                context_parts.append(f"- {objection}")
        
        if persona.decision_factors:
            context_parts.extend(["", "FACTORES DE DECISIÓN:"])
            for factor in persona.decision_factors:
                context_parts.append(f"- {factor}")
        
        if persona.budget_range:
            context_parts.extend(["", f"RANGO DE PRESUPUESTO: {persona.budget_range}"])
        
        if persona.timeline:
            context_parts.extend(["", f"CRONOGRAMA: {persona.timeline}"])
        
        if persona.company_size:
            context_parts.extend(["", f"TAMAÑO DE EMPRESA: {persona.company_size}"])
        
        if persona.industry:
            context_parts.extend(["", f"INDUSTRIA: {persona.industry}"])
        
        # Add conversation history
        context_parts.extend([
            "",
            "HISTORIAL DE CONVERSACIÓN:",
            f"- Duración: {conversation.duration_seconds or 0} segundos",
            f"- Mensajes: {len(conversation.messages)}",
            ""
        ])
        
        for message in conversation.messages[-10:]:  # Last 10 messages
            role = "Usuario" if message.role == MessageRole.USER else "Asistente"
            context_parts.append(f"{role}: {message.content.text}")
        
        context_parts.extend([
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
        
        return "\n".join(context_parts)
    
    async def _call_claude_api(
        self,
        context: str,
        user_message: str,
        persona: Persona
    ) -> str:
        """Call Claude Sonnet 4 API."""
        try:
            # This is a placeholder implementation
            # In a real system, this would call the actual Anthropic API
            
            logger.info(f"Calling Claude API for persona {persona.name}")
            
            # Simulate API call
            await self._simulate_api_delay()
            
            # Generate simulated response based on persona
            response = await self._generate_simulated_response(user_message, persona)
            
            return response
        
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise
    
    async def _simulate_api_delay(self):
        """Simulate API call delay."""
        import asyncio
        await asyncio.sleep(0.5)  # Simulate 500ms delay
    
    async def _generate_simulated_response(self, user_message: str, persona: Persona) -> str:
        """Generate simulated response based on persona."""
        # This is a placeholder - in real implementation, this would be replaced
        # with actual Claude Sonnet 4 API call
        
        responses = {
            "friendly": [
                "¡Hola! Me alegra mucho conocerte. ¿Podrías contarme más sobre tu empresa?",
                "Eso suena muy interesante. ¿Cuáles son los principales desafíos que enfrentas?",
                "Entiendo perfectamente. ¿Has considerado alguna solución específica?",
                "Me parece una excelente oportunidad. ¿Qué te gustaría saber sobre nuestros servicios?"
            ],
            "skeptical": [
                "Hmm, eso suena interesante, pero necesito más detalles. ¿Puedes ser más específico?",
                "He escuchado eso antes. ¿Qué hace que tu situación sea diferente?",
                "No estoy seguro de entender completamente. ¿Podrías explicarlo mejor?",
                "Eso suena bien en teoría, pero ¿cómo funciona en la práctica?"
            ],
            "analytical": [
                "Déjame analizar esto paso a paso. ¿Cuáles son los datos específicos?",
                "Necesito entender mejor los números. ¿Puedes compartir algunas métricas?",
                "Eso es interesante desde una perspectiva analítica. ¿Qué evidencia tienes?",
                "Para tomar una decisión informada, necesito más información técnica."
            ]
        }
        
        # Get persona traits
        traits = persona.personality_traits.get_trait_names()
        
        # Select response based on primary trait
        if "friendly" in traits:
            response_type = "friendly"
        elif "skeptical" in traits:
            response_type = "skeptical"
        elif "analytical" in traits:
            response_type = "analytical"
        else:
            response_type = "friendly"  # Default
        
        import random
        return random.choice(responses[response_type])
    
    async def should_end_conversation(
        self,
        conversation: Conversation,
        persona: Persona
    ) -> bool:
        """Determine if conversation should end."""
        # Check duration
        if conversation.duration_seconds and conversation.duration_seconds > self.api_config.max_conversation_duration:
            return True
        
        # Check message count
        if len(conversation.messages) > 50:  # Max 50 messages
            return True
        
        # Check for natural ending signals
        last_messages = conversation.messages[-3:] if len(conversation.messages) >= 3 else conversation.messages
        
        ending_signals = [
            "gracias", "adiós", "hasta luego", "nos vemos", "chao",
            "perfecto", "entendido", "de acuerdo", "excelente"
        ]
        
        for message in last_messages:
            if message.role == MessageRole.USER:
                content_lower = message.content.text.lower()
                if any(signal in content_lower for signal in ending_signals):
                    return True
        
        return False
    
    async def get_conversation_summary(self, conversation: Conversation) -> Dict[str, Any]:
        """Get conversation summary for analysis."""
        user_messages = [m for m in conversation.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in conversation.messages if m.role == MessageRole.ASSISTANT]
        
        return {
            "conversation_id": str(conversation.id.value),
            "persona_id": conversation.persona_id,
            "duration_seconds": conversation.duration_seconds,
            "total_messages": len(conversation.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "started_at": conversation.started_at.isoformat() if conversation.started_at else None,
            "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
            "status": conversation.status.value
        }
