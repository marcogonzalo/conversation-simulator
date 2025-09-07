# Active Context: Conversation Simulator

## Current Work Focus

**Fase de Inicio**: Configuración del MVP con enfoque en experiencia conversacional de alta calidad

### Prioridades Inmediatas

1. **Configuración del entorno**: Docker + estructura base del proyecto
2. **Integración de ElevenLabs**: STT + TTS con acentos regionales
3. **Perfiles de persona básicos**: 3 perfiles con personalidades distintivas
4. **Motor de conversación**: Claude Sonnet 4 para personalidades convincentes

## Recent Changes

- **Decisión de Stack**: ElevenLabs completo (STT + TTS) para simplicidad del MVP
- **Arquitectura definida**: Next.js 15+ App Router + FastAPI + WebSockets + Supabase
- **Arquitectura DDD**: Backend estructurado con Domain-Driven Design
- **Estrategia de acentos**: Implementar desde el inicio para diferenciación
- **Enfoque MVP**: Priorizar experiencia conversacional sobre features complejas
- **Deployment strategy**: Vercel (frontend) + Fly.io/Render (backend) + Supabase (database)
- **AI models**: Claude Sonnet 4 (conversación + análisis) - decisión final
- **Estructura completa**: Backend DDD + Frontend Next.js 15+ documentados

## Next Steps

1. **Crear estructura base** del proyecto con Docker (backend + frontend)
2. **Configurar APIs externas** (ElevenLabs, Claude Sonnet 4, Supabase)
3. **Implementar bounded contexts** del backend (conversation, persona, analysis, audio)
4. **Desarrollar componentes frontend** (UI base, conversation, persona selection)
5. **Integrar WebSocket** para comunicación en tiempo real
6. **Testing y validación** de la experiencia conversacional

## Active Decisions and Considerations

- **Proveedor de IA**: Claude Sonnet 4 para conversación y análisis
- **Arquitectura de audio**: WebSockets para streaming en tiempo real
- **Base de datos**: Supabase (PostgreSQL) desde el inicio
- **Deployment**: Vercel + Fly.io + Supabase (todo gratis para MVP)

## Important Patterns and Preferences

- **Conversación First**: Toda decisión debe priorizar la experiencia conversacional
- **Simplicidad**: Evitar over-engineering en el MVP
- **Calidad de audio**: Latencia <500ms es crítica
- **Personalidades convincentes**: Prompts optimizados para cada perfil

## Learnings and Project Insights

- **ElevenLabs completo** simplifica la arquitectura significativamente
- **Acentos regionales** son una característica diferenciadora clave
- **MVP enfocado** permite validación rápida de la propuesta de valor
- **Experiencia conversacional** es el corazón del producto, no features adicionales
- **DDD estructura** el backend para escalabilidad y mantenibilidad
- **Claude Sonnet 4** ofrece mejor calidad de simulación de roles que Haiku
- **Next.js 15+ App Router** proporciona estructura moderna y SEO-friendly

## Current Blockers

- Ninguno identificado actualmente

## Immediate Questions

- Ninguna pendiente actualmente
