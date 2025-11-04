# Semantic Validation System

Sistema de validación semántica para configuraciones de 5 capas que detecta inconsistencias lógicas entre las diferentes capas de configuración.

## 🎯 Propósito

Prevenir configuraciones que sean técnicamente válidas (los archivos YAML están bien formados) pero **semánticamente incoherentes** (las combinaciones no tienen sentido lógico).

## 🔍 Reglas de Validación

### Rule 1: Urgency vs Timeline
- ❌ Urgencia "alta" con timeline "6+ meses"
- ❌ Urgencia "baja" con timeline "inmediato"
- ✅ Urgencia "alta" con timeline "1-2 semanas"

### Rule 2: Difficulty vs Cooperation
- ❌ Dificultad "muy_dificil" con cooperación "muy_cooperativo"
- ❌ Dificultad "facil" con cooperación "hostil"
- ✅ Dificultad "dificil" con cooperación "desafiante"

### Rule 3: Sales Phase vs Objection Type
- ❌ Fase "cierre" con objeción "need" (necesidad)
- ❌ Fase "descubrimiento" con objeción "technical"
- ✅ Fase "presentacion" con objeción "technical"

### Rule 4: Budget Flexibility vs Price Objection
- ⚠️ Flexibilidad "alto" con objeción "price" (nota, no crítico)

### Rule 5: Processing Style vs Response Length
- ❌ Estilo "analitico" con respuestas "concise"
- ❌ Estilo "emocional" con respuestas "detailed"
- ✅ Estilo "analitico" con respuestas "detailed"

### Rule 6: Objection Intensity vs Cooperation
- ❌ Intensidad "fuerte" con cooperación "muy_cooperativo"
- ✅ Intensidad "suave" con cooperación "muy_cooperativo"

### Rule 7: Experience vs Question Depth
- ❌ Experiencia "ninguna" con preguntas "muy_profunda"
- ❌ Experiencia "evaluacion_completada" con preguntas "superficial"
- ✅ Experiencia "intermedia" con preguntas "profunda"

## 🔧 Modos de Operación

### Modo Permisivo (Default)
```bash
PROMPT_STRICT_VALIDATION=false
```

**Comportamiento:**
- ✅ Genera todos los prompts
- ⚠️ Log warnings para inconsistencias
- 🔓 No bloquea ninguna configuración

**Uso recomendado:**
- Desarrollo
- Experimentación
- Testing de nuevas configuraciones

### Modo Estricto
```bash
PROMPT_STRICT_VALIDATION=true
```

**Comportamiento:**
- ✅ Genera prompts coherentes
- ❌ **BLOQUEA** prompts con contradicciones críticas
- ⚠️ Permite warnings no críticos
- 🔒 Garantiza calidad en producción

**Uso recomendado:**
- Producción
- Entornos de staging
- CI/CD pipelines

## 📊 Niveles de Severidad

| Tipo | Palabra Clave | Modo Permisivo | Modo Estricto |
|------|---------------|----------------|---------------|
| **Crítico** | "Contradicción", "Inconsistencia" | ⚠️ Warning | ❌ Error |
| **No Crítico** | "Combinación inusual", "Nota" | ⚠️ Warning | ⚠️ Warning |

## 🚀 Uso

### En Código

```python
from src.shared.application.prompt_service import PromptService

# Modo permisivo
service = PromptService(strict_validation=False)
prompt = service.generate_prompt(...)  # Siempre funciona

# Modo estricto
service = PromptService(strict_validation=True)
try:
    prompt = service.generate_prompt(...)  # Puede lanzar ValueError
except ValueError as e:
    print(f"Configuración inválida: {e}")
```

### Vía API

```bash
# Endpoint de validación (siempre disponible)
POST /api/v1/prompts/validate?industry_id=...&situation_id=...&psychology_id=...&identity_id=...

# Response
{
  "valid": true,
  "semantically_coherent": false,
  "warnings": ["⚠️ Combinación inusual: ..."],
  "warning_count": 1
}
```

### Variables de Entorno

```bash
# .env
PROMPT_STRICT_VALIDATION=false  # Development
PROMPT_STRICT_VALIDATION=true   # Production
```

## 📝 Ejemplos

### Ejemplo 1: Combinación Coherente

```yaml
industry: real_estate
situation: discovery_no_urgency_price
  urgency: baja
  timeline: 6+ meses
psychology: conservative_analytical
  difficulty: medio
  cooperation: reservado
identity: ana_garcia
  processing: analitico
  response_length: detailed
```

