# Backend Documentation

Documentación técnica del sistema backend.

## 📚 Contenido

### **Prompt System**

- **[TELEMETRY.md](./TELEMETRY.md)** - Sistema de telemetría para rastreo, debugging y reproducibilidad de prompts
  - Metadata capturada
  - API endpoints
  - Casos de uso en debugging
  - Scripts de analytics

- **[SEMANTIC_VALIDATION.md](./SEMANTIC_VALIDATION.md)** - Sistema de validación semántica entre capas
  - Reglas de consistencia
  - Modo estricto vs permisivo
  - Configuración por entorno
  - Ejemplos de uso

## 🗂️ Estructura de Documentación

```mermaid
backend/
├── docs/                          # Documentación técnica (aquí)
│   ├── README.md                  # Este archivo
│   ├── TELEMETRY.md              # Sistema de telemetría
│   └── SEMANTIC_VALIDATION.md    # Sistema de validación semántica
│
├── config/                        # Configuración de la aplicación
│   ├── CONVERSATION_CONFIGURATION.md
│   ├── DATABASE_URLS.md
│   └── README.md
│
├── src/shared/infrastructure/config/  # Archivos YAML de configuración
│   ├── simulation_rules.yaml
│   ├── industry_contexts/*.yaml
│   ├── sales_situations/*.yaml
│   ├── client_psychology/*.yaml
│   └── client_identity/*.yaml
│
└── tests/                         # Tests unitarios e integración
    ├── RUN_5LAYER_TESTS.md
    └── test_*.py
```

## 🔗 Enlaces Relacionados

- **Configuración de conversaciones**: [../config/CONVERSATION_CONFIGURATION.md](../config/CONVERSATION_CONFIGURATION.md)
- **Setup de debugging**: [../../DEBUG_SETUP.md](../../DEBUG_SETUP.md)
- **Tests del sistema**: [../tests/RUN_5LAYER_TESTS.md](../tests/RUN_5LAYER_TESTS.md)

## 📖 Por Dónde Empezar

1. **Si eres nuevo**: Lee primero [../config/CONVERSATION_CONFIGURATION.md](../config/CONVERSATION_CONFIGURATION.md) para entender el sistema de 5 capas
2. **Para debugging**: Consulta [TELEMETRY.md](./TELEMETRY.md) para rastrear y reproducir prompts
3. **Para validación**: Revisa [SEMANTIC_VALIDATION.md](./SEMANTIC_VALIDATION.md) para entender las reglas de consistencia
