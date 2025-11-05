# Cómo Ejecutar las Pruebas del Sistema de 5 Capas

## Opción 1: Usando Docker (Recomendado)

```bash
# Desde el directorio raíz del proyecto
cd backend

# Ejecutar el script de prueba en Docker
docker-compose run --rm backend python tests/test_5layer_system.py
```

## Opción 2: Entorno Virtual Local

```bash
# Crear entorno virtual
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install pyyaml pydantic

# Ejecutar pruebas
python tests/test_5layer_system.py
```

## Opción 3: Entorno de Desarrollo Existente

```bash
# Si ya tienes un entorno con las dependencias instaladas
cd backend
python tests/test_5layer_system.py
```

## Qué Hace el Script de Prueba

El script `test_5layer_system.py` realiza 4 pruebas:

### Test 1: Opciones Disponibles

- Lista todas las opciones de cada capa
- Calcula combinaciones posibles totales
- Valida que los archivos existan

### Test 2: Generar Prompt Específico

- Prueba una combinación específica:
  - Industry: real_estate
  - Situation: discovery_no_urgency_price
  - Psychology: conservative_analytical  
  - Identity: ana_garcia
- Genera el prompt completo
- Muestra metadatos (longitud, palabras)

### Test 3: Mapeo de Objeciones

- Valida que las objeciones se mapeen correctamente:
  - Real Estate + Precio → "precio por metro cuadrado"
  - Real Estate + Ajuste → "ubicación"
  - Health Insurance + Ajuste → "red de médicos"
  - Health Insurance + Confianza → "aseguradoras"

### Test 4: Todas las Combinaciones

- Prueba TODAS las combinaciones posibles
- Valida que cada una genere un prompt válido
- Reporta tasa de éxito

## Ejemplo de Salida Esperada

```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
  PRUEBAS DEL SISTEMA DE 5 CAPAS
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

================================================================================
  TEST 1: Opciones Disponibles
================================================================================

📦 INDUSTRIAS:
  - real_estate: Real Estate
  - health_insurance: Health Insurance

📊 SITUACIONES DE VENTA:
  - discovery_no_urgency_price: Discovery No Urgency Price
  - closing_high_urgency_fit: Closing High Urgency Fit
  - presentation_medium_urgency_value: Presentation Medium Urgency Value
  - objection_handling_high_urgency_trust: Objection Handling High Urgency Trust

🧠 PSICOLOGÍAS:
  - conservative_analytical: Conservative Analytical
  - impulsive_enthusiastic: Impulsive Enthusiastic
  - skeptical_pragmatic: Skeptical Pragmatic

👤 IDENTIDADES:
  - ana_garcia: Ana Garcia
  - carlos_mendoza: Carlos Mendoza
  - maria_rodriguez: Maria Rodriguez

✨ TOTAL DE COMBINACIONES POSIBLES: 72

[... más tests ...]

================================================================================
  RESUMEN FINAL
================================================================================
✅ Test 1: Opciones disponibles - PASSED
✅ Test 2: Combinación específica - PASSED
✅ Test 3: Mapeo de objeciones - PASSED
✅ Test 4: Todas las combinaciones - PASSED

🎉 TODOS LOS TESTS PASARON EXITOSAMENTE
```

## Dependencias Requeridas

- Python 3.8+
- pyyaml
- pydantic

Estas ya están en `requirements.txt` del proyecto.

## Troubleshooting

### Error: ModuleNotFoundError: No module named 'yaml'

**Solución**: Instala PyYAML con `pip install pyyaml`

### Error: ModuleNotFoundError: No module named 'pydantic'

**Solución**: Instala Pydantic con `pip install pydantic`

### Error: FileNotFoundError al cargar YAMLs

**Solución**: Asegúrate de ejecutar el script desde el directorio `backend/`
