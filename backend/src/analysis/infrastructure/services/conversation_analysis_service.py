"""
Conversation Analysis Service for real-time analysis.
"""
import logging
from typing import Dict, Any, List
import yaml
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
        """Analyze conversation using AI and return analysis with ID."""
        try:
            conversation_id = conversation_data.get("conversation_id", "unknown")
            
            if not self.ai_service:
                # Fallback to simulated analysis
                analysis_text = await self._simulate_analysis(conversation_data)
            else:
                # Load analysis prompts
                analysis_prompts = self._load_analysis_prompts()
                
                # Build conversation context for analysis
                conversation_context = self._build_conversation_context(conversation_data)
                
                # Generate analysis using OpenAI
                analysis_prompt = self._build_analysis_prompt(analysis_prompts, conversation_context)
                
                analysis_text = await self.ai_service.generate_conversation_response(
                    system_prompt=analysis_prompt,
                    user_message=f"Analiza la siguiente conversación de ventas:\n\n{conversation_context}",
                    conversation_history=[]
                )

            # Save analysis to file
            analysis_id = await self.analysis_repository.save_analysis(conversation_id, {
                **conversation_data,
                "analysis": analysis_text
            })

            logger.info(f"Analysis completed and saved: {analysis_id} for conversation {conversation_id}")
            
            return {
                "analysis_id": analysis_id,
                "analysis": analysis_text,
                "conversation_id": conversation_id
            }
        
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            # Fallback to simulated analysis
            analysis_text = await self._simulate_analysis(conversation_data)
            analysis_id = await self.analysis_repository.save_analysis(
                conversation_data.get("conversation_id", "unknown"), 
                {**conversation_data, "analysis": analysis_text}
            )
            return {
                "analysis_id": analysis_id,
                "analysis": analysis_text,
                "conversation_id": conversation_data.get("conversation_id", "unknown")
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
        analysis_template = analysis_prompts.get('analysis_template', '')
        
        prompt = f"""# INSTRUCCIONES PARA ANÁLISIS DE CONVERSACIÓN DE VENTAS

{conversation_analysis.get('instructions', '')}

## CRITERIOS DE EVALUACIÓN:

"""
        
        for category, details in evaluation_criteria.items():
            prompt += f"### {details.get('name', category.upper())} (Peso: {details.get('weight', 0)}%)\n"
            for aspect in details.get('aspects', []):
                prompt += f"- {aspect}\n"
            prompt += "\n"
        
        prompt += f"""
## TEMPLATE DE RESPUESTA:
{analysis_template}

## CONVERSACIÓN A ANALIZAR:
{conversation_context}

---

**IMPORTANTE:** Responde ÚNICAMENTE en formato Markdown usando el template proporcionado. No incluyas texto adicional antes o después del análisis."""
        
        return prompt
    
    async def _simulate_analysis(self, conversation_data: Dict[str, Any]) -> str:
        """Simulate analysis for MVP - returns markdown analysis."""
        messages = conversation_data.get('messages', [])
        duration_seconds = conversation_data.get('duration_seconds', 0)
        persona_name = conversation_data.get('persona_name', 'Cliente')
        
        # Calculate basic metrics
        message_count = len(messages)
        duration_minutes = duration_seconds // 60
        duration_seconds = duration_seconds % 60
        
        # Simulate scores
        opening_score = min(8, max(5, message_count // 2))
        needs_score = min(9, max(6, message_count // 3))
        value_score = min(7, max(4, message_count // 4))
        objections_score = min(8, max(5, message_count // 5))
        closing_score = min(7, max(4, message_count // 6))
        communication_score = min(8, max(6, int(duration_seconds / 60)))
        
        overall_score = (opening_score + needs_score + value_score + objections_score + closing_score + communication_score) // 6
        
        # Determine performance level
        if overall_score >= 8:
            performance_level = "Avanzado"
        elif overall_score >= 6:
            performance_level = "Intermedio"
        else:
            performance_level = "Principiante"
        
        return f"""# 📊 Análisis de Conversación de Ventas

## 🎯 Resumen Ejecutivo
**Duración:** {duration_minutes}m {duration_seconds}s  
**Calificación General:** {overall_score}/10  
**Nivel:** {performance_level}

---

## 📈 Evaluación por Categorías

### 1. 🚀 Apertura y Calificación ({opening_score}/10)
**Fortalezas:**
- Saludo profesional y presentación clara
- Establecimiento de rapport inicial efectivo

**Áreas de Mejora:**
- Mejorar calificación del prospecto
- Identificar más claramente la persona decisora

### 2. 🔍 Evaluación de Necesidades ({needs_score}/10)
**Fortalezas:**
- Preguntas abiertas bien estructuradas
- Escucha activa demostrada

**Áreas de Mejora:**
- Profundizar más en los puntos de dolor específicos
- Validar mejor las necesidades identificadas

### 3. 💎 Presentación de Valor ({value_score}/10)
**Fortalezas:**
- Conexión clara entre necesidades y beneficios
- Uso de ejemplos relevantes

**Áreas de Mejora:**
- Cuantificar mejor el ROI
- Usar más storytelling efectivo

### 4. 🛡️ Manejo de Objeciones ({objections_score}/10)
**Fortalezas:**
- Identificación temprana de preocupaciones
- Respuestas estructuradas

**Áreas de Mejora:**
- Usar más evidencia y testimonios
- Convertir objeciones en oportunidades

### 5. 🎯 Cierre y Próximos Pasos ({closing_score}/10)
**Fortalezas:**
- Definición clara de próximos pasos
- Compromisos mutuos establecidos

**Áreas de Mejora:**
- Más intentos de cierre apropiados
- Identificar mejor las señales de compra

### 6. 💬 Comunicación y Rapport ({communication_score}/10)
**Fortalezas:**
- Claridad en la comunicación
- Construcción de confianza efectiva

**Áreas de Mejora:**
- Optimizar el manejo del tiempo
- Mejorar el profesionalismo general

---

## 🏆 Principales Fortalezas
- Comunicación clara y profesional
- Establecimiento de rapport efectivo
- Estructura de conversación bien organizada

## ⚠️ Áreas Críticas de Mejora
- Profundizar en la calificación del prospecto
- Mejorar el manejo de objeciones
- Optimizar las técnicas de cierre

## 📚 Recomendaciones de Aprendizaje

### 📖 Libros Recomendados
- **SPIN Selling** - Neil Rackham
- **The Challenger Sale** - Matthew Dixon
- **Never Split the Difference** - Chris Voss

### 🎥 Canales de YouTube
- Sales Training by Sandler
- The Sales Evangelist
- HubSpot Sales

### 📰 Artículos Específicos
- Técnicas de calificación de prospectos
- Manejo efectivo de objeciones
- Técnicas de cierre consultivo

---

## 🎯 Plan de Acción Inmediato
1. Practicar técnicas de calificación más profundas
2. Desarrollar respuestas estructuradas para objeciones comunes
3. Mejorar las técnicas de cierre consultivo

## 💡 Próximos Pasos Sugeridos
- Implementar un proceso de calificación más sistemático
- Crear una biblioteca de respuestas a objeciones
- Practicar diferentes técnicas de cierre
"""