**Resultado:**
```
✅ Modo Permisivo: Genera prompt
✅ Modo Estricto: Genera prompt
📊 Warnings: 0
```

### Ejemplo 2: Warning No Crítico

```yaml
industry: real_estate
situation: closing_high_urgency_fit
  phase: cierre
  objection: fit  # ⚠️ Inusual pero permitido
psychology: impulsive_enthusiastic
identity: carlos_mendoza
```

**Resultado:**
```
✅ Modo Permisivo: Genera prompt + warning log
✅ Modo Estricto: Genera prompt + warning log
⚠️ Warnings: 1 (no crítico)
```

### Ejemplo 3: Contradicción Crítica

```yaml
industry: real_estate
situation: custom_high_urgency
  urgency: alta
  timeline: 6+ meses  # ❌ CONTRADICCIÓN
psychology: conservative_analytical
  difficulty: muy_dificil
  cooperation: muy_cooperativo  # ❌ CONTRADICCIÓN
  processing: analitico
identity: ana_garcia
  response_length: concise  # ❌ CONTRADICCIÓN
```

**Resultado:**
```
✅ Modo Permisivo: Genera prompt + 3 warning logs
❌ Modo Estricto: ValueError con lista de 3 contradicciones críticas
🔴 Warnings: 3 (todos críticos)
```

## 🔄 Flujo de Validación

```
1. Usuario selecciona configuración (4 capas)
   ↓
2. build_prompt() carga 5 YAMLs
   ↓
3. SemanticValidator.validate_consistency()
   ├─ Ejecuta 7 reglas de validación
   └─ Devuelve (is_valid, warnings)
   ↓
4. Clasificación de warnings
   ├─ Críticos: "Contradicción", "Inconsistencia"
   └─ No críticos: "Inusual", "Nota"
   ↓
5. Decisión según modo
   ├─ Permisivo: Log + continuar
   └─ Estricto: Si hay críticos → ValueError
   ↓
6. Construir y devolver prompt
```

## 📈 Recomendaciones

### Desarrollo
```bash
PROMPT_STRICT_VALIDATION=false
```
- Permite experimentación
- Logs ayudan a detectar problemas
- No bloquea el flujo

### Staging/QA
```bash
PROMPT_STRICT_VALIDATION=false
```
- Permite testing de edge cases
- Captura warnings para review

### Production
```bash
PROMPT_STRICT_VALIDATION=true
```
- Garantiza calidad
- Previene configuraciones contradictorias
- Falla rápido ante problemas

## 🧪 Testing

```bash
# Ejecutar tests de validación semántica
pytest tests/test_semantic_validator.py -v

# Ejecutar tests de modo estricto
pytest tests/test_prompt_builder_strict_mode.py -v

# Ejecutar todos los tests relacionados
pytest tests/test_semantic_validator.py tests/test_prompt_builder_strict_mode.py -v
```

## 📊 Logs

### Modo Permisivo
```
WARNING - Semantic validation for real_estate_closing_...: 1 warnings found
WARNING -   ⚠️  1 non-critical warnings:
WARNING -     ⚠️ Combinación inusual: Fase 'cierre' con objeción tipo 'fit'...
INFO - Prompt built successfully for real_estate_closing_...
```

### Modo Estricto (con error crítico)
```
WARNING - Semantic validation for ...: 3 warnings found
WARNING -   🔴 3 CRITICAL warnings:
WARNING -     ⚠️ Contradicción: Urgencia 'alta' con timeline largo '6+ meses'
WARNING -     ⚠️ Contradicción: Dificultad 'muy_dificil' con cooperación 'muy_cooperativo'
WARNING -     ⚠️ Contradicción: Estilo 'analitico' con respuestas 'concise'
ERROR - Semantic validation failed in STRICT mode for ...
ERROR - Critical issues: [...]
```

## 🎯 Resumen

| Aspecto | Permisivo | Estricto |
|---------|-----------|----------|
| **Default** | ✅ Sí | ❌ No |
| **Warnings críticos** | ⚠️ Log | ❌ Error |
| **Warnings no críticos** | ⚠️ Log | ⚠️ Log |
| **Genera prompt** | ✅ Siempre | ✅ Si no hay críticos |
| **Uso recomendado** | Dev/Testing | Production |
| **Variable de entorno** | `PROMPT_STRICT_VALIDATION=false` | `PROMPT_STRICT_VALIDATION=true` |

