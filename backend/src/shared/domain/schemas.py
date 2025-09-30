"""
YAML Schema Validation
Esquemas de validación para las tres capas del sistema de prompts
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


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


class DomainExpertise(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class TechnicalComfort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionStyle(str, Enum):
    QUICK = "quick"
    ANALYTICAL = "analytical"
    COLLABORATIVE = "collaborative"


class LearningPreference(str, Enum):
    HANDS_ON = "hands_on"
    THEORETICAL = "theoretical"
    MIXED = "mixed"


class RiskTolerance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionAuthority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExperienceLevel(str, Enum):
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"


# Capa 1: Simulation Rules Schema
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
    behavior_guidelines: Dict[str, Any]
    content_restrictions: Dict[str, Any]
    quality_metadata: Dict[str, Any]


# Capa 2: Conversation Context Schema
class ClientContext(BaseModel):
    situation: str
    budget: Optional[str] = None
    timeline: Optional[str] = None
    property_type: Optional[str] = None
    priority: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None


class Needs(BaseModel):
    primary: List[str]
    secondary: List[str]


class ConversationContextSchema(BaseModel):
    id: str
    name: str
    topic: str
    client_context: ClientContext
    needs: Needs
    pain_points: List[str]
    objections: List[str]
    decision_factors: List[str]
    conversation_flow: List[str]
    instructions: List[str]
    metadata: Dict[str, Any]


# Capa 3: Persona Details Schema
class Identity(BaseModel):
    age: int
    nationality: str
    role: str
    experience: str
    team_size: Optional[int] = None
    company_size: Optional[int] = None
    accent: str
    voice_id: str


class Personality(BaseModel):
    traits: List[str]
    enthusiasm_level: EnthusiasmLevel
    risk_tolerance: RiskTolerance
    decision_style: DecisionStyle
    learning_preference: LearningPreference


class Communication(BaseModel):
    language: str
    accent: str
    formality: FormalityLevel
    response_length: ResponseLength
    question_style: QuestionStyle
    energy_level: EnthusiasmLevel


class Knowledge(BaseModel):
    domain_expertise: DomainExpertise
    technical_comfort: TechnicalComfort
    experience_level: ExperienceLevel
    decision_authority: DecisionAuthority


class MeetingPreferences(BaseModel):
    format: str
    duration: str
    focus: str


class PersonaDetailsSchema(BaseModel):
    id: str
    name: str
    description: str
    identity: Identity
    personality: Personality
    communication: Communication
    characteristics: List[str]
    behavior: List[str]
    knowledge: Knowledge
    meeting_preferences: MeetingPreferences
    instructions: List[str]


# Validadores personalizados
class SchemaValidator:
    """Validador de esquemas YAML para las tres capas"""
    
    @staticmethod
    def validate_simulation_rules(data: Dict[str, Any]) -> bool:
        """Valida esquema de simulation rules"""
        try:
            SimulationRulesSchema(**data)
            return True
        except Exception as e:
            print(f"Simulation rules validation error: {e}")
            return False
    
    @staticmethod
    def validate_conversation_context(data: Dict[str, Any]) -> bool:
        """Valida esquema de conversation context"""
        try:
            ConversationContextSchema(**data)
            return True
        except Exception as e:
            print(f"Conversation context validation error: {e}")
            return False
    
    @staticmethod
    def validate_persona_details(data: Dict[str, Any]) -> bool:
        """Valida esquema de persona details"""
        try:
            PersonaDetailsSchema(**data)
            return True
        except Exception as e:
            print(f"Persona details validation error: {e}")
            return False
    
    @staticmethod
    def validate_all_layers(simulation_rules: Dict[str, Any], 
                          conversation_context: Dict[str, Any], 
                          persona_details: Dict[str, Any]) -> Dict[str, bool]:
        """Valida todas las capas"""
        return {
            "simulation_rules": SchemaValidator.validate_simulation_rules(simulation_rules),
            "conversation_context": SchemaValidator.validate_conversation_context(conversation_context),
            "persona_details": SchemaValidator.validate_persona_details(persona_details)
        }
