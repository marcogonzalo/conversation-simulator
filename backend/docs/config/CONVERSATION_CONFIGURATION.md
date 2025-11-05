# Documentación de Configuración de Conversaciones

## Introducción

Este sistema permite configurar simulaciones de conversaciones de ventas mediante la combinación de **5 capas modulares e independientes**. En lugar de crear archivos monolíticos, se componen escenarios combinando componentes reutilizables.

---

## Arquitectura de 5 Capas

### Capa 1: Simulation Rules (Global) 🔒

**Archivo**: `simulation_rules.yaml` (único)  
**Ubicación**: `src/shared/infrastructure/config/`

Define las reglas inmutables que garantizan calidad y seguridad en TODAS las conversaciones:

- Identidad del LLM (siempre cliente, nunca vendedor)
- Reglas de seguridad críticas
- Estándares de realismo conversacional
- Directrices de comportamiento general

**Modificar**: Solo cuando se identifiquen reglas universales nuevas.

---

### Capa 2: Industry Context 🏭

**Directorio**: `src/shared/infrastructure/config/industry_contexts/`  
**Archivos actuales**: `real_estate.yaml`, `health_insurance.yaml`

Define el contexto de la industria donde ocurre la venta:

| Sección | Contenido |
|---------|-----------|
| **Industry** | Sector, subsector, mercado |
| **Sale Type** | Tipo de producto, complejidad, ciclo |
| **Budget Situation** | Rango presupuestario típico, flexibilidad |
| **Terminology** | Términos clave y preocupaciones comunes |
| **Objection Mappings** | Manifestaciones específicas de objeciones por tipo |

**Crear nuevo**: Por cada industria/vertical nueva.

#### Sistema de Objection Mappings

Cada industria define cómo se manifiestan los 8 tipos de objeción:

```yaml
objection_mappings:
  # No incluir = No aplica
  
  # true = Aplica de forma genérica
  trust: true
  
  # [lista] = Expresiones específicas de la industria
  fit:
    - "La ubicación no me convence"  # Real estate
    - "La red de médicos es limitada"  # Insurance
  
  price:
    - "El precio por m² es muy alto"  # Real estate
    - "La prima mensual es muy alta"  # Insurance
```

---

### Capa 3: Sales Situation 📊

**Directorio**: `src/shared/infrastructure/config/sales_situations/`  
**Archivos actuales**: 4 combinaciones

Define la situación específica de venta: **Fase + Urgencia + Objeción Principal**

| Archivo | Fase | Urgencia | Objeción |
|---------|------|----------|----------|
| `discovery_no_urgency_price.yaml` | Descubrimiento | Baja | Precio |
| `closing_high_urgency_fit.yaml` | Cierre | Alta | Ajuste |
| `presentation_medium_urgency_value.yaml` | Presentación | Media | Valor |
| `objection_handling_high_urgency_trust.yaml` | Manejo Objeciones | Alta | Confianza |

**Característica clave**: 100% agnósticos de industria - funcionan en cualquier contexto.

#### Tipos de Objeción Soportados (8 tipos)

1. **price** - Precio/Costo demasiado alto
2. **value** - No ve el beneficio/ROI
3. **fit** - No se ajusta a necesidades específicas
4. **risk** - Riesgos, seguridad, garantías
5. **trust** - No confía en proveedor/empresa
6. **need** - Cuestiona si realmente lo necesita
7. **competition** - La competencia es mejor/más barata
8. **technical** - Muy complejo o incompatible

**Crear nuevo**: Por cada combinación única de Fase+Urgencia+Objeción.  
**Nomenclatura**: `{fase}_{urgencia}_{objecion}.yaml`

---

### Capa 4: Client Psychology 🧠

**Directorio**: `src/shared/infrastructure/config/client_psychology/`  
**Archivos actuales**: 3 perfiles

Define el perfil psicológico y comportamental del cliente:

| Archivo | Personalidad | Estado Emocional | Nivel de Desafío |
|---------|--------------|------------------|------------------|
| `conservative_analytical.yaml` | Analítico, orientado a datos | Neutral/Profesional | Medio, Reservado |
| `impulsive_enthusiastic.yaml` | Expresivo, decide por emoción | Entusiasmado | Bajo, Muy cooperativo |
| `skeptical_pragmatic.yaml` | Escéptico, difícil convencer | Desconfiado | Alto, Desafiante |

