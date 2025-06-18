from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProjectDescription(BaseModel):
    description: str = Field(..., min_length=10, max_length=1000)
    requirements: List[str] = Field(default_factory=list, max_items=10)
    constraints: List[str] = Field(default_factory=list, max_items=10)

class SimilarProject(BaseModel):
    name: str
    description: str
    technologies: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TechStackRecommendation(BaseModel):
    primary_stack: List[str]
    alternatives: List[str]
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    similar_projects: List[SimilarProject] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "example": {
                "primary_stack": ["React", "Node.js", "MongoDB"],
                "alternatives": ["Vue.js", "Express", "PostgreSQL"],
                "explanation": "This stack is recommended for web applications with real-time features",
                "confidence": 0.85,
                "similar_projects": [
                    {
                        "name": "Sample Project",
                        "description": "A web application with real-time updates",
                        "technologies": ["React", "Node.js"],
                        "metadata": {
                            "stars": 1000,
                            "forks": 100
                        }
                    }
                ]
            }
        } 