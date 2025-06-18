from fastapi import APIRouter, HTTPException, Depends, status
from app.models.recommendation import ProjectDescription, TechStackRecommendation
from app.services.recommendation import RecommendationService
from app.services.cache_service import CacheService
from app.database.base import get_db
from sqlalchemy.orm import Session
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/recommend", response_model=TechStackRecommendation)
async def get_recommendation(
    project: ProjectDescription,
    db: Session = Depends(get_db),
    cache: CacheService = Depends(CacheService)
):
    """
    Get tech stack recommendations based on project description.
    
    Args:
        project: Project description including requirements and constraints
        db: Database session
        cache: Cache service
        
    Returns:
        TechStackRecommendation: Recommended tech stack with alternatives and explanation
        
    Raises:
        HTTPException: If recommendation service fails
    """
    try:
        service = RecommendationService(db=db, cache=cache)
        recommendation = await service.get_recommendation(project)
        return recommendation
    except Exception as e:
        logger.error(f"Error getting recommendation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendation: {str(e)}"
        )

@router.get("/technologies", response_model=list[str])
async def get_technologies(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(CacheService)
):
    """
    Get list of all available technologies in the system.
    
    Returns:
        List[str]: List of technology names
        
    Raises:
        HTTPException: If service fails to fetch technologies
    """
    try:
        service = RecommendationService(db=db, cache=cache)
        technologies = await service.get_available_technologies()
        return technologies
    except Exception as e:
        logger.error(f"Error getting technologies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get technologies: {str(e)}"
        ) 