**Contenido principal**:

- **Perfil del Cliente**: Personalidad, Estado Emocional, Estilo de Procesamiento
- **Nivel de Desafío**: Dificultad, Cooperación, Intensidad de Objeción
- **Patrones de Lenguaje**: Frases típicas y preguntas características

**Característica clave**: Completamente reutilizable en cualquier industria.

---

### Capa 5: Client Identity 👤

**Directorio**: `src/shared/infrastructure/config/client_identity/`  
**Archivos actuales**: 3 identidades

Define la identidad personal, cultural y demográfica específica del cliente:

| Archivo | Nombre | Edad | Nacionalidad | Rol | Psychology Recomendada |
|---------|--------|------|--------------|-----|------------------------|
| `ana_garcia.yaml` | Ana García | 45 | Cubana | Gerente Ventas | conservative_analytical |
| `carlos_mendoza.yaml` | Carlos Mendoza | 32 | Venezolano | CEO Startup | impulsive_enthusiastic |
| `maria_rodriguez.yaml` | María Rodríguez | 40 | Peruana | Directora Marketing | skeptical_pragmatic |

**Contenido principal**:

- **Identity**: Edad, nacionalidad, rol, experiencia
- **Voice Config**: Accent, voice_id, dialect (para Text-to-Speech)
- **Communication Style**: Formalidad, longitud, energía
- **Unique Characteristics**: Rasgos culturales específicos
- **Conversation Specifics**: Expresiones típicas por categoría

---

## Cómo se Combinan las Capas

```python
from src.shared.application.prompt_service import PromptService

# Inicializar servicio
service = PromptService()

# Generar prompt combinando 4 capas
prompt = service.generate_prompt(
    industry_id="real_estate",
    situation_id="discovery_no_urgency_price",
    psychology_id="conservative_analytical",
    identity_id="ana_garcia"
)

# Resultado: Prompt personalizado que incluye las 5 capas
```

### Mapeo Inteligente de Objeciones

**Sales Situation** define el tipo genérico:

```yaml
primary_objection:
  type: "fit"
  generic_expressions:
    - "No es exactamente lo que necesito"
```

**Industry Context** lo interpreta según su dominio:

```yaml
objection_mappings:
  fit:
    - "La ubicación no me convence"  # Real Estate
    - "La red de médicos es limitada"  # Insurance
```

**Resultado**: El cliente usará la expresión específica de la industria.

---

## Ejemplos de Combinaciones

### Ejemplo 1: Venta de Casa - Cliente Conservador

```yaml
Industry: real_estate
Situation: discovery_no_urgency_price
Psychology: conservative_analytical
Identity: ana_garcia
```

**Perfil**: Ana García (45, cubana) explorando casas sin urgencia, preocupada por el precio.

**Objeciones**:

- "El precio por metro cuadrado es muy alto"
- "Los costos de cierre son excesivos"

**Habilidades**: Descubrimiento, escucha activa, manejo de objeción de precio.

---

### Ejemplo 2: Seguro Médico - Cliente Escéptico

```yaml
Industry: health_insurance
Situation: closing_high_urgency_fit
Psychology: skeptical_pragmatic
Identity: maria_rodriguez
```

**Perfil**: María Rodríguez (40, peruana) necesita seguro urgente, dudas sobre cobertura.

**Objeciones**:

- "La red de médicos es muy limitada"
- "Mi especialista no está incluido"

**Habilidades**: Cierre bajo presión, construcción de confianza.

---

### Ejemplo 3: Casa - Cliente Entusiasta

```yaml
Industry: real_estate
Situation: closing_high_urgency_fit
Psychology: impulsive_enthusiastic
Identity: carlos_mendoza
```

**Perfil**: Carlos Mendoza (32, venezolano) quiere comprar urgente, dudas sobre ubicación.

**Objeciones**:

- "La ubicación no me convence del todo"
- "Está lejos de buenas escuelas"

**Habilidades**: Cierre rápido, aprovechar momentum.

---

## Los 10 Aspectos Configurables

### ✅ Implementados

