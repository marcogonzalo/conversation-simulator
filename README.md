# Conversation Simulator

Un simulador de clientes para que agentes de ventas puedan practicar y mejorar sus habilidades interactuando con una IA que simule a un potencial comprador con un perfil y personalidad específica.

## 🚀 Características

- **Conversación de voz bidireccional** en tiempo real con latencia <500ms
- **Múltiples perfiles de cliente** con personalidades distintivas y acentos regionales
- **Análisis automático post-conversación** con feedback detallado y accionable
- **Recomendaciones personalizadas** de contenido educativo basado en performance
- **Interfaz minimalista** enfocada en la experiencia conversacional

## �� Testing y Calidad

### Pre-commit Checks

Ejecuta las verificaciones de calidad antes de cada commit:

```bash
# Ejecutar todas las verificaciones
./tests/scripts/pre-commit.sh

# Solo backend
cd backend
python -m pytest tests/ -v --cov=src --cov-fail-under=80
python -m mypy src/
python -m black --check src/
python -m isort --check-only src/

# Solo frontend
cd frontend
npm run test:coverage
npm run type-check
npm run lint
npx prettier --check "src/**/*.{js,jsx,ts,tsx,json,css,md}"
```

### Cobertura de Tests

- **Backend**: Mínimo 80% de cobertura
- **Frontend**: Mínimo 80% de cobertura
- **Exclusiones**: Frameworks y librerías de terceros

## ⚙️ Configuración

### Variables de Entorno

El proyecto usa variables de entorno para configurar las URLs de la API y WebSocket.

#### Frontend

Crea un archivo `.env.local` en el directorio `frontend/` basado en `frontend-env.example`:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000

# Para producción:
# NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
# NEXT_PUBLIC_WS_BASE_URL=wss://your-api-domain.com
```

#### Backend

Crea un archivo `.env` en el directorio raíz basado en `env.example`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./data/conversation_simulator.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🛠️ Reglas de Desarrollo

Este proyecto sigue un conjunto estricto de reglas de desarrollo configuradas en archivos `.mdc` en `.cursor/rules/` según el [sistema actual de Cursor](https://docs.cursor.com/es/context/rules):

### 🏗️ Arquitectura

- **Arquitectura Hexagonal (DDD)**: Separación clara entre dominio, aplicación e infraestructura
- **CQRS Pattern**: Commands y Queries separados
- **Event-Driven Architecture**: Comunicación entre contextos via Event Bus
- **Repository Pattern**: Interfaces abstractas + implementaciones concretas

### 🧪 Testing

- **TDD Estricto**: Tests antes del código, cobertura mínima 80%
- **Edge Cases**: Incluir casos límite y escenarios de error
- **Test Markers**: Usar markers de pytest (unit, integration, slow, audio, websocket, api, database)
- **Frontend Testing**: Cobertura 80% con Testing Library

### 🐳 Docker y Entornos

- **Docker por Entorno**: Dockerfiles específicos para cada servicio
- **Docker Compose**: Solo en raíz del proyecto
- **Debugging**: Configuración debugpy para Python, debugging desde editor
- **Multi-stage Builds**: Optimización de imágenes de producción

### 💻 Código y Estilo

- **Imports Absolutos**: Rutas absolutas preferidas
- **Console Debugging**: `print('variable_name', variable_name)`
- **TypeScript Estricto**: Tipado completo, evitar 'any'
- **Python Type Hints**: Type hints en todas las funciones

### 🎨 Frontend

- **Modo Oscuro**: Implementación obligatoria, oscuro por defecto
- **Build Validation**: Build exitoso después de cambios
- **Component Structure**: Componentes pequeños y reutilizables
- **Responsive Design**: Mobile-first con Tailwind

### 🔊 Audio y Tiempo Real

- **WebSocket Performance**: Latencia <500ms
- **Audio Formats**: WAV para compatibilidad
- **VAD Optimization**: Configuración optimizada
- **Error Recovery**: Recuperación automática en fallos

## 🛠️ Tecnologías

### Backend

- FastAPI 0.116.1
- Python 3.13+
- WebSockets
- OpenAI API
- Supabase
- Pydantic
- SQLAlchemy

### Frontend

- Next.js 15+
- React 18.2.0
- TypeScript 5.2.0
- Tailwind CSS 3.3.0
- Web Audio API
- Zustand
- Framer Motion

### Infrastructure

- Docker & Docker Compose
- Vercel (Frontend)
- Fly.io (Backend)
- Supabase (Database)

## 📦 Instalación

### Prerrequisitos

- Docker Desktop
- Git
- Cuentas en:
  - OpenAI (API key)
  - Supabase (URL y anon key)

### Configuración

#### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd conversation-simulator
```

