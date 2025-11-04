#!/usr/bin/env python3
"""
Test script for voice conversation integration.
This script tests the complete voice-to-voice flow.
"""
from src.shared.infrastructure.external_apis.api_config import APIConfig
from src.audio.infrastructure.repositories.memory_audio_repository import MemoryAudioRepository
from src.audio.application.services.openai_voice_application_service import OpenAIVoiceApplicationService
from src.persona.infrastructure.repositories.yaml_persona_repository import YAMLPersonaRepository
from src.conversation.infrastructure.persistence.sql_conversation_repo import SQLConversationRepository
from src.conversation.domain.services.conversation_domain_service import ConversationDomainService
from src.conversation.application.services.conversation_application_service import ConversationApplicationService
import asyncio
import json
import logging
import os
import sys
import websockets
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceConversationTester:
    """Test the voice conversation integration."""

    def __init__(self):
        self.conversation_service = None
        self.voice_service = None
        self.persona_repo = None
        self.api_config = None

    async def setup(self):
        """Setup test services."""
        logger.info("Setting up test services...")

        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()

        # Create API config
        self.api_config = APIConfig()

        # Validate configuration
        if not self.api_config.validate_config():
            logger.error("API configuration validation failed")
            return False

        # Create services
        conversation_repo = SQLConversationRepository()
        conversation_domain_service = ConversationDomainService()
        self.conversation_service = ConversationApplicationService(
            conversation_repo, conversation_domain_service)

        audio_repo = MemoryAudioRepository()
        self.voice_service = OpenAIVoiceApplicationService(
            audio_repo, self.api_config)

        self.persona_repo = YAMLPersonaRepository()

        logger.info("Test services setup completed")
        return True

    async def test_conversation_creation(self):
        """Test conversation creation."""
        logger.info("Testing conversation creation...")

        try:
            # Create a test conversation
            result = await self.conversation_service.start_conversation(
                persona_id="ana_garcia",
                metadata={
                    "accent": "mexicano",
                    "test": True
                }
            )

            if result.success:
                logger.info(f"Conversation created: {result.conversation_id}")
                return result.conversation_id
            else:
                logger.error(f"Failed to create conversation: {result.error}")
                return None

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None

    async def test_websocket_connection(self, conversation_id: str):
        """Test WebSocket connection."""
        logger.info(
            f"Testing WebSocket connection for conversation {conversation_id}...")

        try:
            # Connect to WebSocket
            uri = f"ws://localhost:8000/api/v1/ws/conversation/{conversation_id}"
            logger.info(f"Connecting to: {uri}")

            async with websockets.connect(uri) as websocket:
                logger.info("WebSocket connected successfully")

                # Test start voice conversation
                start_message = {
                    "type": "start_voice_conversation",
                    "persona_id": "ana_garcia"
                }

                await websocket.send(json.dumps(start_message))
                logger.info("Start voice conversation message sent")

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                logger.info(f"Response received: {response_data}")

                # Test audio message (mock)
                audio_message = {
                    "type": "audio_message",
                    "audio_data": "dGVzdF9hdWRpb19kYXRh",  # base64 for "test_audio_data"
                    "audio_format": "webm"
                }

                await websocket.send(json.dumps(audio_message))
                logger.info("Audio message sent")

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                logger.info(f"Audio response received: {response_data}")

                # Test end voice conversation
                end_message = {
                    "type": "end_voice_conversation"
                }

                await websocket.send(json.dumps(end_message))
                logger.info("End voice conversation message sent")

                return True

        except Exception as e:
            logger.error(f"WebSocket test failed: {e}")
            return False

    async def test_persona_loading(self):
        """Test persona loading."""
        logger.info("Testing persona loading...")

        try:
            from src.persona.domain.value_objects.persona_id import PersonaId

            # Load a persona
            persona_id = PersonaId("ana_garcia")
            persona = await self.persona_repo.get_by_id(persona_id)

            if persona:
                logger.info(
                    f"Persona loaded: {persona.name} ({persona.accent.value})")
                return True
            else:
                logger.error("Persona not found")
                return False

        except Exception as e:
            logger.error(f"Error loading persona: {e}")
            return False

    async def run_tests(self):
        """Run all tests."""
        logger.info("Starting voice conversation integration tests...")

        # Setup
        if not await self.setup():
            logger.error("Setup failed")
            return False

        # Test persona loading
        if not await self.test_persona_loading():
            logger.error("Persona loading test failed")
            return False

        # Test conversation creation
        conversation_id = await self.test_conversation_creation()
        if not conversation_id:
            logger.error("Conversation creation test failed")
            return False

        # Test WebSocket connection
        if not await self.test_websocket_connection(conversation_id):
            logger.error("WebSocket test failed")
            return False

        logger.info(
            "All tests passed! Voice conversation integration is working.")
        return True


async def main():
    """Run the voice conversation tests."""
    tester = VoiceConversationTester()
    success = await tester.run_tests()

    if success:
        logger.info(
            "🎉 Voice conversation integration test completed successfully!")
        return True
    else:
        logger.error("❌ Voice conversation integration test failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
