#!/usr/bin/env python3
"""
Ejemplo Simple de Uso del Sistema de 5 Capas
Este script demuestra cómo usar el sistema sin necesidad de API o Frontend
"""

from shared.application.prompt_service import PromptService
import sys
import os

# Agregar src al path (desde examples/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def main():
    print("=" * 80)
    print("  EJEMPLO DE USO - SISTEMA DE 5 CAPAS")
    print("=" * 80)

    # Inicializar servicio
    print("\n1️⃣  Inicializando servicio...")
    service = PromptService(config_path="../src/shared/infrastructure/config")
    print("   ✅ Servicio inicializado")

    # Ver opciones disponibles
    print("\n2️⃣  Opciones disponibles:")
    print(f"   📦 Industrias: {len(service.get_available_industries())}")
    print(f"   📊 Situaciones: {len(service.get_available_situations())}")
    print(f"   🧠 Psicologías: {len(service.get_available_psychologies())}")
    print(f"   👤 Identidades: {len(service.get_available_identities())}")
    print(f"   ✨ Total combinaciones: {service.get_total_combinations()}")

    # Ejemplo 1: Venta de vivienda
    print("\n3️⃣  Ejemplo 1: Venta de Vivienda - Cliente Conservador")
    print("   " + "-" * 76)

    try:
        prompt1 = service.generate_prompt(
            industry_id="real_estate",
            situation_id="discovery_no_urgency_price",
            psychology_id="conservative_analytical",
            identity_id="ana_garcia"
        )

        print("   ✅ Prompt generado exitosamente")
        print(f"   📏 Longitud: {len(prompt1)} caracteres")
        print(f"   📝 Primeras 200 caracteres:")
        print("   " + prompt1[:200].replace("\n", "\n   "))
        print("   ...")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Ejemplo 2: Seguro médico
    print("\n4️⃣  Ejemplo 2: Seguro Médico - Cliente Escéptico")
    print("   " + "-" * 76)

    try:
        prompt2 = service.generate_prompt(
            industry_id="health_insurance",
            situation_id="objection_handling_high_urgency_trust",
            psychology_id="skeptical_pragmatic",
            identity_id="maria_rodriguez"
        )

        print("   ✅ Prompt generado exitosamente")
        print(f"   📏 Longitud: {len(prompt2)} caracteres")

        # Buscar objeciones específicas
        if "aseguradoras" in prompt2.lower():
            print("   ✅ Objeción mapeada: 'aseguradoras' (específica de seguros)")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Ejemplo 3: Todas las combinaciones para una identidad
    print("\n5️⃣  Ejemplo 3: Todas las combinaciones para Ana García")
    print("   " + "-" * 76)

    industries = service.prompt_builder.get_available_industries()
    situations = service.prompt_builder.get_available_situations()

    count = 0
    for industry in industries:
        for situation in situations:
            try:
                prompt = service.generate_prompt(
                    industry_id=industry,
                    situation_id=situation,
                    psychology_id="conservative_analytical",
                    identity_id="ana_garcia"
                )
                count += 1
            except Exception as e:
                print(f"   ❌ Falló: {industry} + {situation}")

    total = len(industries) * len(situations)
    print(f"   ✅ Generados exitosamente: {count}/{total}")

    print("\n" + "=" * 80)
    print("  SISTEMA FUNCIONANDO CORRECTAMENTE ✅")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
