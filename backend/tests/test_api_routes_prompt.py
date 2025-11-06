"""
Tests for prompt API routes
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from fastapi import FastAPI

from src.api.routes.prompt import router, get_prompt_service
from src.shared.application.prompt_service import PromptService


@pytest.fixture
def app():
    """Create FastAPI app with prompt router"""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_prompt_service():
    """Create mock prompt service"""
    service = Mock(spec=PromptService)
    service.get_all_available_options.return_value = {
        'industries': [
            {'id': 'real_estate', 'name': 'Real Estate'}
        ],
        'situations': [
            {'id': 'discovery_no_urgency_price', 'name': 'Discovery'}
        ],
        'psychologies': [
            {'id': 'conservative_analytical', 'name': 'Conservative'}
        ],
        'identities': [
            {'id': 'ana_garcia', 'name': 'Ana García'}
        ]
    }
    service.get_total_combinations.return_value = 1
    service.validate_combination.return_value = True
    service.generate_prompt.return_value = "Test prompt content"
    service.get_prompt_telemetry.return_value = {
        'prompt_hash': 'abc123',
        'prompt_length': 100,
        'word_count': 20,
        'validation_warnings': 0
    }
    return service


def test_get_available_options(client, mock_prompt_service):
    """Test getting available configuration options"""
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.get("/api/v1/prompts/options")
        
        assert response.status_code == 200
        data = response.json()
        assert 'industries' in data
        assert 'situations' in data
        assert 'psychologies' in data
        assert 'identities' in data
        assert len(data['industries']) > 0


def test_validate_combination_valid(client, mock_prompt_service):
    """Test validating a valid combination"""
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.post("/api/v1/prompts/validate", params={
            'industry_id': 'real_estate',
            'situation_id': 'discovery_no_urgency_price',
            'psychology_id': 'conservative_analytical',
            'identity_id': 'ana_garcia'
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True


def test_validate_combination_invalid(client, mock_prompt_service):
    """Test validating an invalid combination"""
    mock_prompt_service.validate_combination.return_value = False
    
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.post("/api/v1/prompts/validate", params={
            'industry_id': 'invalid',
            'situation_id': 'invalid',
            'psychology_id': 'invalid',
            'identity_id': 'invalid'
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is False


def test_generate_prompt_success(client, mock_prompt_service):
    """Test successful prompt generation"""
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.post("/api/v1/prompts/generate", params={
            'industry_id': 'real_estate',
            'situation_id': 'discovery_no_urgency_price',
            'psychology_id': 'conservative_analytical',
            'identity_id': 'ana_garcia'
        })
        
        assert response.status_code == 200
        data = response.json()
        assert 'prompt' in data
        assert len(data['prompt']) > 0


def test_generate_prompt_invalid_combination(client, mock_prompt_service):
    """Test prompt generation with invalid combination"""
    mock_prompt_service.validate_combination.return_value = False
    
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.post("/api/v1/prompts/generate", params={
            'industry_id': 'invalid',
            'situation_id': 'invalid',
            'psychology_id': 'invalid',
            'identity_id': 'invalid'
        })
        
        assert response.status_code == 400


def test_get_prompt_telemetry_success(client, mock_prompt_service):
    """Test getting prompt telemetry"""
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.get("/api/v1/prompts/telemetry", params={
            'industry_id': 'real_estate',
            'situation_id': 'discovery_no_urgency_price',
            'psychology_id': 'conservative_analytical',
            'identity_id': 'ana_garcia'
        })
        
        assert response.status_code == 200
        data = response.json()
        assert 'prompt_hash' in data
        assert 'prompt_length' in data
        assert 'word_count' in data


def test_get_total_combinations(client, mock_prompt_service):
    """Test getting total combinations count"""
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.get("/api/v1/prompts/combinations/count")
        
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert data['total'] > 0


def test_generate_prompt_with_error(client, mock_prompt_service):
    """Test prompt generation with service error"""
    mock_prompt_service.generate_prompt.side_effect = Exception("Service error")
    
    with patch('src.api.routes.prompt.get_prompt_service', return_value=mock_prompt_service):
        response = client.post("/api/v1/prompts/generate", params={
            'industry_id': 'real_estate',
            'situation_id': 'discovery_no_urgency_price',
            'psychology_id': 'conservative_analytical',
            'identity_id': 'ana_garcia'
        })
        
        assert response.status_code == 500

