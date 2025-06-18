from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from ..services.recommendation_service import RecommendationService
from ..services.health_service import HealthService

router = APIRouter()

class ProjectDescription(BaseModel):
    description: str
    requirements: List[str] = []
    constraints: Dict[str, Any] = {}

class TechStackRecommendation(BaseModel):
    primary_stack: List[str]
    alternatives: List[str]
    explanation: str
    confidence: float
    similar_projects: List[Dict[str, Any]]

@router.post("/recommend", response_model=TechStackRecommendation)
async def get_recommendation(project: ProjectDescription):
    """Get tech stack recommendations based on project description."""
    try:
        service = RecommendationService()
        recommendation = await service.get_recommendation(
            project.description,
            project.requirements,
            project.constraints
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Check the health of the API and its dependencies."""
    try:
        service = HealthService()
        health_status = await service.check_health()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 