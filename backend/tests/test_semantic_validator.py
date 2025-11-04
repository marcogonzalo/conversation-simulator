"""
Tests for Semantic Validator
Tests cross-layer validation rules to ensure configuration coherence
"""

import pytest
from src.shared.domain.semantic_validator import SemanticValidator


class TestSemanticValidator:
    """Test suite for semantic validation across configuration layers."""
    
    # ================================================================
    # Rule 1: Urgency vs Timeline
    # ================================================================
    
    def test_high_urgency_with_short_timeline_is_valid(self):
        """High urgency with short timeline should be valid."""
        industry = {}
        situation = {
            'urgency': {
                'level': 'alta',
                'timeline_expectation': '1-2 semanas'
            },
            'sales_phase': {'phase': 'cierre'},
            'primary_objection': {'type': 'price'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'neutral'}
            },
            'client_profile': {'processing_style': {'primary': 'practico'}},
            'conversation_behavior': {'question_depth': 'media'}
        }
        identity = {
            'communication_style': {'response_length': 'mixed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is True
        assert len(warnings) == 0
    
    def test_high_urgency_with_long_timeline_is_invalid(self):
        """High urgency with long timeline (6+ months) should generate warning."""
        industry = {}
        situation = {
            'urgency': {
                'level': 'alta',
                'timeline_expectation': '6+ meses para decisión'
            },
            'sales_phase': {'phase': 'descubrimiento'},
            'primary_objection': {'type': 'price'},
            'client_state': {'previous_experience': 'basica'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'neutral'}
            },
            'client_profile': {'processing_style': {'primary': 'practico'}},
            'conversation_behavior': {'question_depth': 'media'}
        }
        identity = {
            'communication_style': {'response_length': 'mixed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('urgencia' in w.lower() and 'timeline' in w.lower() for w in warnings)
    
    def test_low_urgency_with_immediate_timeline_is_invalid(self):
        """Low urgency with immediate timeline should generate warning."""
        industry = {}
        situation = {
            'urgency': {
                'level': 'baja',
                'timeline_expectation': 'inmediato o en días'
            },
            'sales_phase': {'phase': 'descubrimiento'},
            'primary_objection': {'type': 'need'},
            'client_state': {'previous_experience': 'ninguna'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'facil'},
                'cooperation': {'level': 'muy_cooperativo'}
            },
            'client_profile': {'processing_style': {'primary': 'emocional'}},
            'conversation_behavior': {'question_depth': 'superficial'}
        }
        identity = {
            'communication_style': {'response_length': 'concise'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('urgencia' in w.lower() for w in warnings)
    
    # ================================================================
    # Rule 2: Difficulty vs Cooperation
    # ================================================================
    
    def test_difficult_client_with_challenging_cooperation_is_valid(self):
        """Difficult client with challenging cooperation is coherent."""
        industry = {}
        situation = {
            'urgency': {'level': 'media', 'timeline_expectation': '3 meses'},
            'sales_phase': {'phase': 'presentacion'},
            'primary_objection': {'type': 'value'},
            'client_state': {'previous_experience': 'intermedia'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'dificil'},
                'cooperation': {'level': 'desafiante'},
                'objection_intensity': {'level': 'fuerte'}
            },
            'client_profile': {'processing_style': {'primary': 'analitico'}},
            'conversation_behavior': {'question_depth': 'profunda'}
        }
        identity = {
            'communication_style': {'response_length': 'detailed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is True
        assert len(warnings) == 0
    
    def test_very_difficult_with_very_cooperative_is_invalid(self):
        """Very difficult client who is very cooperative is inconsistent."""
        industry = {}
        situation = {
            'urgency': {'level': 'media', 'timeline_expectation': '2 meses'},
            'sales_phase': {'phase': 'descubrimiento'},
            'primary_objection': {'type': 'trust'},
            'client_state': {'previous_experience': 'basica'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'muy_dificil'},
                'cooperation': {'level': 'muy_cooperativo'},
                'objection_intensity': {'level': 'suave'}
            },
            'client_profile': {'processing_style': {'primary': 'analitico'}},
            'conversation_behavior': {'question_depth': 'media'}
        }
        identity = {
            'communication_style': {'response_length': 'mixed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('dificultad' in w.lower() and 'cooperación' in w.lower() for w in warnings)
    
    # ================================================================
    # Rule 3: Sales Phase vs Objection Type
    # ================================================================
    
    def test_discovery_with_technical_objection_is_unusual(self):
        """Technical objection in discovery phase is unusual."""
        industry = {}
        situation = {
            'urgency': {'level': 'baja', 'timeline_expectation': '6 meses'},
            'sales_phase': {'phase': 'descubrimiento'},
            'primary_objection': {'type': 'technical'},
            'client_state': {'previous_experience': 'ninguna'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'neutral'}
            },
            'client_profile': {'processing_style': {'primary': 'practico'}},
            'conversation_behavior': {'question_depth': 'superficial'}
        }
        identity = {
            'communication_style': {'response_length': 'mixed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert any('descubrimiento' in w.lower() and 'technical' in w.lower() for w in warnings)
    
    def test_closing_with_need_objection_is_unusual(self):
        """Need objection in closing phase is unusual (should be resolved earlier)."""
        industry = {}
        situation = {
            'urgency': {'level': 'alta', 'timeline_expectation': '1 semana'},
            'sales_phase': {'phase': 'cierre'},
            'primary_objection': {'type': 'need'},
            'client_state': {'previous_experience': 'evaluacion_completada'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'cooperativo'}
            },
            'client_profile': {'processing_style': {'primary': 'emocional'}},
            'conversation_behavior': {'question_depth': 'media'}
        }
        identity = {
            'communication_style': {'response_length': 'concise'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert any('cierre' in w.lower() and 'need' in w.lower() for w in warnings)
    
    # ================================================================
    # Rule 4: Budget Flexibility vs Price Objection
    # ================================================================
    
    def test_high_budget_flexibility_with_price_objection_generates_note(self):
        """High budget flexibility with price objection should generate a note."""
        industry = {
            'budget_situation': {
                'budget_flexibility': 'alto'
            }
        }
        situation = {
            'urgency': {'level': 'media', 'timeline_expectation': '3 meses'},
            'sales_phase': {'phase': 'presentacion'},
            'primary_objection': {'type': 'price'},
            'client_state': {'previous_experience': 'basica'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'neutral'}
            },
            'client_profile': {'processing_style': {'primary': 'practico'}},
            'conversation_behavior': {'question_depth': 'media'}
        }
        identity = {
            'communication_style': {'response_length': 'mixed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        # This is a note, not a critical error
        assert len(warnings) >= 1
        assert any('flexibilidad' in w.lower() or 'precio' in w.lower() for w in warnings)
    
    # ================================================================
    # Rule 5: Processing Style vs Response Length
    # ================================================================
    
    def test_analytical_with_detailed_responses_is_valid(self):
        """Analytical processing with detailed responses is coherent."""
        industry = {}
        situation = {
            'urgency': {'level': 'baja', 'timeline_expectation': '6 meses'},
            'sales_phase': {'phase': 'descubrimiento'},
            'primary_objection': {'type': 'value'},
            'client_state': {'previous_experience': 'basica'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'reservado'}
            },
            'client_profile': {'processing_style': {'primary': 'analitico'}},
            'conversation_behavior': {'question_depth': 'profunda'}
        }
        identity = {
            'communication_style': {'response_length': 'detailed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is True
        assert len(warnings) == 0
    
    def test_analytical_with_concise_responses_is_contradictory(self):
        """Analytical processing with concise responses is contradictory."""
        industry = {}
        situation = {
            'urgency': {'level': 'media', 'timeline_expectation': '2 meses'},
            'sales_phase': {'phase': 'presentacion'},
            'primary_objection': {'type': 'fit'},
            'client_state': {'previous_experience': 'intermedia'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'reservado'}
            },
            'client_profile': {'processing_style': {'primary': 'analitico'}},
            'conversation_behavior': {'question_depth': 'profunda'}
        }
        identity = {
            'communication_style': {'response_length': 'concise'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('analitico' in w.lower() and 'concise' in w.lower() for w in warnings)
    
    # ================================================================
    # Rule 6: Objection Intensity vs Cooperation
    # ================================================================
    
    def test_strong_objections_with_very_cooperative_is_contradictory(self):
        """Strong objections from very cooperative client is contradictory."""
        industry = {}
        situation = {
            'urgency': {'level': 'media', 'timeline_expectation': '1 mes'},
            'sales_phase': {'phase': 'manejo_objeciones'},
            'primary_objection': {'type': 'risk'},
            'client_state': {'previous_experience': 'basica'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'medio'},
                'cooperation': {'level': 'muy_cooperativo'},
                'objection_intensity': {'level': 'fuerte'}
            },
            'client_profile': {'processing_style': {'primary': 'emocional'}},
            'conversation_behavior': {'question_depth': 'media'}
        }
        identity = {
            'communication_style': {'response_length': 'mixed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('objeción' in w.lower() and 'coopera' in w.lower() for w in warnings)
    
    # ================================================================
    # Rule 7: Experience vs Question Depth
    # ================================================================
    
    def test_no_experience_with_profound_questions_is_unusual(self):
        """Client with no experience asking profound questions is unusual."""
        industry = {}
        situation = {
            'urgency': {'level': 'baja', 'timeline_expectation': '6 meses'},
            'sales_phase': {'phase': 'descubrimiento'},
            'primary_objection': {'type': 'fit'},
            'client_state': {'previous_experience': 'ninguna'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'dificil'},
                'cooperation': {'level': 'reservado'}
            },
            'client_profile': {'processing_style': {'primary': 'analitico'}},
            'conversation_behavior': {'question_depth': 'muy_profunda'}
        }
        identity = {
            'communication_style': {'response_length': 'detailed'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('experiencia' in w.lower() and 'profund' in w.lower() for w in warnings)
    
    def test_completed_evaluation_with_superficial_questions_is_contradictory(self):
        """Client who completed evaluation asking superficial questions is contradictory."""
        industry = {}
        situation = {
            'urgency': {'level': 'alta', 'timeline_expectation': '2 semanas'},
            'sales_phase': {'phase': 'cierre'},
            'primary_objection': {'type': 'value'},
            'client_state': {'previous_experience': 'evaluacion_completada'}
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'bajo'},
                'cooperation': {'level': 'muy_cooperativo'}
            },
            'client_profile': {'processing_style': {'primary': 'emocional'}},
            'conversation_behavior': {'question_depth': 'superficial'}
        }
        identity = {
            'communication_style': {'response_length': 'concise'}
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 1
        assert any('evaluacion_completada' in w.lower() or 'superficial' in w.lower() for w in warnings)
    
    # ================================================================
    # Complex Scenarios (Multiple Issues)
    # ================================================================
    
    def test_multiple_inconsistencies_detected(self):
        """Configuration with multiple inconsistencies should detect all."""
        industry = {
            'budget_situation': {'budget_flexibility': 'alto'}
        }
        situation = {
            'urgency': {
                'level': 'alta',
                'timeline_expectation': '6+ meses'  # Issue 1
            },
            'sales_phase': {'phase': 'cierre'},
            'primary_objection': {'type': 'price'},  # Issue 2 (with high budget)
            'client_state': {'previous_experience': 'ninguna'}  # Issue 3
        }
        psychology = {
            'challenge_level': {
                'difficulty': {'level': 'muy_dificil'},
                'cooperation': {'level': 'muy_cooperativo'},  # Issue 4
                'objection_intensity': {'level': 'fuerte'}  # Issue 5
            },
            'client_profile': {'processing_style': {'primary': 'analitico'}},
            'conversation_behavior': {'question_depth': 'muy_profunda'}  # Issue 3 (no experience but profound)
        }
        identity = {
            'communication_style': {'response_length': 'concise'}  # Issue 6 (analytical + concise)
        }
        
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert is_valid is False
        assert len(warnings) >= 4  # Should detect multiple issues
    
    # ================================================================
    # Edge Cases
    # ================================================================
    
    def test_missing_optional_fields_does_not_crash(self):
        """Validator should handle missing optional fields gracefully."""
        industry = {}
        situation = {
            'sales_phase': {},
            'primary_objection': {}
        }
        psychology = {
            'challenge_level': {},
            'client_profile': {}
        }
        identity = {
            'communication_style': {}
        }
        
        # Should not crash
        is_valid, warnings = SemanticValidator.validate_consistency(
            industry, situation, psychology, identity
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
    
    def test_format_warnings_for_display(self):
        """Test warning formatting utility."""
        warnings = [
            "Warning 1: Issue detected",
            "Warning 2: Another issue"
        ]
        
        formatted = SemanticValidator.format_warnings_for_display(warnings)
        
        assert "2 advertencias" in formatted
        assert "Warning 1" in formatted
        assert "Warning 2" in formatted
    
    def test_format_warnings_empty_list(self):
        """Test formatting with no warnings."""
        formatted = SemanticValidator.format_warnings_for_display([])
        
        assert "✅" in formatted
        assert "coherente" in formatted.lower()

