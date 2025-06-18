import pytest
from app.services.data_processor import DataProcessor
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    return [
        {
            'name': 'Project 1',
            'description': 'A web application with React and Node.js',
            'technologies': ['React', 'Node.js', 'MongoDB'],
            'metadata': {'stars': 1000, 'forks': 100}
        },
        {
            'name': 'Project 2',
            'description': 'A mobile app using React Native',
            'technologies': ['React Native', 'Firebase'],
            'metadata': {'stars': 500, 'forks': 50}
        }
    ]

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_github_data():
    return [
        {
            'name': 'test-repo',
            'description': 'A React and Node.js project with MongoDB',
            'stargazers_count': 100,
            'forks_count': 50,
            'updated_at': '2024-03-20T10:00:00Z',
            'language': 'JavaScript',
            'topics': ['react', 'nodejs', 'mongodb']
        },
        {
            'name': 'django-app',
            'description': 'Django REST API with PostgreSQL',
            'stargazers_count': 200,
            'forks_count': 75,
            'updated_at': '2024-03-19T15:30:00Z',
            'language': 'Python',
            'topics': ['django', 'postgresql', 'api']
        }
    ]

@pytest.fixture
def sample_stackoverflow_data():
    return [
        {
            'title': 'How to use React with TypeScript?',
            'body': 'I am building a React application and want to use TypeScript...',
            'score': 10,
            'view_count': 1000,
            'answer_count': 5,
            'tags': ['react', 'typescript', 'javascript'],
            'creation_date': '2024-03-20T08:00:00Z'
        },
        {
            'title': 'Django vs Flask for REST API',
            'body': 'Which framework is better for building REST APIs...',
            'score': 15,
            'view_count': 2000,
            'answer_count': 8,
            'tags': ['django', 'flask', 'python', 'api'],
            'creation_date': '2024-03-19T12:00:00Z'
        }
    ]

