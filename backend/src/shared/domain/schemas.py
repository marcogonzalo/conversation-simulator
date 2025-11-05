"""
YAML Schema Validation - 5 Layer Architecture
Esquemas de validación para el sistema de configuración de 5 capas
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# ENUMS for Type Safety
# ============================================================================

class ResponseLength(str, Enum):
    CONCISE = "concise"
    DETAILED = "detailed"
    MIXED = "mixed"


class FormalityLevel(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    MIXED = "mixed"


class EnthusiasmLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class QuestionStyle(str, Enum):
    DIRECT = "direct"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"


# ============================================================================
# Capa 1: Simulation Rules Schema (Sin cambios - Global)
# ============================================================================

class LLMIdentity(BaseModel):
    role: str
    behavior: str
    perspective: str


class SimulationRulesSchema(BaseModel):
    id: str
    version: str
    description: str
    llm_identity: LLMIdentity
    safety_rules: List[str]
    realism_standards: Dict[str, Any]
    content_restrictions: Dict[str, Any]
    response_format: Optional[Dict[str, Any]] = None
    objection_timing: Optional[List[str]] = None
    implicit_behaviors: Optional[List[str]] = None
    silence_handling: Optional[List[str]] = None
    escalation_rules: Optional[List[str]] = None
    quality_metadata: Dict[str, Any]
    # Deprecated fields (for backward compatibility)
    behavior_guidelines: Optional[Dict[str, Any]] = None


# ============================================================================
# Capa 2: Industry Context Schema (Nuevo)
# ============================================================================

class Industry(BaseModel):
    sector: str
    subsector: str
    market: str


class SaleType(BaseModel):
    product_type: str
    complexity: str  # transaccional, consultiva, enterprise, técnica
    cycle_duration: str  # corto, medio, largo


class BudgetSituation(BaseModel):
    typical_range: str
    ticket_size: str  # bajo, medio, alto
    budget_flexibility: str  # limitado, definido, flexible
    financing_common: bool


class DecisionStructure(BaseModel):
    typical_authority: str
    typical_roles: List[str]
    typical_participants: int
    decision_process: str


class ClientState(BaseModel):
    typical_temperature: str
    typical_journey_phase: str
    typical_previous_experience: str


class Urgency(BaseModel):
    default_level: str
    typical_timeline: str


class Terminology(BaseModel):
    key_terms: List[str]
    common_concerns: List[str]


class DecisionFactors(BaseModel):
    critical: List[str]
    important: List[str]
    nice_to_have: List[str]


class IndustryContextSchema(BaseModel):
    id: str
    name: str
    version: str
    industry: Industry
    sale_type: SaleType
    budget_situation: BudgetSituation
    client_state: ClientState
    urgency: Urgency
    terminology: Terminology
    decision_factors: DecisionFactors
    objection_mappings: Optional[Dict[str,
                                      Union[bool, List[str], None]]] = None
    metadata: Dict[str, Any]


# ============================================================================
# Capa 3: Sales Situation Schema (Nuevo)
# ============================================================================

class SalesPhase(BaseModel):
    phase: str  # descubrimiento, presentacion, manejo_objeciones, cierre
    phase_name: str
    objective: str
    key_activities: List[str]


class UrgencyLevel(BaseModel):
    level: str  # baja, media, alta
    description: str
    timeline: str
    implication: str
    timeline_expectation: str
    urgency_drivers: Optional[List[str]] = None


class PrimaryObjection(BaseModel):
    type: str  # price, value, fit, risk, trust, need, competition, technical
    label: str
    description: str
    generic_expressions: List[str]  # Expresiones genéricas
    handling_approach: List[str]


class SituationClientState(BaseModel):
    temperature: str
    temperature_description: str
    buyer_journey_phase: str
    journey_description: str
    previous_experience: str
    experience_description: str
    experience_impact: str


class SituationDecisionStructure(BaseModel):
    authority: str
    authority_description: str
    role: str
    role_description: str
    participants: Union[int, str]  # Can be "1-2" or just 1
    participants_description: str
    decision_timeline: str
    approval_required: bool
    approval_from: Optional[str] = None


class ConversationFlow(BaseModel):
    opening: Optional[List[str]] = None
    discovery: Optional[List[str]] = None
    qualification: Optional[List[str]] = None
    presentation: Optional[List[str]] = None
    value_demonstration: Optional[List[str]] = None
    objection_handling: Optional[List[str]] = None
    closing: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    recap: Optional[List[str]] = None
    trust_building: Optional[List[str]] = None
    risk_mitigation: Optional[List[str]] = None
    commitment: Optional[List[str]] = None
    objection_exploration: Optional[List[str]] = None


class ClientBehavior(BaseModel):
    engagement_style: str
    information_seeking: str
    skepticism_level: str
    typical_questions: List[str]
    typical_statements: List[str]


class SalesSituationSchema(BaseModel):
    id: str
    name: str
    version: str
    sales_phase: SalesPhase
    urgency: UrgencyLevel
    primary_objection: PrimaryObjection
    client_state: SituationClientState
    decision_structure: SituationDecisionStructure
    conversation_flow: ConversationFlow
    client_behavior: ClientBehavior
    success_metrics: List[str]
    metadata: Dict[str, Any]


# ============================================================================
# Capa 4: Client Psychology Schema (Nuevo)
# ============================================================================

class Personality(BaseModel):
    primary_type: str  # analitico, expresivo, esceptico, etc.
    description: str
    traits: List[str]
    secondary_traits: List[str]


class EmotionalState(BaseModel):
    primary: str
    description: str
    manifestation: List[str]
    triggers_positive: List[str]
    triggers_negative: List[str]


class ProcessingStyle(BaseModel):
    primary: str  # analitico, emocional, practico, conceptual, visual
    description: str
    information_preference: List[str]
    decision_approach: List[str]
    communication_preference: List[str]


class ClientProfile(BaseModel):
    personality: Personality
    emotional_state: EmotionalState
    processing_style: ProcessingStyle


class Difficulty(BaseModel):
    level: str  # muy_facil, facil, medio, dificil, muy_dificil
    description: str
    characteristics: List[str]
    seller_requirements: List[str]


class Cooperation(BaseModel):
    level: str  # muy_cooperativo, cooperativo, neutral, reservado, desafiante
    description: str
    behavior: List[str]
    trust_building: List[str]


class ObjectionIntensity(BaseModel):
    level: str  # suave, moderada, fuerte, encadenada
    description: str
    objection_style: List[str]
    handling_strategy: List[str]


class ChallengeLevel(BaseModel):
    difficulty: Difficulty
    cooperation: Cooperation
    objection_intensity: ObjectionIntensity


class ConversationBehavior(BaseModel):
    pace: str
    question_frequency: str
    question_depth: str
    typical_behaviors: List[str]
    red_flags_to_avoid: List[str]


class LanguagePatterns(BaseModel):
    typical_phrases: List[str]
    question_examples: List[str]


class ClientPsychologySchema(BaseModel):
    id: str
    name: str
    version: str
    client_profile: ClientProfile
    challenge_level: ChallengeLevel
    conversation_behavior: ConversationBehavior
    language_patterns: LanguagePatterns
    metadata: Dict[str, Any]


# ============================================================================
# Capa 5: Client Identity Schema (Nuevo)
# ============================================================================

class Identity(BaseModel):
    age: int
    nationality: str
    role: str
    experience_years: int
    industry: str
    team_size: Optional[int] = None
    company_size: Optional[int] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None


class VoiceConfig(BaseModel):
    accent: str
    voice_id: str
    language: str
    dialect: str


class CommunicationStyle(BaseModel):
    formality: str
    response_length: str
    question_style: str
    energy_level: str
    warmth: Optional[str] = None
    precision: Optional[str] = None
    pace: Optional[str] = None


class ConversationSpecifics(BaseModel):
    greeting_style: str
    typical_opening: str
    expressions: Dict[str, List[str]]


class PersonalContext(BaseModel):
    family_situation: str
    location: str
    work_mode: str
    experience_with_technology: str


class ClientIdentitySchema(BaseModel):
    id: str
    name: str
    version: str
    identity: Identity
    voice_config: VoiceConfig
    communication_style: CommunicationStyle
    unique_characteristics: List[str]
    personal_context: Optional[PersonalContext] = None
    conversation_specifics: ConversationSpecifics
    typical_topics: List[str]
    references: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


# ============================================================================
# Schema Validator for All Layers
# ============================================================================

class SchemaValidator:
    """Validador de esquemas YAML para las 5 capas"""

    @staticmethod
    def validate_simulation_rules(data: Dict[str, Any]) -> bool:
        """Valida esquema de simulation rules (Capa 1)"""
        try:
            SimulationRulesSchema(**data)
            return True
        except Exception as e:
            # Log error but don't print to console
            return False

    @staticmethod
    def validate_industry_context(data: Dict[str, Any]) -> bool:
        """Valida esquema de industry context (Capa 2)"""
        try:
            IndustryContextSchema(**data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def validate_sales_situation(data: Dict[str, Any]) -> bool:
        """Valida esquema de sales situation (Capa 3)"""
        try:
            SalesSituationSchema(**data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def validate_client_psychology(data: Dict[str, Any]) -> bool:
        """Valida esquema de client psychology (Capa 4)"""
        try:
            ClientPsychologySchema(**data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def validate_client_identity(data: Dict[str, Any]) -> bool:
        """Valida esquema de client identity (Capa 5)"""
        try:
            ClientIdentitySchema(**data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def validate_all_layers(
        simulation_rules: Dict[str, Any],
        industry_context: Dict[str, Any],
        sales_situation: Dict[str, Any],
        client_psychology: Dict[str, Any],
        client_identity: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Valida todas las 5 capas"""
        return {
            "simulation_rules": SchemaValidator.validate_simulation_rules(simulation_rules),
            "industry_context": SchemaValidator.validate_industry_context(industry_context),
            "sales_situation": SchemaValidator.validate_sales_situation(sales_situation),
            "client_psychology": SchemaValidator.validate_client_psychology(client_psychology),
            "client_identity": SchemaValidator.validate_client_identity(client_identity)
        }


