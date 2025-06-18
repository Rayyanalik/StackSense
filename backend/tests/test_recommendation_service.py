import pytest
from app.services.recommendation import RecommendationService
from app.models.recommendation import ProjectDescription, TechStackRecommendation
from unittest.mock import Mock, patch
import asyncio

@pytest.fixture
def mock_collectors():
    with patch('app.services.recommendation.GitHubCollector') as mock_github, \
         patch('app.services.recommendation.StackOverflowCollector') as mock_stackoverflow:
        
        # Mock GitHub collector
        mock_github_instance = Mock()
        mock_github_instance.collect_data.return_value = [
            {
                'name': 'Test Project',
                'description': 'A test project',
                'technologies': ['React', 'Node.js'],
                'metadata': {'stars': 100}
            }
        ]
        mock_github.return_value = mock_github_instance
        
        # Mock Stack Overflow collector
        mock_stackoverflow_instance = Mock()
        mock_stackoverflow_instance.collect_data.return_value = [
            {
                'name': 'Test Question',
                'description': 'A test question',
                'technologies': ['Python', 'Django'],
                'metadata': {'votes': 50}
            }
        ]
        mock_stackoverflow.return_value = mock_stackoverflow_instance
        
        yield mock_github_instance, mock_stackoverflow_instance

@pytest.fixture
def mock_data_processor():
    with patch('app.services.recommendation.DataProcessor') as mock_processor:
        mock_processor_instance = Mock()
        mock_processor_instance.process_data.return_value = [
            {
                'name': 'Processed Project',
                'description': 'A processed project',
                'technologies': ['React', 'Node.js', 'MongoDB'],
                'metadata': {'processed': True}
            }
        ]
        mock_processor.return_value = mock_processor_instance
        yield mock_processor_instance

@pytest.mark.asyncio
async def test_get_recommendation_success(mock_collectors, mock_data_processor):
    service = RecommendationService()
    description = ProjectDescription(
        description="A web application with real-time features",
        requirements=["user authentication", "database storage"],
        constraints=["budget-friendly", "quick to deploy"]
    )
    
    recommendation = await service.get_recommendation(description)
    
    assert isinstance(recommendation, TechStackRecommendation)
    assert recommendation.primary_stack == ["React", "Node.js", "MongoDB"]
    assert recommendation.alternatives == ["Vue.js", "Express", "PostgreSQL"]
    assert recommendation.confidence == 0.85
    assert len(recommendation.similar_projects) == 1

@pytest.mark.asyncio
async def test_get_recommendation_collector_error(mock_collectors, mock_data_processor):
    mock_github, _ = mock_collectors
    mock_github.collect_data.side_effect = Exception("GitHub API error")
    
    service = RecommendationService()
    description = ProjectDescription(
        description="A web application",
        requirements=[],
        constraints=[]
    )
    
    with pytest.raises(Exception) as exc_info:
        await service.get_recommendation(description)
    
    assert "GitHub API error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_recommendation_processor_error(mock_collectors, mock_data_processor):
    mock_data_processor.process_data.side_effect = Exception("Processing error")
    
    service = RecommendationService()
    description = ProjectDescription(
        description="A web application",
        requirements=[],
        constraints=[]
    )
    
    with pytest.raises(Exception) as exc_info:
        await service.get_recommendation(description)
    
    assert "Processing error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_available_technologies(mock_collectors, mock_data_processor):
    service = RecommendationService()
    technologies = await service.get_available_technologies()
    
    assert isinstance(technologies, list)
    assert len(technologies) > 0
    assert all(isinstance(tech, str) for tech in technologies)

@pytest.mark.asyncio
async def test_get_available_technologies_empty_data(mock_collectors, mock_data_processor):
    mock_data_processor.process_data.return_value = []
    
    service = RecommendationService()
    technologies = await service.get_available_technologies()
    
    assert isinstance(technologies, list)
    assert len(technologies) == 0

@pytest.mark.asyncio
async def test_get_available_technologies_error(mock_collectors, mock_data_processor):
    mock_data_processor.process_data.side_effect = Exception("Processing error")
    
    service = RecommendationService()
    
    with pytest.raises(Exception) as exc_info:
        await service.get_available_technologies()
    
    assert "Processing error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_generate_recommendation_with_requirements(mock_collectors, mock_data_processor):
    service = RecommendationService()
    description = ProjectDescription(
        description="A web application with real-time features",
        requirements=["user authentication", "database storage"],
        constraints=["budget-friendly", "quick to deploy"]
    )
    processed_data = [
        {
            'name': 'Test Project',
            'description': 'A test project',
            'technologies': ['React', 'Node.js', 'MongoDB'],
            'metadata': {'stars': 100}
        }
    ]
    
    recommendation = await service._generate_recommendation(description, processed_data)
    
    assert isinstance(recommendation, TechStackRecommendation)
    assert recommendation.primary_stack == ["React", "Node.js", "MongoDB"]
    assert recommendation.alternatives == ["Vue.js", "Express", "PostgreSQL"]
    assert recommendation.confidence == 0.85
    assert len(recommendation.similar_projects) == 1
    assert recommendation.similar_projects[0].name == "Sample Project" 