#### 2. Configurar variables de entorno

```bash
cp env.example .env
```

Editar `.env` con tus API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

#### 3. Ejecutar con Docker

```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up --build

# Producción
docker-compose up --build
```

## 🎯 Perfiles de Persona

### María Rodríguez (Peruana)

- **Perfil**: Directora de Marketing, escéptica pero analítica
- **Acento**: Peruano
- **Personalidad**: Pragmática, busca ROI comprobable
- **Presupuesto**: $5,000 - $15,000 mensuales

### Carlos Mendoza (Venezolano)

- **Perfil**: CEO de startup, entusiasta de la innovación
- **Acento**: Venezolano
- **Personalidad**: Innovador, impaciente, presupuesto limitado
- **Presupuesto**: $500 - $2,000 mensuales

### Ana García (Cubana)

- **Perfil**: Gerente de Ventas, conservadora pero interesada en modernizar
- **Acento**: Caribeño (Cubano)
- **Personalidad**: Conservadora, amigable, cautelosa
- **Presupuesto**: $3,000 - $8,000 mensuales

## 🔄 Flujo de Conversación

1. **Selección de Persona**: Usuario elige un perfil de cliente
2. **Inicio de Conversación**: Se establece conexión WebSocket
3. **Conversación de Voz**:
   - Usuario habla → OpenAI Realtime API → Respuesta de audio directa
   - Flujo audio-to-audio en tiempo real sin conversiones intermedias
4. **Análisis Post-Conversación**: OpenAI analiza la conversación
5. **Reporte de Feedback**: Métricas, fortalezas, debilidades y recomendaciones

## 📊 Análisis de Performance

El sistema analiza:

- **Técnicas de apertura y calificación**
- **Manejo de objeciones**
- **Presentación de valor**
- **Intentos de cierre**
- **Escucha activa**
- **Preguntas efectivas**
- **Construcción de rapport**

## 🚀 Deployment

### Frontend (Vercel)

```bash
# Conectar repositorio a Vercel
# Configurar variables de entorno en Vercel
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_WS_URL=wss://your-backend-url.com/ws
```

### Backend (Fly.io)

```bash
# Instalar Fly CLI
# Configurar fly.toml
# Deploy
fly deploy
```

### Database (Supabase)

- Crear proyecto en Supabase
- Configurar tablas según modelos
- Obtener URL y anon key

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📈 Métricas de Éxito

- **Latencia de audio**: <500ms
- **Tasa de finalización**: >80%
- **Satisfacción del usuario**: Feedback positivo
- **Retención**: Múltiples sesiones por usuario
- **Cobertura de tests**: >80%
- **Build success rate**: 100%

## 🔧 Desarrollo

### Estructura del Proyecto

