# Guía de Integración de Proveedores de IA

Esta guía explica cómo agregar nuevos proveedores de IA (como Gemini, Anthropic, etc.) al Conversation Simulator.

## Descripción General

El sistema soporta dos tipos de proveedores de IA:

1. **Proveedores de IA para Texto**: Para conversaciones basadas en texto y análisis (OpenAI GPT, Gemini, Claude, etc.)
2. **Proveedores de IA para Voz**: Para conversaciones de voz en tiempo real (OpenAI Realtime API, Gemini Live API, etc.)

Ambos tipos usan interfaces abstractas para garantizar código agnóstico del proveedor en toda la aplicación.

## Arquitectura

```sh
┌─────────────────────────────────────────────────────────────┐
│                     Capa de Aplicación                      │
│       (Conversaciones, Análisis, Orquestación de Voz)       │
└────────────────┬─────────────────────────┬──────────────────┘
                 │                         │
                 ▼                         ▼
    ┌────────────────────────┐  ┌─────────────────────────┐
    │   AIServiceInterface   │  │  VoiceServiceInterface  │
    │ (Conversaciones texto) │  │   (Conversaciones voz)  │
    └────────────────────────┘  └─────────────────────────┘
                 │                         │
     ┌───────────┴───────────┐ ┌───────────┴─────────────┐
     ▼                       ▼ ▼                         ▼
┌──────────┐            ┌──────────┐              ┌──────────┐
│  OpenAI  │            │  Gemini  │              │  Futuro  │
│ Service  │            │ Service  │              │ Provider │
└──────────┘            └──────────┘              └──────────┘
```

## Agregar un Proveedor de IA para Texto

### Paso 1: Implementar AIServiceInterface

Crea un nuevo archivo de servicio en `backend/src/shared/infrastructure/external_apis/`:

```python
# backend/src/shared/infrastructure/external_apis/gemini_service.py
"""
Gemini service for text-based AI integration.
"""
import logging
from typing import Dict, Any, List, Optional

from src.shared.domain.interfaces.ai_service_interface import AIServiceInterface

logger = logging.getLogger(__name__)


class GeminiService(AIServiceInterface):
    """Service for Google Gemini API integration."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        logger.info(f"Gemini Service initialized with model: {model}")
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.model
    
    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "gemini"
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using Gemini API."""
        # Implementar llamada a la API de Gemini aquí
        pass
    
    async def generate_conversation_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate conversation response with context."""
        # Implementar llamada a la API de conversación de Gemini aquí
        pass
    
    async def analyze_conversation(
        self,
        conversation_data: Dict[str, Any],
        analysis_prompt: str
    ) -> Dict[str, Any]:
        """Analyze conversation using Gemini."""
        # Implementar llamada de análisis de Gemini aquí
        pass
    
    async def health_check(self) -> bool:
        """Check if Gemini service is accessible."""
        # Implementar health check aquí
        pass
```

### Paso 2: Actualizar APIConfig

Agrega la configuración para el nuevo proveedor en `backend/src/shared/infrastructure/external_apis/api_config.py`:

```python
class APIConfig:
    def __init__(self):
        # ... configuración existente ...
        
        # Configuración de Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        self.gemini_temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
```

### Paso 3: Actualizar AIServiceFactory

Agrega el nuevo proveedor a `backend/src/shared/infrastructure/external_apis/ai_service_factory.py`:

```python
class AIServiceFactory:
    # Actualizar proveedores soportados
    _SUPPORTED_PROVIDERS = ["openai", "gemini"]
    
    @staticmethod
    def create_ai_service(ai_provider: str = None, api_key: str = None, model: str = None, **kwargs):
        try:
            provider = (ai_provider or api_config.text_ai_provider).lower()
            key = api_key or AIServiceFactory._get_api_key_for_provider(provider)
            
            if not key:
                logger.error(f"No API key found for text AI provider: {provider}")
                return None
            
            if provider == "openai":
                return AIServiceFactory._create_openai_service(key, model, **kwargs)
            elif provider == "gemini":
                return AIServiceFactory._create_gemini_service(key, model, **kwargs)
            else:
                logger.error(f"Unsupported text AI provider: {provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to create text AI service: {e}")
            return None
    
    @staticmethod
    def _get_api_key_for_provider(provider: str) -> Optional[str]:
        if provider == "openai":
            return api_config.openai_api_key
        elif provider == "gemini":
            return api_config.gemini_api_key
        return None
    
    @staticmethod
    def _create_gemini_service(api_key: str, model: str = None, **kwargs):
        """Create Gemini text service."""
        try:
            from src.shared.infrastructure.external_apis.gemini_service import GeminiService
            return GeminiService(api_key=api_key, model=model or api_config.gemini_model)
        except Exception as e:
            logger.error(f"Failed to create Gemini service: {e}")
            return None
```

