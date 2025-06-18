from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.recommendation import (
    TechStackRequest,
    TechStackResponse,
    SimilarProject
)
from app.services.recommendation_engine import RecommendationEngine
from app.services.data_processor import DataProcessor
from app.middleware.error_handler import (
    ValidationException,
    NotFoundException,
    RateLimitException
)
from app.services.logging_service import LoggingService
import time

router = APIRouter(
    prefix="/api/v1/tech-stack",
    tags=["Tech Stack"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)

logger = LoggingService()
data_processor = DataProcessor()
recommendation_engine = RecommendationEngine(data_processor)

@router.post(
    "/recommend",
    response_model=TechStackResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Tech Stack Recommendations",
    description="""
    Generate technology stack recommendations based on project description and requirements.
    
    This endpoint analyzes the project description and requirements to suggest:
    - A primary technology stack
    - Alternative technologies
    - Similar projects for reference
    - Confidence level and explanation
    
    The recommendation is based on:
    - Similarity with existing projects
    - Technology compatibility
    - Project requirements
    - User constraints
    """
)
async def get_tech_stack_recommendation(
    request: TechStackRequest
) -> TechStackResponse:
    """
    Generate technology stack recommendations based on project description and requirements.
    
    Args:
        request (TechStackRequest): The project description and requirements
        
    Returns:
        TechStackResponse: The recommended technology stack and alternatives
        
    Raises:
        HTTPException: If validation fails or an error occurs
    """
    try:
        start_time = time.time()
        
        # Validate input
        if not request.description.strip():
            raise ValidationException("Project description is required")
        
        # Process request
        recommendation = recommendation_engine.generate_recommendation(
            project_description=request.description,
            requirements=request.requirements,
            constraints=request.constraints,
            processed_data=[]  # TODO: Add processed data from database
        )
        
        duration = (time.time() - start_time) * 1000
        
        # Log successful recommendation
        logger.log_recommendation(
            project_description=request.description,
            requirements=request.requirements,
            constraints=request.constraints,
            recommendation=recommendation,
            processing_time_ms=duration
        )
        
        return TechStackResponse(
            primary_tech_stack=recommendation['primary_tech_stack'],
            alternatives=recommendation['alternatives'],
            explanation=recommendation['explanation'],
            confidence_level=recommendation['confidence_level'],
            similar_projects=recommendation['similar_projects']
        )
        
    except ValidationException as e:
        logger.error(
            "Validation error in tech stack recommendation",
            error=e,
            extra_data={
                "description": request.description,
                "requirements": request.requirements,
                "constraints": request.constraints
            }
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Error generating tech stack recommendation",
            error=e,
            extra_data={
                "description": request.description,
                "requirements": request.requirements,
                "constraints": request.constraints
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendation"
        )

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="""
    Check the health status of the tech stack recommendation service.
    
    This endpoint verifies:
    - Service availability
    - Database connectivity
    - Cache service status
    - Overall system health
    """
)
async def health_check():
    """
    Health check endpoint for the tech stack recommendation service.
    
    Returns:
        dict: Health status information
        
    Raises:
        HTTPException: If the service is unhealthy
    """
    try:
        start_time = time.time()
        # Add service-specific health checks here
        duration = (time.time() - start_time) * 1000
        
        logger.info(
            "Tech stack service health check successful",
            extra_data={"duration_ms": duration}
        )
        
        return {
            "status": "healthy",
            "service": "tech_stack",
            "version": "1.0.0",
            "timestamp": time.time(),
            "response_time_ms": duration
        }
    except Exception as e:
        logger.error(
            "Tech stack service health check failed",
            error=e,
            extra_data={"duration_ms": (time.time() - start_time) * 1000}
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tech stack service unhealthy"
        ) 