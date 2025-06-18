import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.recommendation_service import RecommendationService
from unittest.mock import Mock, patch

client = TestClient(app)

@pytest.fixture
def mock_recommendation_service():
    with patch('app.api.routes.RecommendationService') as mock:
        yield mock

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert all(comp["status"] in ["healthy", "degraded", "unhealthy"] 
              for comp in data["components"].values())

def test_recommendation_endpoint_success(mock_recommendation_service):
    """Test successful recommendation request."""
    # Mock the recommendation service response
    mock_response = {
        "primary_stack": ["React", "Node.js", "MongoDB"],
        "alternatives": ["Vue.js", "Express", "PostgreSQL"],
        "explanation": "This stack is recommended for web applications",
        "confidence": 0.85,
        "similar_projects": [
            {
                "name": "Sample Project",
                "description": "A sample project",
                "technologies": ["React", "Node.js"],
                "metadata": {}
            }
        ]
    }
    mock_recommendation_service.return_value.get_recommendation.return_value = mock_response

    # Test the endpoint
    response = client.post(
        "/api/recommend",
        json={
            "description": "I need a web application",
            "requirements": ["scalability", "real-time"],
            "constraints": {"budget": "low"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data == mock_response
    assert "primary_stack" in data
    assert "alternatives" in data
    assert "explanation" in data
    assert "confidence" in data
    assert "similar_projects" in data

def test_recommendation_endpoint_validation():
    """Test input validation for recommendation endpoint."""
    # Test empty description
    response = client.post(
        "/api/recommend",
        json={"description": ""}
    )
    assert response.status_code == 422

    # Test missing description
    response = client.post(
        "/api/recommend",
        json={}
    )
    assert response.status_code == 422

def test_recommendation_endpoint_error_handling(mock_recommendation_service):
    """Test error handling in recommendation endpoint."""
    # Mock service to raise an exception
    mock_recommendation_service.return_value.get_recommendation.side_effect = Exception("Test error")

    response = client.post(
        "/api/recommend",
        json={"description": "Test project"}
    )
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data

def test_recommendation_endpoint_rate_limiting():
    """Test rate limiting for recommendation endpoint."""
    # Make multiple requests in quick succession
    for _ in range(10):
        response = client.post(
            "/api/recommend",
            json={"description": "Test project"}
        )
    
    # The last request should be rate limited
    assert response.status_code == 429

def test_recommendation_endpoint_cors():
    """Test CORS headers for recommendation endpoint."""
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