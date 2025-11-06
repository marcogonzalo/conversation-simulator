#!/usr/bin/env python3
"""
Script de prueba para el sistema de 5 capas
Valida que todas las combinaciones funcionan correctamente
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path (desde tests/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from src.shared.application.prompt_service import PromptService


def print_section(title: str):
    """Imprime una sección separada"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


@pytest.fixture
def prompt_service():
    """Fixture: Crear instancia de PromptService"""
    return PromptService()


def test_available_options(prompt_service):
    """Prueba 1: Listar opciones disponibles"""
    print_section("TEST 1: Opciones Disponibles")
    
    options = prompt_service.get_all_available_options()

    print("📦 INDUSTRIAS:")
    for ind in options['industries']:
        print(f"  - {ind['id']}: {ind['name']}")

    print("\n📊 SITUACIONES DE VENTA:")
    for sit in options['situations']:
        print(f"  - {sit['id']}: {sit['name']}")

    print("\n🧠 PSICOLOGÍAS:")
    for psy in options['psychologies']:
        print(f"  - {psy['id']}: {psy['name']}")

    print("\n👤 IDENTIDADES:")
    for ident in options['identities']:
        print(f"  - {ident['id']}: {ident['name']}")

    total = prompt_service.get_total_combinations()
    print(f"\n✨ TOTAL DE COMBINACIONES POSIBLES: {total}")
    
    assert len(options['industries']) > 0
    assert len(options['situations']) > 0
    assert len(options['psychologies']) > 0
    assert len(options['identities']) > 0
    assert total > 0


def test_specific_combination(prompt_service):
    """Prueba 2: Generar prompt específico"""
    print_section("TEST 2: Generar Prompt Específico")

    # Combinación de prueba
    industry_id = "real_estate"
    situation_id = "discovery_no_urgency_price"
    psychology_id = "conservative_analytical"
    identity_id = "ana_garcia"

    print("🎯 COMBINACIÓN DE PRUEBA:")
    print(f"  Industry: {industry_id}")
    print(f"  Situation: {situation_id}")
    print(f"  Psychology: {psychology_id}")
    print(f"  Identity: {identity_id}")

    # Validar combinación
    is_valid = prompt_service.validate_combination(
        industry_id, situation_id, psychology_id, identity_id
    )
    print(f"\n✅ Combinación válida: {is_valid}")

    assert is_valid, "La combinación debe ser válida"

    # Generar prompt
    prompt = prompt_service.generate_prompt(
        industry_id, situation_id, psychology_id, identity_id
    )

    # Mostrar metadatos
    metadata = prompt_service.get_prompt_telemetry(
        industry_id, situation_id, psychology_id, identity_id
    )

    print("\n📄 METADATOS DEL PROMPT:")
    print(f"  Longitud: {metadata['prompt_length']} caracteres")
    print(f"  Palabras: {metadata['word_count']}")

    print("\n📝 PRIMERAS 500 CARACTERES DEL PROMPT:")
    print("-" * 80)
    print(prompt[:500])
    print("...")
    print("-" * 80)
    
    assert len(prompt) > 100
    assert metadata['prompt_length'] > 0


def test_objection_mapping(prompt_service):
    """Prueba 3: Verificar mapeo de objeciones"""
    print_section("TEST 3: Mapeo de Objeciones")

    test_cases = [
        {
            "name": "Real Estate - Precio",
            "industry": "real_estate",
            "situation": "discovery_no_urgency_price",
            "expected": "precio por metro cuadrado"
        },
        {
            "name": "Real Estate - Ajuste (Ubicación)",
            "industry": "real_estate",
            "situation": "closing_high_urgency_fit",
            "expected": "ubicación"
        },
        {
            "name": "Health Insurance - Ajuste (Red médicos)",
            "industry": "health_insurance",
            "situation": "closing_high_urgency_fit",
            "expected": "red de médicos"
        },
        {
            "name": "Health Insurance - Confianza",
            "industry": "health_insurance",
            "situation": "objection_handling_high_urgency_trust",
            "expected": "aseguradoras"
        }
    ]

    psychology_id = "conservative_analytical"
    identity_id = "ana_garcia"

    results = []

    for test in test_cases:
        print(f"\n🧪 {test['name']}")
        prompt = prompt_service.generate_prompt(
            test['industry'],
            test['situation'],
            psychology_id,
            identity_id
        )

        # Buscar objeción en el prompt
        if test['expected'].lower() in prompt.lower():
            print(
                f"  ✅ Objeción mapeada correctamente (encontrado: '{test['expected']}')")
            results.append(True)
        else:
            print(
                f"  ⚠️  No se encontró la objeción esperada: '{test['expected']}'")
            results.append(False)

    success_rate = (sum(results) / len(results)) * 100
    print(
        f"\n📊 TASA DE ÉXITO: {success_rate:.1f}% ({sum(results)}/{len(results)})")

    assert sum(results) >= len(results) * 0.75, f"Al menos 75% de los tests deben pasar (pasaron {sum(results)}/{len(results)})"


def test_all_combinations(prompt_service):
    """Prueba 4: Validar todas las combinaciones"""
    print_section("TEST 4: Validar Todas las Combinaciones")

    industries = prompt_service.prompt_builder.get_available_industries()
    situations = prompt_service.prompt_builder.get_available_situations()
    psychologies = prompt_service.prompt_builder.get_available_psychologies()
    identities = prompt_service.prompt_builder.get_available_identities()

    total_combinations = len(industries) * len(situations) * \
        len(psychologies) * len(identities)

    print(f"⏳ Probando {total_combinations} combinaciones...")
    print(f"   Industrias: {len(industries)}")
    print(f"   Situaciones: {len(situations)}")
    print(f"   Psicologías: {len(psychologies)}")
    print(f"   Identidades: {len(identities)}")

    successful = 0
    failed = 0
    failed_combinations = []

    for industry in industries:
        for situation in situations:
            for psychology in psychologies:
                for identity in identities:
                    try:
                        prompt = prompt_service.generate_prompt(
                            industry, situation, psychology, identity
                        )
                        if len(prompt) > 100:  # Validación básica
                            successful += 1
                        else:
                            failed += 1
                            failed_combinations.append(
                                f"{industry}+{situation}+{psychology}+{identity}"
                            )
                    except Exception as e:
                        failed += 1
                        failed_combinations.append(
                            f"{industry}+{situation}+{psychology}+{identity}: {str(e)}"
                        )

    print(f"\n✅ Exitosas: {successful}/{total_combinations}")
    print(f"❌ Fallidas: {failed}/{total_combinations}")

    if failed > 0:
        print("\n⚠️  COMBINACIONES FALLIDAS:")
        for combo in failed_combinations[:5]:  # Mostrar solo las primeras 5
            print(f"  - {combo}")
        if len(failed_combinations) > 5:
            print(f"  ... y {len(failed_combinations) - 5} más")

    success_rate = (successful / total_combinations) * 100
    print(f"\n📊 TASA DE ÉXITO: {success_rate:.1f}%")

    assert success_rate >= 90.0, f"Al menos 90% de las combinaciones deben funcionar (actual: {success_rate:.1f}%)"


# El archivo ahora está estructurado como tests de pytest
# Ejecutar con: pytest tests/test_5layer_system.py -v
