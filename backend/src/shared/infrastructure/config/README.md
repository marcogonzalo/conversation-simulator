# Configuración de Conversaciones

Este directorio contiene las configuraciones YAML para el sistema de 5 capas.

## 📂 Estructura

```mermaid
config/
├── CONVERSATION_CONFIGURATION.md   # Documentación completa ⭐
├── simulation_rules.yaml           # Capa 1: Reglas globales
├── industry_contexts/              # Capa 2: Industrias (2)
├── sales_situations/               # Capa 3: Situaciones (4)
├── client_psychology/              # Capa 4: Psicologías (3)
└── client_identity/                # Capa 5: Identidades (3)
```

## 📖 Documentación

- **Configuración**: Lee `CONVERSATION_CONFIGURATION.md` para entender el sistema completo de 5 capas
- **Validación Semántica**: Ver [/backend/docs/SEMANTIC_VALIDATION.md](/backend/docs/SEMANTIC_VALIDATION.md)
- **Telemetría**: Ver [/backend/docs/TELEMETRY.md](/backend/docs/TELEMETRY.md)

## 🚀 Uso

```python
from src.shared.application.prompt_service import PromptService

service = PromptService()  # Usa path default
prompt = service.generate_prompt(
    industry_id="real_estate",
    situation_id="discovery_no_urgency_price",
    psychology_id="conservative_analytical",
    identity_id="ana_garcia"
)
```

## 📊 Estadísticas

- **72 combinaciones** posibles (2×4×3×3)
- **8 tipos** de objeción con mapeo inteligente
- **100% modular** y reutilizable

---

**Ver documentación completa**: `CONVERSATION_CONFIGURATION.md`
