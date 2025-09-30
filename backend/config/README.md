# Sistema de Prompts Dinámicos - Documentación Completa

Este directorio contiene los archivos de configuración para el simulador conversacional con el nuevo **Sistema de Prompts Dinámicos**.

## 🚀 Nueva Arquitectura de Tres Capas

El sistema utiliza una arquitectura de **tres capas** para maximizar la escalabilidad y variabilidad mientras mantiene la calidad y coherencia de la experiencia conversacional.

### Arquitectura de Capas

```
Prompt Final = Reglas de Seguridad + Simulation Rules + Conversation Context + Persona Details
```

#### Capa 1: Simulation Rules (Inmutable)

**Archivo:** `simulation_rules.yaml`

- **Propósito:** Reglas base que garantizan calidad y consistencia
- **Contenido:** Identidad del LLM, reglas de seguridad, estándares de realismo
- **Características:** Nunca cambia entre ejecuciones, aplica a todas las conversaciones

#### Capa 2: Conversation Context (Específico)

**Directorio:** `conversation_contexts/`

- **Propósito:** Marco de conocimiento específico para cada tipo de conversación
- **Contenido:** Necesidades del cliente, puntos de dolor, objeciones, factores de decisión
- **Características:** Se selecciona según el tipo de conversación

#### Capa 3: Persona Details (Específico)

**Directorio:** `persona_details/`

- **Propósito:** Estilo de comunicación y personalidad específica del cliente
- **Contenido:** Identidad, personalidad, estilo de comunicación, comportamiento
- **Características:** Se selecciona según la persona a simular

## Estructura de Archivos

```text
backend/config/
├── simulation_rules.yaml                    # Capa 1 (inmutable)
├── conversation_contexts/                   # Capa 2 (contextos específicos)
│   ├── compra_vivienda.yaml
│   ├── evaluacion_crm.yaml
│   ├── negociacion_erp.yaml
│   └── presentacion_marketing.yaml
└── persona_details/                        # Capa 3 (personas específicas)
    ├── carlos_mendoza.yaml
    ├── ana_garcia.yaml
    └── maria_rodriguez.yaml
```

## Combinaciones Disponibles

- **4 Contextos** × **3 Personas** = **12 Combinaciones Únicas**
- Cada combinación genera un prompt único y coherente
- Fácil expansión para más contextos y personas

## API Endpoints

### Generar Prompt

```http
POST /api/v1/prompts/generate
Content-Type: application/json

{
  "conversation_context_id": "compra_vivienda",
  "persona_id": "carlos_mendoza"
}
```

### Obtener Combinaciones Disponibles

```http
GET /api/v1/prompts/combinations
```

### Obtener Contextos Disponibles

```http
GET /api/v1/prompts/contexts
```

### Obtener Personas Disponibles

```http
GET /api/v1/prompts/personas
```

### Obtener Metadatos de Prompt

```http
GET /api/v1/prompts/metadata/{context_id}/{persona_id}
```

### Limpiar Cache

```http
POST /api/v1/prompts/cache/clear
```

## Ventajas del Nuevo Sistema

### 1. **Escalabilidad**

- Fácil agregar nuevos contextos de conversación
- Fácil agregar nuevas personas
- Combinaciones N×M automáticas

### 2. **Variabilidad**

- 4 contextos × 3 personas = 12 combinaciones únicas
- Cada combinación genera un prompt único y coherente
- Fácil expansión para más contextos y personas

### 3. **Mantenibilidad**

- Cada capa es independiente
- Cambios en una capa no afectan las otras
- Fácil debugging y testing

### 4. **Consistencia**

- Reglas base garantizan calidad uniforme
- Estándares de realismo aplicados consistentemente
- Comportamiento predecible en todas las combinaciones

### 5. **Flexibilidad**

- Fácil modificar comportamientos específicos
- Configuración externa sin cambios de código
- Cache inteligente para performance

## Uso del Sistema

### 1. **Generar Prompt Programáticamente**

```python
from src.shared.application.prompt_service import PromptService

# Inicializar servicio
prompt_service = PromptService()

# Generar prompt
prompt = prompt_service.generate_prompt(
    conversation_context_id="compra_vivienda",
    persona_id="carlos_mendoza"
)
```

### 2. **Obtener Combinaciones Disponibles**

```python
combinations = prompt_service.get_available_combinations()
for combo in combinations:
    print(f"{combo['name']}: {combo['conversation_context_id']} + {combo['persona_id']}")
```

### 3. **Validar Combinación**

```python
is_valid = prompt_service.validate_combination(
    conversation_context_id="evaluacion_crm",
    persona_id="ana_garcia"
)
```

## Testing

Ejecutar el script de prueba:

```bash
cd backend
python test_prompt_system.py
```

## Migración Completada

El sistema ha sido completamente modernizado:

- Todos los archivos del sistema anterior han sido eliminados
- El nuevo sistema proporciona mejor seguridad, escalabilidad y mantenibilidad
- Los endpoints de la API han sido actualizados para usar el nuevo sistema

## Consideraciones de Seguridad

- **Reglas de Seguridad Inmutables:** Las reglas base están hardcodeadas para prevenir manipulación
- **Validación de Entrada:** Todas las combinaciones se validan antes de generar prompts
- **Cache Seguro:** El cache no expone información sensible
- **Logging de Auditoría:** Todas las operaciones se registran para auditoría
- **Protección contra Prompt Injection:** Sistema robusto de limpieza con 50+ patrones de inyección
- **Delimitadores de Sesión:** IDs únicos por conversación para prevenir ataques
- **Limpieza Automática:** Todo el contenido se limpia antes de enviar a OpenAI
- **Efectividad de Limpieza:** 87.7% de reducción de contenido malicioso

## Próximos Pasos

1. **Validación de Esquemas YAML** - Agregar validación estricta
2. **Tests Unitarios** - Cobertura completa del sistema
3. **Documentación API** - Swagger/OpenAPI actualizado
4. **Frontend Integration** - Actualizar interfaz para usar nuevo sistema
5. **Performance Optimization** - Cache avanzado y lazy loading

## Beneficios

1. **Escalabilidad:** Fácil agregar nuevos contextos y personas
2. **Variabilidad:** Combinaciones N×M automáticas
3. **Mantenibilidad:** Cada capa es independiente
4. **Consistencia:** Reglas base garantizan calidad uniforme
5. **Flexibilidad:** Fácil modificar comportamientos específicos