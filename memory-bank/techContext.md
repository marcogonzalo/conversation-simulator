# Tech Context: Conversation Simulator

## Technologies Used

### Frontend

- **Next.js 15+**: App Router, SSR/SSG, optimización automática
- **TypeScript**: Tipado estático, mejor DX, menos errores
- **Tailwind CSS**: Styling utilitario, modo oscuro por defecto
- **Web Audio API**: Captura y reproducción de audio
- **WebSockets**: Comunicación en tiempo real con backend

### Backend

- **FastAPI**: API moderna, documentación automática, WebSockets
- **Python 3.13+**: Async/await, type hints, performance
- **WebSockets**: Comunicación bidireccional en tiempo real
- **PostgreSQL**: Base de datos principal para producción
- **SQLite**: Base de datos ligera para desarrollo
- **Supabase**: PostgreSQL en la nube para despliegues cloud
- **Pydantic**: Validación de datos, serialización
- **SQLAlchemy**: ORM para acceso a base de datos
- **Alembic**: Migraciones de base de datos
- **PyYAML**: Configuración basada en YAML

### AI Services

- **OpenAI Realtime API**: Conversación de voz audio-to-audio en tiempo real
- **Integración completa**: Audio-to-audio en tiempo real con OpenAI Realtime API

### Infrastructure

- **Docker**: Containerización, entorno consistente
- **Docker Compose**: Orquestación de servicios
- **Vercel**: Frontend hosting (gratis)
- **Fly.io**: Backend hosting (gratis)
- **Supabase**: Database hosting (gratis) - PostgreSQL en la nube
- **PostgreSQL**: Base de datos principal para producción
- **SQLite**: Base de datos ligera para desarrollo local

## Development Setup

### Prerequisites

- Docker Desktop
- Git (para versionado)
- Cuenta OpenAI (para API key)
- Cuenta Supabase (para database)
- Cuenta Vercel (para frontend - futuro)
- Cuenta Fly.io (para backend - futuro)

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# OpenAI Voice-to-Voice Configuration
OPENAI_VOICE_MODEL=4o-mini-realtime-preview
OPENAI_VOICE_TEMPERATURE=0.8
OPENAI_VOICE_MAX_TOKENS=4096
OPENAI_VOICE_DEFAULT_VOICE=alloy

# AI Provider Configuration (for fallback text conversations)
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000

# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Audio Settings
AUDIO_CHANNELS=1
AUDIO_PLAYBACK_SAMPLE_RATE=24000

# Voice Detection Settings
VOICE_DETECTION_THRESHOLD=0.5
VOICE_DETECTION_PREFIX_PADDING_MS=300
VOICE_DETECTION_SILENCE_DURATION_MS=500

# Database Configuration
DATABASE_TYPE=postgresql  # postgresql, sqlite, or supabase
DATABASE_URL=postgresql://user:password@localhost:5432/conversation_simulator
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Analysis Configuration
ANALYSIS_CONFIG_PATH=backend/config/analysis_prompts.yaml
```

### Local Development

```bash
# Docker (recomendado - solo opción)
docker-compose up --build

# Desarrollo individual (no recomendado)
# Backend
docker-compose up backend

# Frontend
docker-compose up frontend
```

## Technical Constraints

### Performance

- **Latencia de audio**: <500ms para conversación natural
- **Memoria**: Optimizar para dispositivos móviles
- **CPU**: Procesamiento de audio eficiente
- **Red**: Minimizar transferencia de datos

### Browser Compatibility

- **Web Audio API**: Chrome 66+, Firefox 60+, Safari 14+
- **WebSockets**: Soporte universal
- **MediaRecorder API**: Chrome 47+, Firefox 25+, Safari 14+
- **Mobile**: iOS Safari, Chrome Mobile

### Audio Quality

- **Sample Rate**: 24kHz para OpenAI Realtime API
- **Channels**: Mono para eficiencia
- **Format**: PCM16 para OpenAI, WAV para frontend
- **Compression**: Mínima para preservar calidad
- **Playback Rate**: 24kHz (configurable via AUDIO_PLAYBACK_SAMPLE_RATE)

## Dependencies

### Backend Main Dependencies

```sh
fastapi==0.116.1
uvicorn[standard]==0.34.0
websockets==15.0.1
openai==1.107.2
aiohttp==3.12.15
pydantic==2.11.7
supabase==2.18.1
sqlalchemy==2.0.43
alembic==1.16.5
httpx==0.28.1
psycopg2-binary==2.9.10
pyyaml==6.0.2
```

### Frontend Dependencies

```sh
next@^15.5.2
react@^19.1.1
typescript@^5.9.2
tailwindcss@^4.1.13
@types/node@^24.3.1
@types/react@^19.1.12
@types/react-dom@^19.1.9
```

### Docker Dependencies

```sh
node:18-alpine
python:3.11-slim
```

## Tool Usage Patterns

### Development Tools

- **VS Code**: Editor principal con extensiones TypeScript/Python
- **Docker Desktop**: Desarrollo local con containers
- **Postman**: Testing de APIs
- **Chrome DevTools**: Debugging de audio y WebRTC

### Testing Strategy

- **Backend**: pytest para unit tests, FastAPI TestClient
- **Frontend**: Jest + React Testing Library
- **Integration**: Docker Compose para testing end-to-end
- **Audio**: Testing manual con diferentes dispositivos

### Deployment Pattern

- **Development**: Docker Compose local
- **Frontend**: Vercel (automatic deployment from GitHub)
- **Backend**: Fly.io (Docker deployment)
- **Database**: Supabase (managed PostgreSQL)

### Monitoring and Logging

- **Logging**: Python logging + FastAPI logs
- **Metrics**: Latencia de audio, tasa de errores
- **Health Checks**: Endpoints de salud para servicios
- **Error Tracking**: Sentry o similar (futuro)

## Security Considerations

- **API Keys**: Variables de entorno, nunca en código
- **CORS**: Configuración restrictiva para producción
- **Rate Limiting**: Protección contra abuso de APIs
- **Audio Privacy**: No almacenar conversaciones (GDPR)
- **HTTPS**: Obligatorio para WebRTC en producción

## Technical Decision Rationale

### AI Models Selection

#### OpenAI GPT-4o-mini-realtime (Conversación de Voz)

**¿Por qué elegimos GPT-4o-mini-realtime para conversación de voz?**

- **Tiempo real**: Diseñado específicamente para conversaciones de voz en tiempo real
- **Latencia ultra-baja**: <500ms para respuesta natural
- **Calidad de voz**: Síntesis de voz nativa integrada
- **Transcripción integrada**: Whisper integrado en OpenAI Realtime API
- **Costo eficiente**: $0.15/1M tokens entrada, $0.60/1M tokens salida
- **Simplicidad**: Una sola API para todo el flujo de voz
- **WebSockets nativos**: Comunicación bidireccional en tiempo real
- **Personalidades**: Capacidad de mantener personajes consistentes

**Alternativas consideradas:**

- **OpenAI GPT-4o-mini-realtime**: Mayor calidad con latencia ultra-baja y arquitectura simplificada
- **GPT-4 + TTS externo**: Mejor calidad de texto pero sin tiempo real
- **Whisper + Claude + TTS**: Múltiples APIs, mayor latencia y complejidad

#### OpenAI Whisper (STT)

**¿Por qué Whisper integrado?**

- **Calidad superior**: Mejor transcripción del mercado
- **Múltiples idiomas**: Soporte nativo para español y acentos
- **Integración nativa**: Parte del flujo de GPT-4o-mini-realtime
- **Sin costos adicionales**: Incluido en el precio de la API de tiempo real

#### OpenAI TTS (Síntesis de Voz)

**¿Por qué TTS de OpenAI?**

- **Voces naturales**: Calidad profesional de síntesis
- **Múltiples voces**: 6 voces diferentes disponibles
- **Integración perfecta**: Parte del flujo de tiempo real
- **Latencia mínima**: Sin delays adicionales de conversión
- **Consistencia**: Mismo proveedor para todo el flujo

**Ventajas del enfoque unificado:**

- **Simplicidad**: Una sola API key, una sola integración
- **Confiabilidad**: Menos puntos de falla
- **Mantenimiento**: Menos dependencias externas
- **Costo predecible**: Un solo modelo de precios
- **Desarrollo rápido**: Menos tiempo de integración

### Infrastructure Selection

#### Vercel (Frontend)

**¿Por qué Vercel?**

- **Optimizado para Next.js**: Creado por el mismo equipo
- **Deploy automático**: Conecta GitHub, deploy en cada push
- **Plan gratuito generoso**: 100GB bandwidth/mes
- **CDN global**: Performance excelente mundialmente
- **HTTPS incluido**: Certificados automáticos

#### Fly.io (Backend)

**¿Por qué Fly.io?**

- **WebSockets nativos**: Perfecto para audio en tiempo real
- **Sin cold starts**: Aplicaciones siempre activas
- **Docker nativo**: Mismo setup que desarrollo
- **Pay-as-you-go**: Sin tarifa mínima, facturas <$5 exoneradas
- **Performance superior**: Mejor para aplicaciones en tiempo real

**Alternativas consideradas:**

- **Render**: Plan gratuito disponible, pero con cold starts (15-30s)
- **Railway**: $5/mes, no hay plan gratuito
- **Heroku**: Muy caro para MVP

#### Supabase (Database)

**¿Por qué Supabase?**

- **PostgreSQL completo**: Base de datos robusta desde el inicio
- **Plan gratuito**: 500MB, 50MB archivos, 2GB bandwidth
- **API automática**: REST y GraphQL generados automáticamente
- **Auth incluido**: Sistema de autenticación (futuro)
- **Real-time**: WebSockets para actualizaciones en tiempo real
- **Dashboard**: Interfaz web para gestión de datos

**Alternativas consideradas:**

- **SQLite**: Más simple pero limitado para escalabilidad
- **MongoDB Atlas**: NoSQL, menos apropiado para nuestro caso
- **PlanetScale**: MySQL, menos features que Supabase

### Development Approach

#### Docker-Only Development

**¿Por qué solo Docker?**

- **Consistencia**: Mismo entorno en desarrollo, staging y producción
- **Simplicidad**: No necesitas instalar Node.js, Python, etc.
- **Aislamiento**: Cada servicio en su propio contenedor
- **Escalabilidad**: Fácil agregar más servicios
- **Onboarding**: Nuevos desarrolladores solo necesitan Docker

#### Next.js App Router

**¿Por qué Next.js 15+ con App Router?**

- **SSR/SSG**: Mejor SEO para páginas públicas
- **Performance**: Optimizaciones automáticas
- **Developer Experience**: Hot reload, TypeScript, etc.
- **Ecosistema**: Amplia comunidad y recursos
- **Vercel integration**: Deploy optimizado

#### UI/UX Design System

**¿Por qué Tailwind CSS + Design System?**

- **Consistency**: Sistema de diseño coherente
- **Accessibility**: Componentes accesibles por defecto
- **Dark Mode**: Modo oscuro nativo y toggle
- **Responsive**: Mobile-first approach
- **Performance**: CSS optimizado y purgado
- **Developer Experience**: Clases utilitarias rápidas

**Componentes de Diseño:**

- **Design Tokens**: Colores, tipografías, espaciados consistentes
- **Component Library**: Botones, inputs, cards reutilizables
- **Accessibility**: ARIA labels, keyboard navigation, screen readers
- **Animations**: Transiciones suaves y micro-interacciones
- **Loading States**: Skeleton loaders y spinners
- **Error States**: Mensajes de error claros y accionables

#### FastAPI + WebSockets

**¿Por qué FastAPI?**

- **Performance**: Muy rápido, comparable a Node.js
- **WebSockets nativos**: Perfecto para audio en tiempo real
- **Documentación automática**: Swagger/OpenAPI incluido
- **Type hints**: Mejor DX con Python
- **Async/await**: Ideal para operaciones de IA

### Cost Analysis

#### Costo Total MVP: ~$0-5/mes

- **Vercel**: Gratis (100GB bandwidth)
- **Fly.io**: Pay-as-you-go (facturas <$5 exoneradas)
- **Supabase**: Gratis (500MB database)
- **OpenAI GPT-4o-mini-realtime**: ~$0.20 por conversación (STT + conversación + TTS)
- **Total por conversación**: ~$0.20

#### Escalabilidad

- **100 conversaciones/mes**: ~$20/mes
- **1000 conversaciones/mes**: ~$200/mes
- **Upgrade paths**: Fácil migrar a planes pagos cuando sea necesario

#### Ventajas de Costo

- **60% más barato**: vs. soluciones multi-API (~$0.50)
- **Una sola API**: Menos complejidad de facturación
- **Precios predecibles**: Modelo de tokens estándar
- **Sin costos ocultos**: Todo incluido en el precio base
