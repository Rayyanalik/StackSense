import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.recommendation import RecommendationService
from app.data.processing.data_processor import DataProcessor
from app.data.collection.github_collector import GitHubCollector
from app.data.collection.stackoverflow_collector import StackOverflowCollector
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_collectors():
    with patch('app.services.recommendation.GitHubCollector') as mock_github, \
         patch('app.services.recommendation.StackOverflowCollector') as mock_stackoverflow:
        
        # Mock GitHub collector
        mock_github_instance = MagicMock()
        mock_github_instance.collect_data.return_value = [
            {
                'name': 'Test Project 1',
                'description': 'A web application using React and Node.js',
                'technologies': ['React', 'Node.js', 'MongoDB'],
                'metadata': {'stars': 1000, 'forks': 100}
            }
        ]
        mock_github.return_value = mock_github_instance
        
        # Mock StackOverflow collector
        mock_stackoverflow_instance = MagicMock()
        mock_stackoverflow_instance.collect_data.return_value = [
            {
                'name': 'Test Question 1',
                'description': 'How to use React with Node.js?',
                'technologies': ['React', 'Node.js'],
                'metadata': {'score': 50, 'answers': 10}
            }
        ]
        mock_stackoverflow.return_value = mock_stackoverflow_instance
        
        yield mock_github_instance, mock_stackoverflow_instance

def test_complete_recommendation_flow(client, mock_collectors):
    """Test the complete flow from API request to recommendation response."""
    # Test data
    project_description = {
        "description": "I want to build a modern web application with real-time features",
        "requirements": ["Scalability", "Real-time updates"],
        "constraints": ["Must use open-source technologies"]
    }
    
    # Make request to recommendation endpoint
    response = client.post("/api/recommend", json=project_description)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "primary_tech_stack" in data
    assert "alternatives" in data
    assert "explanation" in data
    assert "confidence_level" in data
    assert "similar_projects" in data
    
    # Verify data collection was called
    mock_github, mock_stackoverflow = mock_collectors
    mock_github.collect_data.assert_called_once()
    mock_stackoverflow.collect_data.assert_called_once()

def test_error_handling_flow(client, mock_collectors):
    """Test error handling in the complete flow."""
    mock_github, _ = mock_collectors
    mock_github.collect_data.side_effect = Exception("GitHub API error")
    
    # Test data
    project_description = {
        "description": "Test project",
        "requirements": [],
        "constraints": []
    }
    
    # Make request to recommendation endpoint
    response = client.post("/api/recommend", json=project_description)
    
    # Verify error response
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert "GitHub API error" in data["error"]

def test_rate_limiting_integration(client):
    """Test rate limiting in the complete flow."""
    # Test data
    project_description = {
        "description": "Test project",
        "requirements": [],
        "constraints": []
    }
    
    # Make multiple requests in quick succession
    responses = []
    for _ in range(6):  # Assuming rate limit is 5 requests per minute
        response = client.post("/api/recommend", json=project_description)
        responses.append(response)
    
    # Verify rate limiting
    assert any(r.status_code == 429 for r in responses)

def test_data_processing_integration(client, mock_collectors):
    """Test data processing in the complete flow."""
    # Test data with special characters and invalid formats
    project_description = {
        "description": "Test project with <script>alert('xss')</script>",
        "requirements": ["Requirement 1", "Requirement 2"],
        "constraints": ["Constraint 1"]
    }
    
    # Make request to recommendation endpoint
    response = client.post("/api/recommend", json=project_description)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Check that XSS was prevented
    assert "<script>" not in data["explanation"]
    
    # Verify similar projects were processed
    for project in data["similar_projects"]:
        assert isinstance(project["technologies"], list)
        assert all(isinstance(tech, str) for tech in project["technologies"])

def test_health_check_integration(client):
    """Test health check endpoint in the complete flow."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data

def test_available_technologies_integration(client, mock_collectors):
    """Test available technologies endpoint in the complete flow."""
    response = client.get("/api/technologies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(tech, str) for tech in data) 