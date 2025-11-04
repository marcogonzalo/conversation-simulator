"""
Semantic Validator for 5-Layer Configuration
Validates semantic consistency across configuration layers to prevent incoherent combinations
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SemanticValidator:
    """Validates semantic consistency across 5-layer configuration."""
    
    @staticmethod
    def validate_consistency(
        industry: Dict[str, Any],
        situation: Dict[str, Any],
        psychology: Dict[str, Any],
        identity: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validates semantic consistency across layers.
        
        Args:
            industry: Industry context configuration (Layer 2)
            situation: Sales situation configuration (Layer 3)
            psychology: Client psychology configuration (Layer 4)
            identity: Client identity configuration (Layer 5)
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
            - is_valid: True if no critical issues found
            - warnings: List of warning messages (empty if perfect)
        """
        warnings = []
        
        # ================================================================
        # Rule 1: Urgency vs Timeline Consistency
        # ================================================================
        urgency_level = situation.get('urgency', {}).get('level', 'media')
        timeline = situation.get('urgency', {}).get('timeline_expectation', '')
        
        # High urgency with long timeline is inconsistent
        if urgency_level == 'alta' and ('6+' in timeline or 'largo' in timeline.lower() or 'meses' in timeline.lower()):
            warnings.append(
                f"⚠️ Inconsistencia detectada: Urgencia '{urgency_level}' con timeline largo '{timeline}'. "
                f"Urgencia alta típicamente requiere decisión en días/semanas, no meses."
            )
        
        # Low urgency with immediate timeline is inconsistent
        if urgency_level == 'baja' and ('inmediato' in timeline.lower() or 'días' in timeline.lower() or '1-2' in timeline):
            warnings.append(
                f"⚠️ Inconsistencia detectada: Urgencia '{urgency_level}' con timeline corto '{timeline}'. "
                f"Urgencia baja típicamente implica timeline de meses, no días."
            )
        
        # ================================================================
        # Rule 2: Psychology Difficulty vs Cooperation Level
        # ================================================================
        difficulty_level = psychology.get('challenge_level', {}).get('difficulty', {}).get('level', 'medio')
        cooperation_level = psychology.get('challenge_level', {}).get('cooperation', {}).get('level', 'neutral')
        
        # Very difficult client who is very cooperative is unusual
        if difficulty_level in ['muy_dificil', 'dificil'] and cooperation_level == 'muy_cooperativo':
            warnings.append(
                f"⚠️ Combinación inusual: Cliente con dificultad '{difficulty_level}' pero cooperación '{cooperation_level}'. "
                f"Clientes difíciles típicamente son reservados o desafiantes, no muy cooperativos."
            )
        
        # Very easy client who is hostile/challenging is unusual
        if difficulty_level in ['muy_facil', 'facil'] and cooperation_level in ['desafiante', 'hostil']:
            warnings.append(
                f"⚠️ Combinación inusual: Cliente con dificultad '{difficulty_level}' pero cooperación '{cooperation_level}'. "
                f"Clientes fáciles típicamente son cooperativos, no desafiantes."
            )
        
        # ================================================================
        # Rule 3: Sales Phase vs Objection Type Coherence
        # ================================================================
        phase = situation.get('sales_phase', {}).get('phase', '')
        objection_type = situation.get('primary_objection', {}).get('type', '')
        
        # Unusual phase-objection combinations
        unusual_combinations = {
            ('descubrimiento', 'technical'): "Objeciones técnicas son raras en descubrimiento inicial",
            ('prospección', 'technical'): "Objeciones técnicas son raras en prospección inicial",
            ('cierre', 'need'): "En fase de cierre no se cuestiona la necesidad (ya debería estar clara)",
            ('cierre', 'fit'): "Objeciones de ajuste deberían resolverse antes del cierre",
        }
        
        if (phase, objection_type) in unusual_combinations:
            reason = unusual_combinations[(phase, objection_type)]
            warnings.append(
                f"⚠️ Combinación inusual: Fase '{phase}' con objeción tipo '{objection_type}'. "
                f"{reason}"
            )
        
        # ================================================================
        # Rule 4: Industry Budget Flexibility vs Price Objection
        # ================================================================
        budget_flex = industry.get('budget_situation', {}).get('budget_flexibility', '')
        
        if budget_flex == 'alto' and objection_type == 'price':
            warnings.append(
                f"⚠️ Nota: Cliente con flexibilidad presupuestaria '{budget_flex}' presenta objeción de precio. "
                f"Asegúrate de que esto tenga sentido en el contexto (ej: objeción estratégica, no real)."
            )
        
        # ================================================================
        # Rule 5: Processing Style vs Response Length
        # ================================================================
        processing = psychology.get('client_profile', {}).get('processing_style', {}).get('primary', '')
        response_length = identity.get('communication_style', {}).get('response_length', '')
        
        # Analytical style with concise responses is contradictory
        if processing == 'analitico' and response_length == 'concise':
            warnings.append(
                f"⚠️ Contradicción: Estilo de procesamiento '{processing}' con respuestas '{response_length}'. "
                f"Clientes analíticos típicamente prefieren respuestas detalladas con datos."
            )
        
        # Emotional style with very detailed responses is unusual
        if processing == 'emocional' and response_length == 'detailed':
            warnings.append(
                f"⚠️ Combinación inusual: Estilo '{processing}' con respuestas muy detalladas. "
                f"Clientes emocionales típicamente prefieren respuestas concisas y directas."
            )
        
        # ================================================================
        # Rule 6: Objection Intensity vs Cooperation Level
        # ================================================================
        objection_intensity = psychology.get('challenge_level', {}).get('objection_intensity', {}).get('level', 'moderada')
        
        # Strong objections with very cooperative attitude is contradictory
        if objection_intensity in ['fuerte', 'encadenada'] and cooperation_level == 'muy_cooperativo':
            warnings.append(
                f"⚠️ Contradicción: Intensidad de objeción '{objection_intensity}' con cooperación '{cooperation_level}'. "
                f"Objeciones fuertes típicamente vienen de clientes reservados o desafiantes."
            )
        
        # ================================================================
        # Rule 7: Experience Level vs Question Depth
        # ================================================================
        previous_experience = situation.get('client_state', {}).get('previous_experience', 'basica')
        question_depth = psychology.get('conversation_behavior', {}).get('question_depth', 'media')
        
        # No experience with very profound questions is unusual
        if previous_experience in ['ninguna', 'ninguna_o_basica'] and question_depth in ['muy_profunda', 'profunda']:
            warnings.append(
                f"⚠️ Combinación inusual: Experiencia '{previous_experience}' con profundidad de preguntas '{question_depth}'. "
                f"Clientes sin experiencia típicamente hacen preguntas básicas o superficiales."
            )
        
        # Extensive evaluation with superficial questions is contradictory
        if previous_experience == 'evaluacion_completada' and question_depth == 'superficial':
            warnings.append(
                f"⚠️ Contradicción: Cliente con '{previous_experience}' hace preguntas superficiales. "
                f"Si completó evaluación, debería hacer preguntas más profundas."
            )
        
        # ================================================================
        # Final Validation Result
        # ================================================================
        is_valid = len(warnings) == 0
        
        if is_valid:
            logger.info("✅ Validación semántica: Sin inconsistencias detectadas")
        else:
            logger.warning(f"⚠️ Validación semántica: {len(warnings)} advertencias encontradas")
        
        return is_valid, warnings
    
    @staticmethod
    def format_warnings_for_display(warnings: List[str]) -> str:
        """
        Formats warnings for console/log display.
        
        Args:
            warnings: List of warning messages
        
        Returns:
            Formatted string with all warnings
        """
        if not warnings:
            return "✅ Configuración semánticamente coherente"
        
        formatted = f"⚠️ Se encontraron {len(warnings)} advertencias de coherencia:\n"
        for i, warning in enumerate(warnings, 1):
            formatted += f"  {i}. {warning}\n"
        
        return formatted.strip()