| # | Aspecto | Capa | Opciones |
|---|---------|------|----------|
| 1 | **Fase de Venta** | 3 | Descubrimiento, Presentación, Manejo Objeciones, Cierre |
| 2 | **Perfil del Cliente** | 4 | Personalidad, Estado Emocional, Procesamiento |
| 3 | **Nivel de Desafío** | 4 | Dificultad, Cooperación, Intensidad Objeción |
| 4 | **Tipo de Objeción** | 3 | price, value, fit, risk, trust, need, competition, technical |
| 8 | **Presupuesto** | 2 | Rango típico, Ticket size, Flexibilidad |
| 9 | **Industria** | 2 | Real Estate, Health Insurance |

### ❓ Con Defaults Neutrales

| # | Aspecto | Capa | Default |
|---|---------|------|---------|
| 5 | **Estado del Cliente** | 2, 3 | Tibio, Consideración, Experiencia básica |
| 6 | **Estructura de Decisión** | 3 | Decisor conjunto, 2 participantes |
| 7 | **Urgencia** | 3 | Media (1-3 meses) |
| 10 | **Tipo de Venta** | 2 | Consultiva, Ciclo medio |

---

## Crear Nuevas Configuraciones

### Agregar Nueva Industria

1. Copiar plantilla: `industry_example.yaml`
2. Modificar `id`, `industry`, `terminology`
3. Definir `objection_mappings` para tipos relevantes
4. Guardar en `industry_contexts/{nombre}.yaml`

### Agregar Nueva Sales Situation

1. Copiar plantilla: `situation_example.yaml`
2. Modificar `sales_phase`, `urgency`, `primary_objection`
3. Usar solo tipos genéricos de objeción
4. Guardar en `sales_situations/{fase}_{urgencia}_{objecion}.yaml`

### Agregar Nueva Psychology

1. Copiar plantilla: `psychology_example.yaml`
2. Modificar perfil psicológico, challenge_level
3. Guardar en `client_psychology/{tipo}_{estilo}.yaml`

### Agregar Nueva Identity

1. Copiar plantilla: `identity_example.yaml`
2. Modificar demografía, voice_config, expresiones culturales
3. Guardar en `client_identity/{nombre}.yaml`

---

## Tipos de Objeción (Referencia)

| Tipo | Real Estate | Health Insurance |
|------|-------------|------------------|
| **price** | "Precio por m² alto" | "Prima muy alta" |
| **value** | "¿Vale la pena vs rentar?" | "Estoy sano, no necesito" |
| **fit** | "Ubicación no convence" | "Red de médicos limitada" |
| **risk** | "¿Y si no se revaloriza?" | "¿Y si no cubren?" |
| **trust** | Generic | "No confío en aseguradoras" |
| **need** | "¿Comprar o rentar?" | "Nunca me enfermo" |
| **competition** | "Propiedades más baratas" | "Otras aseguradoras mejores" |
| **technical** | N/A | "No entiendo exclusiones" |

---

## Mejores Prácticas

### ✅ DO

1. Reutiliza componentes existentes
2. Mantén sales_situations agnósticas de industria
3. Define objection_mappings completos en cada industry
4. Usa nombres descriptivos
5. Documenta claramente cada archivo

### ❌ DON'T

1. No dupliques información entre capas
2. No hagas situations específicos de una industria
3. No mezcles conceptos de diferentes capas
4. No uses tipos de objeción contradictorios (authority, time, complexity)
5. No omitas objection_mappings en industries

---

## Estadísticas

- **2 industrias**: Real Estate, Health Insurance
- **4 situaciones**: Descubrimiento, Presentación, Manejo, Cierre
- **3 psicologías**: Conservador, Impulsivo, Escéptico
- **3 identidades**: Ana, Carlos, María
- **72 combinaciones** únicas posibles (2×4×3×3)

---

## Validación

El sistema valida automáticamente cada capa con Pydantic:

- `IndustryContextSchema`
- `SalesSituationSchema`
- `ClientPsychologySchema`
- `ClientIdentitySchema`

---

## Archivos de Ejemplo

Cada directorio incluye plantillas `*_example.yaml` para crear nuevas configuraciones:

- `industry_example.yaml`
- `situation_example.yaml`
- `psychology_example.yaml`
- `identity_example.yaml`

---

## Referencias

- **Código**: `src/shared/domain/prompt_builder.py`
- **Servicio**: `src/shared/application/prompt_service.py`
- **Tests**: `tests/test_5layer_system.py`
- **Ejemplo**: `examples/example_5layer_usage.py`

---

**Versión**: 1.0 (5 Capas)  
**Última actualización**: Noviembre 2025  
**Estado**: ✅ Funcional
