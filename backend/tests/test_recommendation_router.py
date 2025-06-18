import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import json

client = TestClient(app)

@pytest.fixture
def mock_recommendation_service():
    with patch('app.routes.recommendation.RecommendationService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.get_recommendation.return_value = {
            "primary_stack": ["React", "Node.js", "MongoDB"],
            "alternatives": ["Vue.js", "Express", "PostgreSQL"],
            "explanation": "This stack is recommended for web applications",
            "confidence": 0.85,
            "similar_projects": [
                {
                    "name": "Sample Project",
                    "description": "A sample project",
                    "technologies": ["React", "Node.js"],
                    "metadata": {"stars": 1000}
                }
            ]
        }
        mock_instance.get_available_technologies.return_value = [
            "React", "Node.js", "MongoDB", "Vue.js", "Express", "PostgreSQL"
        ]
        yield mock_instance

def test_get_recommendation_success(mock_recommendation_service):
    response = client.post(
        "/api/recommend",
        json={
            "description": "A web application with real-time features",
            "requirements": ["user authentication", "database storage"],
            "constraints": ["budget-friendly", "quick to deploy"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "primary_stack" in data
    assert "alternatives" in data
    assert "explanation" in data
    assert "confidence" in data
    assert "similar_projects" in data

def test_get_recommendation_validation_error():
    response = client.post(
        "/api/recommend",
        json={
            "description": "test",  # Too short
            "requirements": [],
            "constraints": []
        }
    )
    
    assert response.status_code == 422
    assert "description" in response.json()["detail"][0]["loc"]

def test_get_recommendation_service_error(mock_recommendation_service):
    mock_recommendation_service.get_recommendation.side_effect = Exception("Service error")
    
    response = client.post(
        "/api/recommend",
        json={
            "description": "A web application with real-time features",
            "requirements": [],
            "constraints": []
        }
    )
    
    assert response.status_code == 500
    assert "Failed to get recommendation" in response.json()["detail"]

def test_get_available_technologies_success(mock_recommendation_service):
    response = client.get("/api/technologies")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(tech, str) for tech in data)

def test_get_available_technologies_service_error(mock_recommendation_service):
    mock_recommendation_service.get_available_technologies.side_effect = Exception("Service error")
    
    response = client.get("/api/technologies")
    
    assert response.status_code == 500
    assert "Failed to get technologies" in response.json()["detail"]

def test_rate_limiting():
    # Make multiple requests quickly
    for _ in range(10):
        response = client.post(
            "/api/recommend",
            json={
                "description": "A web application with real-time features",
                "requirements": [],
                "constraints": []
            }
        )
    
    # Next request should be rate limited
    response = client.post(
        "/api/recommend",
        json={
            "description": "A web application with real-time features",
            "requirements": [],
            "constraints": []
        }
    )
    
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_cors_headers():
    response = client.options(
        "/api/recommend",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
    )
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers 