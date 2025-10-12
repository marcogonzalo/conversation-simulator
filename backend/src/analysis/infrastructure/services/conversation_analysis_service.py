"""
Conversation Analysis Service for real-time analysis.
"""
import logging
from typing import Dict, Any, List
import yaml
import json
from pathlib import Path

from src.shared.infrastructure.external_apis.api_config import api_config
from src.shared.infrastructure.external_apis.ai_service_factory import AIServiceFactory
from src.analysis.infrastructure.repositories.file_analysis_repository import FileAnalysisRepository

logger = logging.getLogger(__name__)


class ConversationAnalysisService:
    """Service for analyzing conversations using AI."""
    
    def __init__(self, ai_provider: str = None, api_key: str = None, analysis_repository: FileAnalysisRepository = None):
        self.ai_provider = ai_provider or api_config.ai_provider
        self.api_key = api_key
        self.api_config = api_config
        
        # Initialize AI service using factory
        self.ai_service = AIServiceFactory.create_ai_service(self.ai_provider, self.api_key)
        
        # Initialize analysis repository
        self.analysis_repository = analysis_repository or FileAnalysisRepository()
    
    async def analyze_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation using AI and return structured analysis with ID."""
        try:
            conversation_id = conversation_data.get("conversation_id", "unknown")
            
            if not self.ai_service:
                # Fallback to simulated analysis (returns structured JSON)
                analysis_data = await self._simulate_analysis_structured(conversation_data)
            else:
                # Load analysis prompts
                analysis_prompts = self._load_analysis_prompts()
                
                # Build conversation context for analysis
                conversation_context = self._build_conversation_context(conversation_data)
                
                # Generate analysis using OpenAI
                analysis_prompt = self._build_analysis_prompt(analysis_prompts, conversation_context)
                
                analysis_response = await self.ai_service.generate_conversation_response(
                    system_prompt=analysis_prompt,
                    user_message=f"Analiza la siguiente conversación de ventas:\n\n{conversation_context}",
                    conversation_history=[]
                )
                
                # Parse JSON response
                try:
                    # Clean up response (remove markdown code blocks if present)
                    cleaned_response = analysis_response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]
                    if cleaned_response.startswith("```"):
                        cleaned_response = cleaned_response[3:]
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]
                    cleaned_response = cleaned_response.strip()
                    
                    analysis_data = json.loads(cleaned_response)
                    logger.info(f"Successfully parsed JSON analysis for conversation {conversation_id}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON analysis: {e}. Falling back to simulated analysis.")
                    analysis_data = await self._simulate_analysis_structured(conversation_data)

            # Add metadata
            metadata = {
                "duration_seconds": conversation_data.get("duration_seconds", 0),
                "message_count": len(conversation_data.get("messages", [])),
                "persona_name": conversation_data.get("persona_name", "Unknown"),
                "context_id": conversation_data.get("context_id", "unknown"),
                "conversation_metadata": conversation_data.get("metadata", {})
            }
            
            # Build complete analysis object
            complete_analysis = {
                "conversation_id": conversation_id,
                "overall_score": analysis_data.get("overall_score", 0),
                "summary": analysis_data.get("summary", ""),
                "strengths": analysis_data.get("strengths", []),
                "areas_for_improvement": analysis_data.get("areas_for_improvement", []),
                "recommendations": analysis_data.get("recommendations", []),
                "metrics": analysis_data.get("metrics", {}),
                "metadata": metadata
            }

            # Save analysis to file
            analysis_id = await self.analysis_repository.save_analysis(conversation_id, complete_analysis)

            logger.info(f"Analysis completed and saved: {analysis_id} for conversation {conversation_id}")
            
            return {
                "analysis_id": analysis_id,
                "conversation_id": conversation_id,
                **complete_analysis
            }
        
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            # Fallback to simulated analysis
            analysis_data = await self._simulate_analysis_structured(conversation_data)
            
            metadata = {
                "duration_seconds": conversation_data.get("duration_seconds", 0),
                "message_count": len(conversation_data.get("messages", [])),
                "persona_name": conversation_data.get("persona_name", "Unknown"),
                "context_id": conversation_data.get("context_id", "unknown"),
                "conversation_metadata": conversation_data.get("metadata", {})
            }
            
            complete_analysis = {
                "conversation_id": conversation_id,
                "overall_score": analysis_data.get("overall_score", 0),
                "summary": analysis_data.get("summary", ""),
                "strengths": analysis_data.get("strengths", []),
                "areas_for_improvement": analysis_data.get("areas_for_improvement", []),
                "recommendations": analysis_data.get("recommendations", []),
                "metrics": analysis_data.get("metrics", {}),
                "metadata": metadata
            }
            
            analysis_id = await self.analysis_repository.save_analysis(conversation_id, complete_analysis)
            
            return {
                "analysis_id": analysis_id,
                "conversation_id": conversation_id,
                **complete_analysis
            }
    
    def _load_analysis_prompts(self) -> Dict[str, Any]:
        """Load analysis prompts from configuration."""
        try:
            prompts_path = Path("/app/config/analysis_prompts.yaml")
            with open(prompts_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading analysis prompts: {e}")
            return {}
    
    def _build_conversation_context(self, conversation_data: Dict[str, Any]) -> str:
        """Build conversation context for analysis."""
        messages = conversation_data.get('messages', [])
        duration_seconds = conversation_data.get('duration_seconds', 0)
        persona_name = conversation_data.get('persona_name', 'Cliente')
        
        # Format duration
        duration_minutes = duration_seconds // 60
        duration_seconds = duration_seconds % 60
        
        context = f"**CONVERSACIÓN DE VENTAS**\n"
        context += f"**Cliente:** {persona_name}\n"
        context += f"**Duración:** {duration_minutes}m {duration_seconds}s\n"
        context += f"**Número de intercambios:** {len(messages)}\n\n"
        context += "**TRANSCRIPCIÓN COMPLETA:**\n\n"
        
        for i, message in enumerate(messages, 1):
            role = "VENDEDOR" if message.get('role') == 'user' else "CLIENTE"
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            
            context += f"**{i}. {role}** ({timestamp}):\n"
            context += f"{content}\n\n"
        
        return context
    
    def _build_analysis_prompt(self, analysis_prompts: Dict[str, Any], conversation_context: str) -> str:
        """Build the analysis prompt using the configuration."""
        conversation_analysis = analysis_prompts.get('conversation_analysis', {})
        evaluation_criteria = analysis_prompts.get('evaluation_criteria', {})
        response_format = analysis_prompts.get('response_format', {})
        
        prompt = f"""# INSTRUCCIONES PARA ANÁLISIS DE CONVERSACIÓN DE VENTAS

{conversation_analysis.get('instructions', '')}

## CRITERIOS DE EVALUACIÓN:

"""
        
        for category, details in evaluation_criteria.items():
            prompt += f"### {details.get('name', category.upper())} (Peso: {details.get('weight', 0)}%)\n"
            for aspect in details.get('aspects', []):
                prompt += f"- {aspect}\n"
            prompt += "\n"
        
        # Build response format section from configuration
        response_template = response_format.get('template', '')
        response_instructions = response_format.get('instructions', [])
        
        prompt += f"""
## FORMATO DE RESPUESTA REQUERIDO:

{response_template}

**IMPORTANTE:** 
"""
        
        for instruction in response_instructions:
            prompt += f"- {instruction}\n"
        
        prompt += f"""
## CONVERSACIÓN A ANALIZAR:
{conversation_context}"""
        
        return prompt
    
    async def _simulate_analysis_structured(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate analysis for MVP - returns structured JSON."""
        messages = conversation_data.get('messages', [])
        duration_seconds = conversation_data.get('duration_seconds', 0)
        persona_name = conversation_data.get('persona_name', 'Cliente')
        
        # Calculate basic metrics
        message_count = len(messages)
        
        # Simulate scores based on conversation metrics
        opening_score = min(10, max(3, message_count // 2))
        needs_score = min(10, max(4, message_count // 2 + 1))
        value_score = min(10, max(5, message_count // 2 + 2))
        objections_score = min(10, max(3, message_count // 3))
        closing_score = min(10, max(4, message_count // 3 + 1))
        communication_score = min(10, max(5, min(8, duration_seconds // 30)))
        
        # Calculate overall score (weighted average)
        overall_score = round(
            (opening_score * 0.20 + 
             needs_score * 0.25 + 
             value_score * 0.20 + 
             objections_score * 0.15 + 
             closing_score * 0.15 + 
             communication_score * 0.05) * 10
        ) / 10
        
        return {
            "overall_score": overall_score,
            "summary": f"Conversación profesional de {message_count} intercambios con {persona_name}. El vendedor demostró habilidades consistentes con áreas específicas de mejora identificadas.",
            "strengths": [
                "Saludo profesional y presentación clara al inicio",
                "Uso de preguntas abiertas para entender necesidades",
                "Mantuvo un tono profesional durante toda la conversación"
            ],
            "areas_for_improvement": [
                "Profundizar más en la calificación del prospecto (BANT)",
                "Presentar más casos de éxito o referencias relevantes",
                "Mejorar las técnicas de cierre con próximos pasos más claros"
            ],
            "recommendations": [
                "Practicar técnicas de calificación BANT (Budget, Authority, Need, Timeline)",
                "Crear un banco de casos de éxito por industria y tipo de cliente",
                "Desarrollar un framework de cierre consultivo con múltiples próximos pasos"
            ],
            "metrics": {
                "opening_qualification": opening_score,
                "needs_assessment": needs_score,
                "value_presentation": value_score,
                "objection_handling": objections_score,
                "closing_effectiveness": closing_score,
                "communication_rapport": communication_score
            }
        }

