"""
OpenAI service for provisional AI integration.
"""
import json
import logging
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp

from src.shared.domain.interfaces.ai_service_interface import AIServiceInterface
from src.shared.infrastructure.external_apis.api_config import api_config

logger = logging.getLogger(__name__)


class OpenAIService(AIServiceInterface):
    """Service for OpenAI API integration (provisional)."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.api_config = api_config
        logger.info(f"OpenAI Service initialized with model: {model}")
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.model
    
    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "openai"
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        raise Exception(f"OpenAI API error: {response.status}")
        
        except asyncio.TimeoutError:
            logger.error("OpenAI API timeout")
            raise Exception("OpenAI API timeout")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def generate_conversation_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate conversation response with context."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return await self.generate_response(
            messages=messages,
            temperature=self.api_config.ai_temperature,
            max_tokens=self.api_config.ai_max_tokens
        )
    
    async def analyze_conversation(
        self,
        conversation_data: Dict[str, Any],
        analysis_prompt: str
    ) -> Dict[str, Any]:
        """Analyze conversation using OpenAI."""
        try:
            # Build analysis context
            context = self._build_analysis_context(conversation_data)
            
            messages = [
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": context}
            ]
            
            response = await self.generate_response(
                messages=messages,
                temperature=0.3,  # Lower temperature for analysis
                max_tokens=2000
            )
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"analysis": response}
        
        except Exception as e:
            logger.error(f"Conversation analysis failed: {e}")
            raise
    
    def _build_analysis_context(self, conversation_data: Dict[str, Any]) -> str:
        """Build context for conversation analysis."""
        context_parts = [
            f"Conversation ID: {conversation_data.get('conversation_id', 'N/A')}",
            f"Duration: {conversation_data.get('duration_seconds', 0)} seconds",
            f"Total Messages: {conversation_data.get('total_messages', 0)}",
            f"User Messages: {conversation_data.get('user_messages', 0)}",
            f"Assistant Messages: {conversation_data.get('assistant_messages', 0)}",
            "",
            "CONVERSATION DATA:",
            json.dumps(conversation_data, indent=2, ensure_ascii=False)
        ]
        
        return "\n".join(context_parts)
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