# ============================================================================
# Backwards Compatibility Validators (Legacy 3-layer system)
# ============================================================================

class ConversationContextSchema(BaseModel):
    """Legacy schema for backwards compatibility"""
    id: str
    name: str
    topic: str
    client_context: Dict[str, Any]
    needs: Dict[str, List[str]]
    pain_points: List[str]
    objections: List[str]
    decision_factors: List[str]
    conversation_flow: List[str]
    instructions: List[str]
    metadata: Dict[str, Any]


class PersonaDetailsSchema(BaseModel):
    """Legacy schema for backwards compatibility"""
    id: str
    name: str
    description: str
    identity: Dict[str, Any]
    personality: Dict[str, Any]
    communication: Dict[str, Any]
    characteristics: List[str]
    behavior: List[str]
    knowledge: Dict[str, Any]
    meeting_preferences: Dict[str, Any]
    instructions: List[str]


class LegacySchemaValidator:
    """Validators for legacy 3-layer system"""

    @staticmethod
    def validate_conversation_context(data: Dict[str, Any]) -> bool:
        """Valida esquema de conversation context (legacy)"""
        try:
            ConversationContextSchema(**data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def validate_persona_details(data: Dict[str, Any]) -> bool:
        """Valida esquema de persona details (legacy)"""
        try:
            PersonaDetailsSchema(**data)
            return True
        except Exception as e:
            return False
