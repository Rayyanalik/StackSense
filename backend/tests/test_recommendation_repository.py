import pytest
from sqlalchemy.orm import Session
from app.repositories.recommendation_repository import RecommendationRepository
from app.database.models import Recommendation, RecommendationTechnology

@pytest.fixture
def db_session():
    # This fixture should be provided by your test configuration
    # It should create a test database session
    pass

@pytest.fixture
def recommendation_repository(db_session: Session):
    return RecommendationRepository(db_session)

@pytest.fixture
def sample_recommendation_data():
    return {
        'project_description': 'A web application for project management',
        'requirements': ['User authentication', 'Task management', 'Real-time updates'],
        'constraints': ['Must use Python', 'Must be scalable'],
        'confidence_score': 0.85,
        'explanation': 'Based on similar successful projects',
        'metadata': {'source': 'github', 'analysis_time': '2024-03-20'},
        'technologies': [
            {
                'name': 'Django',
                'category': 'backend',
                'confidence': 0.9,
                'is_primary': True
            },
            {
                'name': 'React',
                'category': 'frontend',
                'confidence': 0.85,
                'is_primary': True
            },
            {
                'name': 'PostgreSQL',
                'category': 'database',
                'confidence': 0.8,
                'is_primary': True
            }
        ]
    }

def test_create_recommendation(recommendation_repository, sample_recommendation_data):
    recommendation = recommendation_repository.create_recommendation(sample_recommendation_data)
    
    assert recommendation is not None
    assert recommendation.project_description == sample_recommendation_data['project_description']
    assert recommendation.requirements == sample_recommendation_data['requirements']
    assert recommendation.constraints == sample_recommendation_data['constraints']
    assert recommendation.confidence_score == sample_recommendation_data['confidence_score']
    assert recommendation.explanation == sample_recommendation_data['explanation']
    assert recommendation.metadata == sample_recommendation_data['metadata']
    
    # Check technologies
    assert len(recommendation.technologies) == len(sample_recommendation_data['technologies'])
    for tech in recommendation.technologies:
        matching_tech = next(
            t for t in sample_recommendation_data['technologies']
            if t['name'] == tech.name
        )
        assert tech.category == matching_tech['category']
        assert tech.confidence == matching_tech['confidence']
        assert tech.is_primary == matching_tech['is_primary']

def test_get_recommendation(recommendation_repository, sample_recommendation_data):
    created = recommendation_repository.create_recommendation(sample_recommendation_data)
    retrieved = recommendation_repository.get_recommendation(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.project_description == created.project_description
    assert len(retrieved.technologies) == len(created.technologies)

def test_get_recommendations(recommendation_repository, sample_recommendation_data):
    # Create multiple recommendations
    for i in range(3):
        data = sample_recommendation_data.copy()
        data['project_description'] = f"Project {i}"
        recommendation_repository.create_recommendation(data)
    
    # Test pagination
    recommendations = recommendation_repository.get_recommendations(skip=0, limit=2)
    assert len(recommendations) == 2
    
    # Test with min_confidence
    recommendations = recommendation_repository.get_recommendations(min_confidence=0.9)
    assert all(r.confidence_score >= 0.9 for r in recommendations)

def test_get_recommendations_by_technologies(recommendation_repository, sample_recommendation_data):
    recommendation_repository.create_recommendation(sample_recommendation_data)
    
    recommendations = recommendation_repository.get_recommendations_by_technologies(
        technologies=['Django', 'React']
    )
    assert len(recommendations) > 0
    assert all(
        any(tech.name in ['Django', 'React'] for tech in r.technologies)
        for r in recommendations
    )

def test_update_recommendation(recommendation_repository, sample_recommendation_data):
    created = recommendation_repository.create_recommendation(sample_recommendation_data)
    
    update_data = {
        'confidence_score': 0.95,
        'explanation': 'Updated explanation',
        'technologies': [
            {
                'name': 'FastAPI',
                'category': 'backend',
                'confidence': 0.95,
                'is_primary': True
            }
        ]
    }
    
    updated = recommendation_repository.update_recommendation(created.id, update_data)
    assert updated is not None
    assert updated.confidence_score == update_data['confidence_score']
    assert updated.explanation == update_data['explanation']
    assert len(updated.technologies) == 1
    assert updated.technologies[0].name == 'FastAPI'

def test_delete_recommendation(recommendation_repository, sample_recommendation_data):
    created = recommendation_repository.create_recommendation(sample_recommendation_data)
    
    # Delete the recommendation
    success = recommendation_repository.delete_recommendation(created.id)
    assert success is True
    
    # Verify it's deleted
    deleted = recommendation_repository.get_recommendation(created.id)
    assert deleted is None

def test_error_handling(recommendation_repository):
    # Test with invalid data
    with pytest.raises(Exception):
        recommendation_repository.create_recommendation({})
    
    # Test with non-existent ID
    assert recommendation_repository.get_recommendation(999) is None
    
    # Test update with non-existent ID
    assert recommendation_repository.update_recommendation(999, {}) is None
    
    # Test delete with non-existent ID
    assert recommendation_repository.delete_recommendation(999) is False 