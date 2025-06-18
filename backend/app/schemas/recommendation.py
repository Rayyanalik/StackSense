from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class TechnologyCategory(str, Enum):
    """Categories of technologies in a tech stack."""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    DEVOPS = "devops"

class Technology(BaseModel):
    """Represents a technology in the tech stack."""
    name: str = Field(..., description="Name of the technology")
    category: TechnologyCategory = Field(..., description="Category of the technology")
    version: Optional[str] = Field(None, description="Version of the technology if specified")
    description: Optional[str] = Field(None, description="Brief description of the technology")

    class Config:
        schema_extra = {
            "example": {
                "name": "React",
                "category": "frontend",
                "version": "18.2.0",
                "description": "A JavaScript library for building user interfaces"
            }
        }

class TechStackRequest(BaseModel):
    """Request model for tech stack recommendations."""
    description: str = Field(
        ...,
        description="Detailed description of the project",
        min_length=10,
        max_length=2000
    )
    requirements: List[str] = Field(
        default_factory=list,
        description="List of specific requirements or constraints for the project"
    )
    constraints: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Dictionary of constraints by category (e.g., {'frontend': ['React', 'Vue']})"
    )

    class Config:
        schema_extra = {
            "example": {
                "description": "A real-time chat application with user authentication and message history",
                "requirements": [
                    "Real-time updates",
                    "User authentication",
                    "Message persistence",
                    "Mobile responsive design"
                ],
                "constraints": {
                    "frontend": ["React"],
                    "backend": ["Node.js"]
                }
            }
        }

class SimilarProject(BaseModel):
    """Represents a similar project used for recommendation."""
    name: str = Field(..., description="Name of the similar project")
    description: str = Field(..., description="Description of the similar project")
    tech_stack: List[Technology] = Field(..., description="Technology stack used in the project")
    similarity_score: float = Field(..., description="Similarity score with the requested project")

    class Config:
        schema_extra = {
            "example": {
                "name": "ChatApp",
                "description": "A real-time chat application with user authentication",
                "tech_stack": [
                    {
                        "name": "React",
                        "category": "frontend",
                        "version": "18.2.0"
                    },
                    {
                        "name": "Node.js",
                        "category": "backend",
                        "version": "18.0.0"
                    }
                ],
                "similarity_score": 0.85
            }
        }

class TechStackResponse(BaseModel):
    """Response model for tech stack recommendations."""
    primary_tech_stack: List[Technology] = Field(
        ...,
        description="Primary recommended technology stack"
    )
    alternatives: Dict[str, List[Technology]] = Field(
        ...,
        description="Alternative technologies by category"
    )
    explanation: str = Field(
        ...,
        description="Detailed explanation of the recommendation"
    )
    confidence_level: float = Field(
        ...,
        description="Confidence level of the recommendation (0-1)",
        ge=0,
        le=1
    )
    similar_projects: List[SimilarProject] = Field(
        ...,
        description="List of similar projects used for the recommendation"
    )

    class Config:
        schema_extra = {
            "example": {
                "primary_tech_stack": [
                    {
                        "name": "React",
                        "category": "frontend",
                        "version": "18.2.0"
                    },
                    {
                        "name": "Node.js",
                        "category": "backend",
                        "version": "18.0.0"
                    }
                ],
                "alternatives": {
                    "frontend": [
                        {
                            "name": "Vue.js",
                            "category": "frontend",
                            "version": "3.2.0"
                        }
                    ]
                },
                "explanation": "Based on similar projects and requirements, React and Node.js are recommended for their strong ecosystem and real-time capabilities.",
                "confidence_level": 0.85,
                "similar_projects": [
                    {
                        "name": "ChatApp",
                        "description": "A real-time chat application",
                        "tech_stack": [
                            {
                                "name": "React",
                                "category": "frontend",
                                "version": "18.2.0"
                            }
                        ],
                        "similarity_score": 0.85
                    }
                ]
            }
        } 