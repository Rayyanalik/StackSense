import pytest
from app.services.recommendation_engine import RecommendationEngine
from app.services.data_processor import DataProcessor

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def recommendation_engine(data_processor):
    return RecommendationEngine(data_processor)

@pytest.fixture
def sample_processed_data():
    return [
        {
            'name': 'react-node-app',
            'description': 'A React and Node.js application with MongoDB',
            'technologies': ['react', 'node.js', 'express', 'mongodb', 'typescript'],
            'metadata': {
                'stars': 100,
                'forks': 50
            }
        },
        {
            'name': 'django-postgres-app',
            'description': 'Django application with PostgreSQL and Redis',
            'technologies': ['django', 'postgresql', 'redis', 'python'],
            'metadata': {
                'stars': 200,
                'forks': 75
            }
        },
        {
            'name': 'vue-spring-app',
            'description': 'Vue.js frontend with Spring Boot backend',
            'technologies': ['vue', 'spring', 'java', 'mysql'],
            'metadata': {
                'stars': 150,
                'forks': 60
            }
        }
    ]

def test_generate_recommendation(recommendation_engine, sample_processed_data):
    project_description = "I need a modern web application with real-time features"
    requirements = ["Scalable", "Real-time updates", "User authentication"]
    constraints = ["No PHP", "Must be open source"]
    
    recommendation = recommendation_engine.generate_recommendation(
        project_description,
        requirements,
        constraints,
        sample_processed_data
    )
    
    assert 'primary_tech_stack' in recommendation
    assert 'alternatives' in recommendation
    assert 'explanation' in recommendation
    assert 'confidence_level' in recommendation
    assert 'similar_projects' in recommendation
    
    assert isinstance(recommendation['primary_tech_stack'], list)
    assert isinstance(recommendation['alternatives'], list)
    assert isinstance(recommendation['explanation'], str)
    assert isinstance(recommendation['confidence_level'], float)
    assert isinstance(recommendation['similar_projects'], list)
    
    assert 0 <= recommendation['confidence_level'] <= 1
    assert len(recommendation['similar_projects']) <= 5

def test_find_similar_projects(recommendation_engine, sample_processed_data):
    description = "React application with Node.js backend"
    requirements = ["Real-time", "Scalable"]
    
    similar_projects = recommendation_engine._find_similar_projects(
        description,
        requirements,
        sample_processed_data
    )
    
    assert len(similar_projects) == len(sample_processed_data)
    assert similar_projects[0]['name'] == 'react-node-app'  # Should be most similar

def test_generate_primary_stack(recommendation_engine):
    tech_frequency = {
        'react': 10,
        'node.js': 8,
        'express': 7,
        'mongodb': 6,
        'django': 5,
        'postgresql': 4
    }
    constraints = ["No PHP"]
    
    primary_stack = recommendation_engine._generate_primary_stack(tech_frequency, constraints)
    
    assert len(primary_stack) > 0
    assert all(tech in tech_frequency for tech in primary_stack)
    assert not any("php" in tech.lower() for tech in primary_stack)

def test_generate_alternatives(recommendation_engine):
    tech_frequency = {
        'react': 10,
        'node.js': 8,
        'express': 7,
        'mongodb': 6,
        'django': 5,
        'postgresql': 4
    }
    primary_stack = ['react', 'node.js']
    constraints = ["No PHP"]
    
    alternatives = recommendation_engine._generate_alternatives(
        tech_frequency,
        primary_stack,
        constraints
    )
    
    assert len(alternatives) <= 5
    assert not any(tech in primary_stack for tech in alternatives)
    assert not any("php" in tech.lower() for tech in alternatives)

def test_calculate_confidence(recommendation_engine, sample_processed_data):
    tech_frequency = {
        'react': 10,
        'node.js': 8,
        'express': 7
    }
    
    confidence = recommendation_engine._calculate_confidence(sample_processed_data, tech_frequency)
    
    assert 0 <= confidence <= 1

def test_generate_explanation(recommendation_engine):
    primary_stack = ['react', 'node.js', 'mongodb']
    alternatives = ['vue', 'express', 'postgresql']
    similar_projects = [{'name': 'test-project'}]
    confidence = 0.8
    
    explanation = recommendation_engine._generate_explanation(
        primary_stack,
        alternatives,
        similar_projects,
        confidence
    )
    
    assert isinstance(explanation, str)
    assert len(explanation) > 0
    assert all(tech in explanation.lower() for tech in primary_stack)

def test_error_handling(recommendation_engine):
    # Test with empty data
    empty_recommendation = recommendation_engine.generate_recommendation(
        "test",
        [],
        [],
        []
    )
    assert empty_recommendation['confidence_level'] == 0
    assert len(empty_recommendation['primary_tech_stack']) == 0
    assert len(empty_recommendation['alternatives']) == 0
    
    # Test with invalid data
    with pytest.raises(Exception):
        recommendation_engine.generate_recommendation(
            "test",
            [],
            [],
            [{'invalid': 'data'}]
        )

def test_constraints_handling(recommendation_engine, sample_processed_data):
    # Test with strict constraints
    strict_constraints = ["No JavaScript", "No Python"]
    recommendation = recommendation_engine.generate_recommendation(
        "test project",
        [],
        strict_constraints,
        sample_processed_data
    )
    
    assert not any("javascript" in tech.lower() for tech in recommendation['primary_tech_stack'])
    assert not any("python" in tech.lower() for tech in recommendation['primary_tech_stack'])
    
    # Test with no constraints
    no_constraints = []
    recommendation = recommendation_engine.generate_recommendation(
        "test project",
        [],
        no_constraints,
        sample_processed_data
    )
    
    assert len(recommendation['primary_tech_stack']) > 0 