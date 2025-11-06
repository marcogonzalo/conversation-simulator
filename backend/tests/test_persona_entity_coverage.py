"""
Tests for Persona entity
"""
import pytest

from src.persona.domain.entities.persona import Persona
from src.persona.domain.value_objects.persona_id import PersonaId
from src.persona.domain.value_objects.personality_traits import PersonalityTraits


class TestPersonaEntityCoverage:
    """Tests for Persona entity"""
    
    @pytest.fixture
    def persona_id(self):
        """Create persona ID"""
        return PersonaId(value="test_persona")
    
    @pytest.fixture
    def personality_traits(self):
        """Create personality traits"""
        return PersonalityTraits(
            openness=0.8,
            conscientiousness=0.7,
            extraversion=0.6,
            agreeableness=0.75,
            neuroticism=0.3
        )
    
    @pytest.fixture
    def persona(self, persona_id, personality_traits):
        """Create persona instance"""
        return Persona(
            persona_id=persona_id,
            name="Test Persona",
            age=35,
            nationality="Test Nation",
            role="Test Role",
            accent="neutral",
            personality_traits=personality_traits,
            background={"industry": "Tech", "experience": "Senior"},
            goals=["Goal 1", "Goal 2"],
            pain_points=["Pain 1"],
            objections=["Objection 1"],
            budget_range="$5k-$15k"
        )
    
    def test_persona_creation(self, persona, persona_id):
        """Test persona entity creation"""
        assert persona is not None
        assert persona.id == persona_id
        assert persona.name == "Test Persona"
        assert persona.age == 35
    
    def test_persona_id_access(self, persona, persona_id):
        """Test accessing persona ID"""
        assert persona.id == persona_id
        assert str(persona.id) == str(persona_id)
    
    def test_persona_name(self, persona):
        """Test persona name"""
        assert persona.name == "Test Persona"
    
    def test_persona_age(self, persona):
        """Test persona age"""
        assert persona.age == 35
        assert isinstance(persona.age, int)
    
    def test_persona_nationality(self, persona):
        """Test persona nationality"""
        assert persona.nationality == "Test Nation"
    
    def test_persona_role(self, persona):
        """Test persona role"""
        assert persona.role == "Test Role"
    
    def test_persona_accent(self, persona):
        """Test persona accent"""
        assert persona.accent == "neutral"
    
    def test_persona_personality_traits(self, persona, personality_traits):
        """Test personality traits access"""
        assert persona.personality_traits == personality_traits
    
    def test_personality_traits_big_five(self, personality_traits):
        """Test Big Five personality traits"""
        assert personality_traits.openness == 0.8
        assert personality_traits.conscientiousness == 0.7
        assert personality_traits.extraversion == 0.6
        assert personality_traits.agreeableness == 0.75
        assert personality_traits.neuroticism == 0.3
    
    def test_personality_traits_range_validation(self):
        """Test personality traits are in valid range"""
        traits = PersonalityTraits(
            openness=0.5,
            conscientiousness=0.5,
            extraversion=0.5,
            agreeableness=0.5,
            neuroticism=0.5
        )
        
        # All should be between 0 and 1
        assert 0 <= traits.openness <= 1
        assert 0 <= traits.conscientiousness <= 1
        assert 0 <= traits.extraversion <= 1
        assert 0 <= traits.agreeableness <= 1
        assert 0 <= traits.neuroticism <= 1
    
    def test_persona_background(self, persona):
        """Test persona background"""
        assert persona.background is not None
        assert isinstance(persona.background, dict)
        assert "industry" in persona.background
    
    def test_persona_goals(self, persona):
        """Test persona goals"""
        assert persona.goals is not None
        assert isinstance(persona.goals, list)
        assert len(persona.goals) == 2
    
    def test_persona_pain_points(self, persona):
        """Test persona pain points"""
        assert persona.pain_points is not None
        assert isinstance(persona.pain_points, list)
        assert len(persona.pain_points) >= 1
    
    def test_persona_objections(self, persona):
        """Test persona objections"""
        assert persona.objections is not None
        assert isinstance(persona.objections, list)
    
    def test_persona_budget_range(self, persona):
        """Test persona budget range"""
        assert persona.budget_range == "$5k-$15k"
    
    def test_persona_id_string_representation(self, persona_id):
        """Test PersonaId string representation"""
        assert isinstance(str(persona_id), str)
    
    def test_persona_id_equality(self):
        """Test PersonaId equality"""
        id1 = PersonaId(value="same_id")
        id2 = PersonaId(value="same_id")
        id3 = PersonaId(value="different_id")
        
        assert id1.value == id2.value
        assert id1.value != id3.value
    
    def test_personality_traits_creation(self):
        """Test creating personality traits"""
        traits = PersonalityTraits(
            openness=0.9,
            conscientiousness=0.8,
            extraversion=0.7,
            agreeableness=0.6,
            neuroticism=0.5
        )
        
        assert traits is not None
    
    def test_persona_with_empty_goals(self, persona_id, personality_traits):
        """Test persona with empty goals list"""
        persona = Persona(
            persona_id=persona_id,
            name="Test",
            age=30,
            nationality="Test",
            role="Role",
            accent="neutral",
            personality_traits=personality_traits,
            background={},
            goals=[],
            pain_points=[],
            objections=[],
            budget_range="$1k-$5k"
        )
        
        assert persona.goals == []
    
    def test_persona_multiple_instances_independent(self, personality_traits):
        """Test multiple persona instances are independent"""
        persona1 = Persona(
            persona_id=PersonaId(value="persona1"),
            name="Persona 1",
            age=30,
            nationality="Nation1",
            role="Role1",
            accent="accent1",
            personality_traits=personality_traits,
            background={},
            goals=[],
            pain_points=[],
            objections=[],
            budget_range="$1k"
        )
        
        persona2 = Persona(
            persona_id=PersonaId(value="persona2"),
            name="Persona 2",
            age=40,
            nationality="Nation2",
            role="Role2",
            accent="accent2",
            personality_traits=personality_traits,
            background={},
            goals=[],
            pain_points=[],
            objections=[],
            budget_range="$2k"
        )
        
        assert persona1.id != persona2.id
        assert persona1.name != persona2.name

