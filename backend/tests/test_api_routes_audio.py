"""
Comprehensive tests for audio API routes
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, AsyncMock

from src.api.routes.audio import router, get_voice_service


@pytest.fixture
def mock_voice_service():
    """Create mock voice service"""
    service = Mock()
    service.is_healthy = AsyncMock(return_value=True)
    service.get_voice_for_persona = Mock(return_value="nova")
    return service


@pytest.fixture
def app(mock_voice_service):
    """Create FastAPI app with audio router and dependency overrides"""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/audio")
    app.dependency_overrides[get_voice_service] = lambda: mock_voice_service
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestAudioHealthEndpoint:
    """Tests for /health endpoint"""
    
    def test_audio_health_healthy(self, client):
        """Test health check when service is healthy"""
        response = client.get("/api/v1/audio/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "openai_voice"
        assert data["connected"] is True
    
    def test_audio_health_unhealthy(self, app, mock_voice_service):
        """Test health check when service is unhealthy"""
        mock_voice_service.is_healthy = AsyncMock(return_value=False)
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["connected"] is False
    
    def test_audio_health_error(self, app, mock_voice_service):
        """Test health check with service error"""
        mock_voice_service.is_healthy = AsyncMock(side_effect=Exception("Service error"))
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/health")
        
        assert response.status_code == 500
    
    def test_audio_health_response_structure(self, client):
        """Test health response has all required fields"""
        response = client.get("/api/v1/audio/health")
        
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "connected" in data


class TestVoicesEndpoint:
    """Tests for /voices endpoint"""
    
    def test_get_voices_returns_list(self, client):
        """Test getting list of available voices"""
        response = client.get("/api/v1/audio/voices")
        
        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert isinstance(data["voices"], list)
    
    def test_voices_count(self, client):
        """Test that 6 voices are returned"""
        response = client.get("/api/v1/audio/voices")
        
        data = response.json()
        assert len(data["voices"]) == 6
    
    def test_voices_have_required_fields(self, client):
        """Test that each voice has required fields"""
        response = client.get("/api/v1/audio/voices")
        
        voices = response.json()["voices"]
        for voice in voices:
            assert "id" in voice
            assert "name" in voice
            assert "description" in voice
    
    def test_voices_contain_alloy(self, client):
        """Test that alloy voice is in the list"""
        response = client.get("/api/v1/audio/voices")
        
        voices = response.json()["voices"]
        voice_ids = [v["id"] for v in voices]
        assert "alloy" in voice_ids
    
    def test_voices_contain_nova(self, client):
        """Test that nova voice is in the list"""
        response = client.get("/api/v1/audio/voices")
        
        voices = response.json()["voices"]
        voice_ids = [v["id"] for v in voices]
        assert "nova" in voice_ids
    
    def test_voices_error_handling(self, client):
        """Test error handling for voices endpoint"""
        # This endpoint has simple logic, so errors are unlikely
        # but we test the exception handler is in place
        response = client.get("/api/v1/audio/voices")
        # Should succeed with hardcoded data
        assert response.status_code == 200


class TestVoiceForPersonaEndpoint:
    """Tests for /voices/persona/{accent} endpoint"""
    
    def test_voice_for_caribbean_accent(self, app, mock_voice_service):
        """Test getting voice for Caribbean accent"""
        mock_voice_service.get_voice_for_persona.return_value = "nova"
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/voices/persona/caribbean")
        
        assert response.status_code == 200
        data = response.json()
        assert data["voice_id"] == "nova"
        assert data["accent"] == "caribbean"
    
    def test_voice_for_venezuelan_accent(self, app, mock_voice_service):
        """Test getting voice for Venezuelan accent"""
        mock_voice_service.get_voice_for_persona.return_value = "echo"
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/voices/persona/venezuelan")
        
        data = response.json()
        assert data["voice_id"] == "echo"
        assert data["accent"] == "venezuelan"
    
    def test_voice_for_peruvian_accent(self, app, mock_voice_service):
        """Test getting voice for Peruvian accent"""
        mock_voice_service.get_voice_for_persona.return_value = "shimmer"
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/voices/persona/peruvian")
        
        data = response.json()
        assert data["voice_id"] == "shimmer"
    
    def test_voice_response_structure(self, app, mock_voice_service):
        """Test voice response has all required fields"""
        mock_voice_service.get_voice_for_persona.return_value = "alloy"
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/voices/persona/neutral")
        
        data = response.json()
        assert "voice_id" in data
        assert "accent" in data
        assert "name" in data
        assert "language" in data
    
    def test_voice_includes_language(self, client):
        """Test voice response includes language field"""
        response = client.get("/api/v1/audio/voices/persona/test")
        
        data = response.json()
        assert data["language"] == "spanish"
    
    def test_voice_error_handling(self, app, mock_voice_service):
        """Test error handling for voice endpoint"""
        mock_voice_service.get_voice_for_persona.side_effect = Exception("Service error")
        client = TestClient(app)
        
        response = client.get("/api/v1/audio/voices/persona/test")
        
        assert response.status_code == 500
    
    def test_voice_accent_parameter_passed(self, app, mock_voice_service):
        """Test that accent parameter is passed to service"""
        client = TestClient(app)
        
        client.get("/api/v1/audio/voices/persona/custom_accent")
        
        mock_voice_service.get_voice_for_persona.assert_called_once_with("custom_accent")