def test_process_data_valid(data_processor, sample_data):
    processed_data = data_processor.process_data(sample_data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 2
    
    # Check first item
    assert processed_data[0]['name'] == 'Project 1'
    assert processed_data[0]['description'] == 'A web application with React and Node.js'
    assert set(processed_data[0]['technologies']) == {'React', 'Node.js', 'MongoDB'}
    assert processed_data[0]['metadata']['stars'] == 1000
    assert processed_data[0]['metadata']['forks'] == 100
    
    # Check second item
    assert processed_data[1]['name'] == 'Project 2'
    assert processed_data[1]['description'] == 'A mobile app using React Native'
    assert set(processed_data[1]['technologies']) == {'React Native', 'Firebase'}
    assert processed_data[1]['metadata']['stars'] == 500
    assert processed_data[1]['metadata']['forks'] == 50

def test_process_data_empty(data_processor):
    processed_data = data_processor.process_data([])
    assert isinstance(processed_data, list)
    assert len(processed_data) == 0

def test_process_data_missing_fields(data_processor):
    data = [
        {
            'name': 'Project 1',
            'description': 'A web application'
        },
        {
            'name': 'Project 2',
            'technologies': ['React']
        }
    ]
    
    processed_data = data_processor.process_data(data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 2
    
    # Check first item
    assert processed_data[0]['name'] == 'Project 1'
    assert processed_data[0]['description'] == 'A web application'
    assert 'technologies' in processed_data[0]
    assert isinstance(processed_data[0]['technologies'], list)
    assert len(processed_data[0]['technologies']) == 0
    assert 'metadata' in processed_data[0]
    assert isinstance(processed_data[0]['metadata'], dict)
    
    # Check second item
    assert processed_data[1]['name'] == 'Project 2'
    assert 'description' in processed_data[1]
    assert processed_data[1]['description'] == ''
    assert processed_data[1]['technologies'] == ['React']
    assert 'metadata' in processed_data[1]
    assert isinstance(processed_data[1]['metadata'], dict)

def test_process_data_invalid_technology_format(data_processor):
    data = [
        {
            'name': 'Project 1',
            'description': 'A web application',
            'technologies': 'React, Node.js',  # Should be a list
            'metadata': {}
        }
    ]
    
    processed_data = data_processor.process_data(data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 1
    assert isinstance(processed_data[0]['technologies'], list)
    assert len(processed_data[0]['technologies']) == 0

def test_process_data_long_strings(data_processor):
    long_description = 'A' * 1000
    data = [
        {
            'name': 'Project 1',
            'description': long_description,
            'technologies': ['React'],
            'metadata': {}
        }
    ]
    
    processed_data = data_processor.process_data(data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 1
    assert processed_data[0]['description'] == long_description

def test_process_data_special_characters(data_processor):
    data = [
        {
            'name': 'Project 1',
            'description': 'A web app with <script>alert("xss")</script>',
            'technologies': ['React'],
            'metadata': {}
        }
    ]
    
    processed_data = data_processor.process_data(data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 1
    assert '<script>' not in processed_data[0]['description']

def test_process_data_duplicate_technologies(data_processor):
    data = [
        {
            'name': 'Project 1',
            'description': 'A web application',
            'technologies': ['React', 'React', 'Node.js', 'Node.js'],
            'metadata': {}
        }
    ]
    
    processed_data = data_processor.process_data(data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 1
    assert len(processed_data[0]['technologies']) == 2
    assert set(processed_data[0]['technologies']) == {'React', 'Node.js'}

def test_process_data_case_sensitive_technologies(data_processor):
    data = [
        {
            'name': 'Project 1',
            'description': 'A web application',
            'technologies': ['react', 'React', 'REACT'],
            'metadata': {}
        }
    ]
    
    processed_data = data_processor.process_data(data)
    
    assert isinstance(processed_data, list)
    assert len(processed_data) == 1
    assert len(processed_data[0]['technologies']) == 1
    assert processed_data[0]['technologies'][0] == 'React'

def test_process_data_error_handling(data_processor):
    # Test with invalid data type
    with pytest.raises(TypeError):
        data_processor.process_data("invalid data")
    
    # Test with None
    with pytest.raises(TypeError):
        data_processor.process_data(None)
    
    # Test with invalid item type
    with pytest.raises(TypeError):
        data_processor.process_data([1, 2, 3])

def test_process_github_data(data_processor, sample_github_data):
    processed_data = data_processor.process_github_data(sample_github_data)
    
    assert len(processed_data) == 2
    assert processed_data[0]['name'] == 'test-repo'
    assert 'react' in processed_data[0]['technologies']
    assert 'node.js' in processed_data[0]['technologies']
    assert 'mongodb' in processed_data[0]['technologies']
    assert processed_data[0]['metadata']['stars'] == 100
    assert processed_data[0]['metadata']['forks'] == 50

def test_process_stackoverflow_data(data_processor, sample_stackoverflow_data):
    processed_data = data_processor.process_stackoverflow_data(sample_stackoverflow_data)
    
    assert len(processed_data) == 2
    assert 'react' in processed_data[0]['technologies']
    assert 'typescript' in processed_data[0]['technologies']
    assert processed_data[0]['metadata']['score'] == 10
    assert processed_data[0]['metadata']['view_count'] == 1000

def test_extract_technologies(data_processor):
    data = {
        'description': 'Building a React app with TypeScript and Tailwind CSS',
        'body': 'Using Node.js and Express for the backend',
        'title': 'Full Stack Development',
        'topics': ['web-development', 'javascript'],
        'tags': ['react', 'typescript']
    }
    
    technologies = data_processor._extract_technologies(data)
    assert 'react' in technologies
    assert 'typescript' in technologies
    assert 'tailwind' in technologies
    assert 'node.js' in technologies
    assert 'express' in technologies

def test_normalize_text(data_processor):
    text = "  Hello, World!  This is a test...  "
    normalized = data_processor.normalize_text(text)
    assert normalized == "hello world this is a test"

def test_calculate_similarity_score(data_processor):
    text1 = "React application with TypeScript"
    text2 = "TypeScript and React project"
    score = data_processor.calculate_similarity_score(text1, text2)
    assert 0 < score < 1

def test_get_technology_frequency(data_processor, sample_github_data, sample_stackoverflow_data):
    github_processed = data_processor.process_github_data(sample_github_data)
    stackoverflow_processed = data_processor.process_stackoverflow_data(sample_stackoverflow_data)
    all_data = github_processed + stackoverflow_processed
    
    frequency = data_processor.get_technology_frequency(all_data)
    assert frequency['react'] > 0
    assert frequency['django'] > 0
    assert frequency['typescript'] > 0

def test_filter_by_technologies(data_processor, sample_github_data, sample_stackoverflow_data):
    github_processed = data_processor.process_github_data(sample_github_data)
    stackoverflow_processed = data_processor.process_stackoverflow_data(sample_stackoverflow_data)
    all_data = github_processed + stackoverflow_processed
    
    filtered = data_processor.filter_by_technologies(all_data, ['react', 'typescript'])
    assert len(filtered) > 0
    assert all(
        any(tech in ['react', 'typescript'] for tech in item['technologies'])
        for item in filtered
    )

def test_error_handling(data_processor):
    # Test with invalid data
    with pytest.raises(Exception):
        data_processor.process_github_data([{'invalid': 'data'}])
    
    # Test with empty data
    assert data_processor.process_github_data([]) == []
    assert data_processor.process_stackoverflow_data([]) == []
    
    # Test with None
    assert data_processor.normalize_text(None) == ""
    assert data_processor.calculate_similarity_score(None, "test") == 0.0
    assert data_processor.get_technology_frequency([]) == {}
    assert data_processor.filter_by_technologies([], ['test']) == [] 