### Paso 4: Actualizar Configuración de Entorno

Agrega la configuración del nuevo proveedor a `env.example`:

```bash
# Configuración de Gemini (opcional)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
```

### Paso 5: Probar la Integración

Crea tests para tu nuevo proveedor en `backend/tests/`:

```python
# backend/tests/test_gemini_service.py
import pytest
from src.shared.infrastructure.external_apis.gemini_service import GeminiService

class TestGeminiService:
    def test_service_initialization(self):
        service = GeminiService(api_key="test-key", model="gemini-pro")
        assert service.provider == "gemini"
        assert service.model_name == "gemini-pro"
```

## Agregar un Proveedor de IA para Voz

### Paso 1: Implementar VoiceServiceInterface

Crea un nuevo archivo de servicio en `backend/src/audio/infrastructure/services/`:

```python
# backend/src/audio/infrastructure/services/gemini_voice_service.py
"""
Gemini Live API service for real-time voice-to-voice conversations.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, Callable

from src.shared.domain.interfaces.voice_service_interface import VoiceServiceInterface
from src.shared.infrastructure.external_apis.api_config import APIConfig

logger = logging.getLogger(__name__)


class GeminiVoiceService(VoiceServiceInterface):
    """Service for Gemini Live API voice-to-voice conversations."""
    
    def __init__(self, api_config: APIConfig):
        self.api_config = api_config
        self._is_connected = False
        self.conversation_id: Optional[str] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not self.api_config.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        # Inicializar el cliente de Gemini aquí
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._is_connected:
            await self.disconnect()
    
    async def connect(
        self,
        conversation_id: str,
        persona_config: Dict[str, Any],
        on_audio_chunk: Callable[[bytes], None],
        on_transcript: Callable[[str], None],
        on_error: Callable[[str], None],
        on_audio_complete: Optional[Callable[[], None]] = None
    ) -> bool:
        """Connect to Gemini Live API."""
        # Implementar lógica de conexión aquí
        self._is_connected = True
        return True
    
    async def disconnect(self):
        """Disconnect from Gemini Live API."""
        # Implementar lógica de desconexión aquí
        self._is_connected = False
    
    async def send_audio(self, audio_data: bytes) -> bool:
        """Send audio data to Gemini."""
        # Implementar lógica de envío de audio aquí
        return True
    
    def get_voice_for_persona(self, persona_accent: str) -> str:
        """Get appropriate voice ID for persona accent."""
        # Mapear acentos de persona a IDs de voz de Gemini
        accent_voice_map = {
            "mexicano": "gemini_voice_1",
            "peruano": "gemini_voice_2",
            # ... agregar más mapeos
        }
        return accent_voice_map.get(persona_accent.lower(), "gemini_voice_default")
    
    def get_instructions_for_persona(self, persona_config: Dict[str, Any]) -> str:
        """Generate instructions for the persona."""
        # Generar instrucciones basadas en la configuración de la persona
        pass
    
    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "gemini"
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected to voice service."""
        return self._is_connected
```

### Paso 2: Actualizar VoiceServiceFactory

Agrega el nuevo proveedor a `backend/src/shared/infrastructure/external_apis/voice_service_factory.py`:

```python
class VoiceServiceFactory:
    @staticmethod
    def create_voice_service(voice_provider: str = None, api_config_instance = None):
        try:
            provider = (voice_provider or api_config.voice_ai_provider).lower()
            config = api_config_instance or api_config
            
            if provider == "openai":
                return VoiceServiceFactory._create_openai_voice_service(config)
            elif provider == "gemini":
                return VoiceServiceFactory._create_gemini_voice_service(config)
            else:
                logger.error(f"Unsupported voice AI provider: {provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to create voice AI service: {e}")
            return None
    
    @staticmethod
    def _create_gemini_voice_service(config):
        """Create Gemini voice service."""
        try:
            from src.audio.infrastructure.services.gemini_voice_service import GeminiVoiceService
            
            if not config.gemini_api_key:
                logger.error("Gemini API key not configured")
                return None
            
            return GeminiVoiceService(api_config=config)
        except Exception as e:
            logger.error(f"Failed to create Gemini voice service: {e}")
            return None
    
    @staticmethod
    def get_available_voice_providers() -> list:
        """Get list of available voice AI providers."""
        return ["openai", "gemini"]
```

## Usar el Nuevo Proveedor

### Opción 1: Via Variables de Entorno

Configura el proveedor en tu archivo `.env`:

```bash
# Para operaciones basadas en texto
TEXT_AI_PROVIDER=gemini

# Para operaciones basadas en voz
VOICE_AI_PROVIDER=gemini
```

### Opción 2: Via Código

Sobrescribe el proveedor programáticamente:

```python
# Para conversaciones de texto
from src.shared.infrastructure.external_apis.ai_service_factory import AIServiceFactory

ai_service = AIServiceFactory.create_ai_service(
    ai_provider="gemini",
    api_key="your-api-key"
)

# Para conversaciones de voz
from src.shared.infrastructure.external_apis.voice_service_factory import VoiceServiceFactory

voice_service = VoiceServiceFactory.create_voice_service(
    voice_provider="gemini",
    api_config_instance=your_config
)
```

## Probar tu Integración

### Tests Unitarios

Crea tests unitarios completos para tu proveedor:

```python
import pytest
from your_provider_service import YourProviderService

@pytest.mark.asyncio
async def test_provider_connection():
    service = YourProviderService(api_config)
    assert await service.health_check() is True
```

### Tests de Integración

Prueba el proveedor con el flujo completo de conversación:

```bash
cd backend
docker-compose -f docker-compose.test.yml run --rm backend-test pytest tests/test_your_provider.py -v
```

## Mejores Prácticas

1. **Manejo de Errores**: Implementa manejo robusto de errores y logging
2. **Rate Limiting**: Respeta los límites de tasa del proveedor
3. **Fallback**: Implementa degradación elegante si el proveedor no está disponible
4. **Seguridad**: Nunca hardcodees API keys; siempre usa variables de entorno
5. **Documentación**: Documenta configuraciones específicas del proveedor y peculiaridades
6. **Testing**: Escribe tests comprehensivos antes de desplegar a producción

## Patrones Comunes

### Lógica de Reintentos

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_api_with_retry(self, ...):
    # Llamada a la API aquí
    pass
```

### Rate Limiting

```python
from aiolimiter import AsyncLimiter

class YourProviderService:
    def __init__(self):
        # 10 requests por segundo
        self.rate_limiter = AsyncLimiter(10, 1)
    
    async def make_request(self):
        async with self.rate_limiter:
            # Hacer llamada a la API
            pass
```

## Solución de Problemas

### Proveedor No Encontrado

Si obtienes el error "Unsupported provider":

1. Verifica que el proveedor esté agregado a `_SUPPORTED_PROVIDERS`
2. Verifica que el factory tenga el caso del proveedor
3. Asegúrate de que el archivo del servicio sea importable

### Problemas con API Key

Si obtienes el error "No API key found":

1. Verifica que la variable de entorno esté configurada
2. Verifica que `_get_api_key_for_provider()` tenga tu proveedor
3. Confirma que `api_config` carga la key correctamente

### Fallos de Conexión

Si las conexiones fallan:

1. Verifica que la API key sea válida
2. Verifica conectividad de red
3. Revisa requisitos específicos del proveedor (headers, auth, etc.)
4. Verifica el estado del servicio del proveedor

## Soporte

Para preguntas o problemas:

1. Consulta la documentación oficial del proveedor
2. Revisa implementaciones de proveedores existentes (OpenAI)
3. Crea un issue en el repositorio del proyecto
