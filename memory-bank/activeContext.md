# Active Context: Conversation Simulator

## Current Work Focus

**Fase de Integración de Base de Datos**: Sistema completo de almacenamiento PostgreSQL con análisis mejorado

### Prioridades Inmediatas

1. **Integración PostgreSQL**: Sistema completo de almacenamiento en base de datos
2. **Historial de conversaciones**: Vista completa de todas las conversaciones con metadatos
3. **Análisis mejorado**: Configuración YAML para análisis y colores dinámicos
4. **Testing comprehensivo**: Suite completa de tests para nuevas funcionalidades

## Recent Changes

- **Integración PostgreSQL**: Migración completa de almacenamiento a PostgreSQL con detección automática de tipo de BD
- **Sistema de migración**: Scripts automáticos de migración de base de datos
- **Repositorio SQL**: Nuevo repositorio SQL con operaciones completas CRUD
- **Servicio de transcripción**: TranscriptionFileService para gestión de archivos de transcripción
- **Configuración YAML**: Análisis basado en configuración YAML en lugar de código hardcoded
- **Historial de conversaciones**: Nueva página de historial con nombres humanizados y metadatos
- **Página de detalle**: Vista detallada de conversaciones individuales con transcripciones completas
- **Análisis con colores**: Métricas con colores dinámicos basados en puntuación
- **Tests comprehensivos**: Suite completa de tests para repositorios, servicios y análisis
- **DTOs mejorados**: Data Transfer Objects extendidos con metadatos adicionales
- **API mejorada**: Nuevos endpoints para historial y detalles de conversaciones

## Next Steps

1. **Testing de personalidades**: Validación completa de los 3 perfiles de persona
2. **Optimización de latencia**: Mejoras en el pipeline de audio
3. **Testing cruzado**: Validación en múltiples navegadores
4. **Preparación para deployment**: Configuración de producción
5. **Documentación de usuario**: Guías y tutoriales
6. **Recomendaciones de contenido**: Sistema de recomendaciones post-conversación

## Active Decisions and Considerations

- **Proveedor de IA**: OpenAI GPT-4o-mini-realtime para conversación y análisis
- **Arquitectura de audio**: WebSockets para streaming en tiempo real
- **Base de datos**: Supabase (PostgreSQL) desde el inicio
- **Deployment**: Vercel + Fly.io + Supabase (todo gratis para MVP)

## Important Patterns and Preferences

- **Conversación First**: Toda decisión debe priorizar la experiencia conversacional
- **Simplicidad**: Evitar over-engineering en el MVP
- **Calidad de audio**: Latencia <500ms es crítica
- **Personalidades convincentes**: Prompts optimizados para cada perfil

## Learnings and Project Insights

- **OpenAI completo** simplifica la arquitectura significativamente
- **Acentos regionales** son una característica diferenciadora clave
- **MVP enfocado** permite validación rápida de la propuesta de valor
- **Experiencia conversacional** es el corazón del producto, no features adicionales
- **DDD estructura** el backend para escalabilidad y mantenibilidad
- **OpenAI GPT-4o-mini-realtime** ofrece mejor calidad de simulación de roles con latencia ultra-baja
- **Next.js 15+ App Router** proporciona estructura moderna y SEO-friendly

## Current Blockers

- Ninguno identificado actualmente

## Immediate Questions

- Ninguna pendiente actualmente