```mermaid
conversation-simulator/
├── backend/                           # FastAPI + DDD
│   ├── src/
│   │   ├── api/                      # API Gateway y rutas
│   │   │   ├── gateway.py
│   │   │   └── routes/               # Endpoints por dominio
│   │   ├── analysis/                 # Bounded Context: Análisis
│   │   │   ├── application/          # Application Layer
│   │   │   │   ├── commands/         # Command handlers
│   │   │   │   ├── queries/          # Query handlers
│   │   │   │   └── services/         # Application services
│   │   │   ├── domain/               # Domain Layer
│   │   │   │   ├── entities/         # Domain entities
│   │   │   │   ├── value_objects/    # Value objects
│   │   │   │   ├── repositories/     # Repository interfaces
│   │   │   │   └── services/         # Domain services
│   │   │   └── infrastructure/       # Infrastructure Layer
│   │   │       ├── repositories/     # Repository implementations
│   │   │       └── services/         # External service adapters
│   │   ├── audio/                    # Bounded Context: Audio
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   ├── conversation/             # Bounded Context: Conversación
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   ├── persona/                  # Bounded Context: Persona
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   ├── shared/                   # Shared Kernel
│   │   │   ├── domain/               # Shared domain concepts
│   │   │   └── infrastructure/       # Shared infrastructure
│   │   └── main.py                   # Application entry point
│   ├── data/                         # Datos estáticos
│   │   ├── personas/                 # YAML personas
│   │   ├── conversations/            # Datos de conversaciones
│   │   └── analyses/                 # Análisis guardados
│   ├── Dockerfile                    # Production container
│   ├── Dockerfile.dev                # Development container
│   └── requirements.txt
├── frontend/                         # Next.js 15+
│   ├── src/
│   │   ├── app/                     # App Router
│   │   │   ├── analysis/[id]/       # Páginas de análisis
│   │   │   ├── conversation/[id]/   # Páginas de conversación
│   │   │   ├── api/                 # API routes
│   │   │   └── globals.css
│   │   ├── components/              # React components
│   │   │   ├── analysis/            # Componentes de análisis
│   │   │   ├── conversation/        # Componentes de conversación
│   │   │   ├── persona/             # Componentes de persona
│   │   │   ├── layout/              # Componentes de layout
│   │   │   ├── providers/           # Context providers
│   │   │   └── ui/                  # UI components base
│   │   ├── lib/                     # Utilities
│   │   ├── store/                   # Zustand stores
│   │   └── types/                   # TypeScript types
│   ├── Dockerfile                   # Production container
│   ├── Dockerfile.dev               # Development container
│   └── package.json
├── .cursor/                         # Cursor AI configuration
│   └── rules/                       # Development rules (.mdc files)
│       ├── architecture.mdc         # Architecture patterns
│       ├── testing.mdc              # Testing and quality rules
│       ├── backend.mdc              # Backend-specific rules
│       ├── frontend.mdc             # Frontend-specific rules
│       ├── audio.mdc                # Audio and real-time rules
│       ├── domain.mdc               # Domain-specific rules
│       ├── security.mdc             # Security and best practices
│       └── workflow.mdc             # Workflow and project management
├── memory-bank/                      # Documentación del proyecto
├── docker-compose.yml               # Production
├── docker-compose.dev.yml           # Development
├── env.example                      # Variables de entorno
└── README.md
```

### Comandos Útiles

```bash
# Desarrollo completo
docker-compose -f docker-compose.dev.yml up --build

# Solo backend
docker-compose -f docker-compose.dev.yml up backend

# Solo frontend
docker-compose -f docker-compose.dev.yml up frontend

# Logs
docker-compose logs -f [service]

# Rebuild
docker-compose -f docker-compose.dev.yml up --build --force-recreate

# Pre-commit checks
./tests/scripts/pre-commit.sh

# Debugging
# Usar configuración en .vscode/launch.json
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Aplicar reglas de desarrollo (TDD, linting, testing)
4. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
5. Push al branch (`git push origin feature/AmazingFeature`)
6. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte, email <support@conversationsimulator.com> o crear un issue en GitHub.

## 🗺️ Roadmap

- [ ] Panel de administración para gestión de perfiles
- [ ] Avatares digitales animados
- [ ] Métricas avanzadas y analytics
- [ ] Sistema de usuarios y autenticación
- [ ] Múltiples idiomas
- [ ] Integración con LMS
