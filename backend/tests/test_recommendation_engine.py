import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.recommendation_engine import RecommendationEngine

@pytest.fixture
def engine():
    """Provides a RecommendationEngine instance for testing."""
    return RecommendationEngine()

def test_get_llm_prompt_formatting(engine):
    """
    Tests if the _get_llm_prompt method correctly injects the project description.
    """
    description = "a test project"
    prompt = engine._get_llm_prompt(description)
    assert f"Project Description: '{description}'" in prompt
    assert "'primary_tech_stack'" in prompt
    assert "'explanation'" in prompt

def test_local_recommendation_fallback(engine):
    """
    Tests the local recommendation logic to ensure it can generate a stack
    from the local dataset when external APIs fail.
    """
    # This test assumes 'tech_stacks.json' has data.
    description = "a simple web application"
    recommendation = engine._generate_local_recommendation(description, [], {})
    
    assert "primary_tech_stack" in recommendation
    assert "similar_projects" in recommendation
    assert isinstance(recommendation["primary_tech_stack"], list)
    if recommendation["primary_tech_stack"]:
        assert "name" in recommendation["primary_tech_stack"][0]
        assert "category" in recommendation["primary_tech_stack"][0]

@patch('requests.post')
@patch('app.services.recommendation_engine.GitHubCollector')
def test_generate_recommendation_success_path(MockGitHubCollector, mock_post, engine):
    """
    Tests the main generate_recommendation function's happy path,
    mocking external API calls.
    """
    # Mock GitHub response
    mock_github_instance = MockGitHubCollector.return_value
    mock_github_instance.search_projects.return_value = [
        {"name": "test-repo", "description": "A test repo", "metadata": {}}
    ]

    # Mock Perplexity LLM response
    mock_llm_response = MagicMock()
    mock_llm_response.json.return_value = {
        "choices": [{
            "message": {
                "content": '{"primary_tech_stack": [{"category": "frontend", "name": "React"}], "explanation": "It is good."}'
            }
        }]
    }
    mock_llm_response.raise_for_status.return_value = None
    mock_post.return_value = mock_llm_response

    # Call the function
    description = "a saas platform"
    recommendation = engine.generate_recommendation(description, [], {})

    # Assertions
    assert recommendation is not None
    assert "primary_tech_stack" in recommendation
    assert recommendation["primary_tech_stack"][0]["name"] == "React"
    assert "detailed_explanation" in recommendation
    assert recommendation["detailed_explanation"] == "It is good."
    assert "similar_projects" in recommendation
    assert recommendation["similar_projects"][0]["name"] == "test-repo"
    
    # Verify that the correct API was called
    mock_post.assert_called_once()
    assert "api.perplexity.ai" in mock_post.call_args[0][0]