# Tech Context: Conversation Simulator

## Technologies Used

### Frontend

- **Next.js 15+**: App Router, SSR/SSG, optimización automática
- **TypeScript**: Tipado estático, mejor DX, menos errores
- **Tailwind CSS**: Styling utilitario, modo oscuro por defecto
- **Web Audio API**: Captura y reproducción de audio
- **WebRTC**: Streaming de audio en tiempo real

### Backend

- **FastAPI**: API moderna, documentación automática, WebSockets
- **Python 3.13+**: Async/await, type hints, performance
- **WebSockets**: Comunicación bidireccional en tiempo real
- **SQLite**: Base de datos ligera para MVP
- **Pydantic**: Validación de datos, serialización

### AI Services

- **Claude Sonnet 4**: Generación de personalidades para conversación (calidad optimizada) + Análisis post-conversación (calidad optimizada)
- **ElevenLabs**: STT + TTS con acentos regionales

### Infrastructure

- **Docker**: Containerización, entorno consistente
- **Docker Compose**: Orquestación de servicios
- **Vercel**: Frontend hosting (gratis)
- **Fly.io**: Backend hosting (gratis)
- **Supabase**: Database hosting (gratis)

## Development Setup

### Prerequisites

- Docker Desktop
- Git (para versionado)
- Cuenta Vercel (para frontend)
- Cuenta Fly.io (para backend)
- Cuenta Supabase (para database)

### Environment Variables

```bash
# ElevenLabs
ELEVENLABS_API_KEY=your_api_key

# Anthropic
ANTHROPIC_API_KEY=your_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Audio Settings
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=1
AUDIO_LATENCY_TARGET=500
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
- **WebRTC**: Navegadores modernos
- **WebSockets**: Soporte universal
- **Mobile**: iOS Safari, Chrome Mobile

### Audio Quality

- **Sample Rate**: 44.1kHz para calidad profesional
- **Channels**: Mono para eficiencia
- **Format**: WAV para máxima calidad
- **Compression**: Mínima para preservar calidad

## Dependencies

### Backend Dependencies

```sh
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
elevenlabs==0.2.26
anthropic==0.7.8
pydantic==2.5.0
supabase==2.0.0
python-multipart==0.0.6
python-dotenv==1.0.0
```

### Frontend Dependencies

```sh
next@14.0.0
react@18.2.0
typescript@5.2.0
tailwindcss@3.3.0
@types/node@20.8.0
@types/react@18.2.0
@types/react-dom@18.2.0
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

#### Claude Sonnet 4 (Conversación)

**¿Por qué elegimos Sonnet 4 para conversación?**

- **Calidad de simulación**: Excelente consistencia en personalidades complejas
- **Comprensión contextual**: Superior para matices emocionales y sutilezas
- **Coherencia**: Mantiene el hilo del personaje en conversaciones largas
- **Costo-beneficio**: $3-6/1M entrada, $15-22.50/1M salida (mismo costo total)
- **Latencia aceptable**: 1-2 segundos (suficiente para conversación natural)
- **Contexto adecuado**: 200k tokens suficientes para conversaciones de 10-15 minutos
- **Estrategia de duración**: MVP optimizado para 5-8 minutos, producción para 10-15 minutos

**Alternativas consideradas:**

- **Claude Haiku 3.5**: $0.80/1M entrada, $4/1M salida (más rápido pero menos calidad de rol)
- **Claude Opus 4.1**: $15/1M entrada, $75/1M salida (muy caro para MVP)
- **GPT-5**: $1.25/1M entrada, $10/1M salida (más caro que Sonnet 4)
- **Gemini 2.5 Flash**: $0.30/1M entrada, $2.50/1M salida (más barato pero menos consistencia)

#### Claude Sonnet 4 (Análisis)

**¿Por qué elegimos Sonnet 4 para análisis?**

- **Calidad superior**: Mejor razonamiento para análisis complejos
- **Consistencia**: Mismo modelo que conversación para coherencia total
- **Análisis detallado**: Necesitamos insights profundos sobre técnicas de venta
- **Eficiencia**: Una sola API para todo el flujo de IA

#### ElevenLabs (STT + TTS)

**¿Por qué ElevenLabs completo?**

- **Simplicidad**: Una sola API para entrada y salida de audio
- **Calidad excepcional**: Mejor síntesis de voz del mercado
- **Acentos regionales**: Característica diferenciadora clave
- **Costo razonable**: $0.18/1000 caracteres TTS, $0.0015/minuto STT
- **API estable**: Muy confiable, menos puntos de falla

**Alternativa más económica:**

- **Whisper + Gemini 2.5 Flash TTS**: ~$0.10 por conversación (33% más barato)
- **Trade-off**: Menos acentos disponibles, más complejidad de integración

**Alternativas consideradas:**

- **Whisper + Gemini 2.5 Flash TTS**: $0.50/1M entrada, $10/1M salida (más barato, menos acentos)
- **Whisper + Gemini 2.5 Pro TTS**: $1/1M entrada, $20/1M salida (más caro que ElevenLabs)
- **Whisper + ElevenLabs**: Mejor STT pero más complejidad
- **Azure Cognitive Services**: Más barato pero menor calidad de voz
- **Google Cloud TTS**: Buena calidad pero menos opciones de acentos

**Análisis de Costos TTS:**

- **ElevenLabs**: ~$0.15 por conversación (STT + TTS)
- **Whisper + Gemini Flash TTS**: ~$0.10 por conversación (33% más barato)
- **Whisper + Gemini Pro TTS**: ~$0.20 por conversación (33% más caro)

**Recomendación actualizada:**

- **MVP**: ElevenLabs (simplicidad, acentos regionales)
- **Optimización de costos**: Whisper + Gemini Flash TTS (33% ahorro)

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
- **Claude Sonnet 4**: ~$0.35 por conversación (conversación + análisis)
- **ElevenLabs**: ~$0.15 por conversación (STT + TTS)
- **Total por conversación**: ~$0.50

#### Escalabilidad

- **100 conversaciones/mes**: ~$50/mes
- **1000 conversaciones/mes**: ~$500/mes
- **Upgrade paths**: Fácil migrar a planes pagos cuando sea necesario
