import pytest
from app.models.recommendation import ProjectDescription, TechStackRecommendation, SimilarProject
from pydantic import ValidationError

def test_project_description_valid():
    description = ProjectDescription(
        description="A web application with real-time features",
        requirements=["user authentication", "database storage"],
        constraints=["budget-friendly", "quick to deploy"]
    )
    
    assert description.description == "A web application with real-time features"
    assert len(description.requirements) == 2
    assert len(description.constraints) == 2

def test_project_description_empty():
    description = ProjectDescription(
        description="A web application with real-time features",
        requirements=[],
        constraints=[]
    )
    
    assert description.description == "A web application with real-time features"
    assert len(description.requirements) == 0
    assert len(description.constraints) == 0

def test_project_description_validation_error_short_description():
    with pytest.raises(ValidationError) as exc_info:
        ProjectDescription(
            description="test",
            requirements=[],
            constraints=[]
        )
    
    assert "description" in str(exc_info.value)

def test_project_description_validation_error_long_description():
    with pytest.raises(ValidationError) as exc_info:
        ProjectDescription(
            description="A" * 1001,
            requirements=[],
            constraints=[]
        )
    
    assert "description" in str(exc_info.value)

def test_project_description_validation_error_too_many_requirements():
    with pytest.raises(ValidationError) as exc_info:
        ProjectDescription(
            description="A web application",
            requirements=["req" + str(i) for i in range(11)],
            constraints=[]
        )
    
    assert "requirements" in str(exc_info.value)

def test_project_description_validation_error_too_many_constraints():
    with pytest.raises(ValidationError) as exc_info:
        ProjectDescription(
            description="A web application",
            requirements=[],
            constraints=["constraint" + str(i) for i in range(11)]
        )
    
    assert "constraints" in str(exc_info.value)

def test_similar_project_valid():
    project = SimilarProject(
        name="Test Project",
        description="A test project",
        technologies=["React", "Node.js"],
        metadata={"stars": 1000, "forks": 100}
    )
    
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert len(project.technologies) == 2
    assert project.metadata["stars"] == 1000
    assert project.metadata["forks"] == 100

def test_similar_project_empty_metadata():
    project = SimilarProject(
        name="Test Project",
        description="A test project",
        technologies=["React", "Node.js"]
    )
    
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert len(project.technologies) == 2
    assert project.metadata == {}

def test_tech_stack_recommendation_valid():
    recommendation = TechStackRecommendation(
        primary_stack=["React", "Node.js", "MongoDB"],
        alternatives=["Vue.js", "Express", "PostgreSQL"],
        explanation="This stack is recommended for web applications",
        confidence=0.85,
        similar_projects=[
            SimilarProject(
                name="Sample Project",
                description="A sample project",
                technologies=["React", "Node.js"],
                metadata={"stars": 1000}
            )
        ]
    )
    
    assert len(recommendation.primary_stack) == 3
    assert len(recommendation.alternatives) == 3
    assert recommendation.explanation == "This stack is recommended for web applications"
    assert recommendation.confidence == 0.85
    assert len(recommendation.similar_projects) == 1

def test_tech_stack_recommendation_validation_error_confidence():
    with pytest.raises(ValidationError) as exc_info:
        TechStackRecommendation(
            primary_stack=["React"],
            alternatives=["Vue.js"],
            explanation="Test explanation",
            confidence=1.5,  # Invalid confidence value
            similar_projects=[]
        )
    
    assert "confidence" in str(exc_info.value)

def test_tech_stack_recommendation_empty_similar_projects():
    recommendation = TechStackRecommendation(
        primary_stack=["React", "Node.js", "MongoDB"],
        alternatives=["Vue.js", "Express", "PostgreSQL"],
        explanation="This stack is recommended for web applications",
        confidence=0.85,
        similar_projects=[]
    )
    
    assert len(recommendation.primary_stack) == 3
    assert len(recommendation.alternatives) == 3
    assert recommendation.explanation == "This stack is recommended for web applications"
    assert recommendation.confidence == 0.85
    assert len(recommendation.similar_projects) == 0

def test_tech_stack_recommendation_schema_example():
    example = TechStackRecommendation.Config.schema_extra["example"]
    recommendation = TechStackRecommendation(**example)
    
    assert len(recommendation.primary_stack) == 3
    assert len(recommendation.alternatives) == 3
    assert recommendation.explanation == "This stack is recommended for web applications with real-time features"
    assert recommendation.confidence == 0.85
    assert len(recommendation.similar_projects) == 1
    assert recommendation.similar_projects[0].name == "Sample Project"
    assert recommendation.similar_projects[0].metadata["stars"] == 1000
    assert recommendation.similar_projects[0].metadata["forks"] == 100 