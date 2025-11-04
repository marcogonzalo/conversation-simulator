#!/usr/bin/env python3
"""
Script de prueba para el sistema de 5 capas
Valida que todas las combinaciones funcionan correctamente
"""

from pathlib import Path
from shared.application.prompt_service import PromptService
import sys
import os

# Agregar el directorio src al path (desde tests/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def print_section(title: str):
    """Imprime una sección separada"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_available_options():
    """Prueba 1: Listar opciones disponibles"""
    print_section("TEST 1: Opciones Disponibles")
    
    service = PromptService(config_path="../src/shared/infrastructure/config")
    options = service.get_all_available_options()

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

    total = service.get_total_combinations()
    print(f"\n✨ TOTAL DE COMBINACIONES POSIBLES: {total}")

    return service


def test_specific_combination(service: PromptService):
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
    is_valid = service.validate_combination(
        industry_id, situation_id, psychology_id, identity_id
    )
    print(f"\n✅ Combinación válida: {is_valid}")

    if is_valid:
        # Generar prompt
        try:
            prompt = service.generate_prompt(
                industry_id, situation_id, psychology_id, identity_id
            )

            # Mostrar metadatos
            metadata = service.get_prompt_metadata(
                industry_id, situation_id, psychology_id, identity_id
            )

            print("\n📄 METADATOS DEL PROMPT:")
            print(f"  Longitud: {metadata['prompt_length']} caracteres")
            print(f"  Palabras: {metadata['prompt_word_count']}")

            print("\n📝 PRIMERAS 500 CARACTERES DEL PROMPT:")
            print("-" * 80)
            print(prompt[:500])
            print("...")
            print("-" * 80)

            return True
        except Exception as e:
            print(f"\n❌ Error generando prompt: {e}")
            import traceback
            traceback.print_exc()
            return False

    return False


def test_objection_mapping(service: PromptService):
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
        try:
            prompt = service.generate_prompt(
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

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)

    success_rate = (sum(results) / len(results)) * 100
    print(
        f"\n📊 TASA DE ÉXITO: {success_rate:.1f}% ({sum(results)}/{len(results)})")

    return all(results)


def test_all_combinations(service: PromptService):
    """Prueba 4: Validar todas las combinaciones"""
    print_section("TEST 4: Validar Todas las Combinaciones")

    industries = service.prompt_builder.get_available_industries()
    situations = service.prompt_builder.get_available_situations()
    psychologies = service.prompt_builder.get_available_psychologies()
    identities = service.prompt_builder.get_available_identities()

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
                        prompt = service.generate_prompt(
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

    return failed == 0


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "🧪" * 40)
    print("  PRUEBAS DEL SISTEMA DE 5 CAPAS")
    print("🧪" * 40)

    try:
        # Test 1: Opciones disponibles
        service = test_available_options()

        # Test 2: Combinación específica
        test2_passed = test_specific_combination(service)

        # Test 3: Mapeo de objeciones
        test3_passed = test_objection_mapping(service)

        # Test 4: Todas las combinaciones
        test4_passed = test_all_combinations(service)

        # Resumen final
        print_section("RESUMEN FINAL")
        print("✅ Test 1: Opciones disponibles - PASSED")
        print(f"{'✅' if test2_passed else '❌'} Test 2: Combinación específica - {'PASSED' if test2_passed else 'FAILED'}")
        print(f"{'✅' if test3_passed else '❌'} Test 3: Mapeo de objeciones - {'PASSED' if test3_passed else 'FAILED'}")
        print(f"{'✅' if test4_passed else '❌'} Test 4: Todas las combinaciones - {'PASSED' if test4_passed else 'FAILED'}")

        all_passed = test2_passed and test3_passed and test4_passed

        if all_passed:
            print("\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
            return 0
        else:
            print("\n⚠️  ALGUNOS TESTS FALLARON")
            return 1

    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
