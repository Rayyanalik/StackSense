from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Recommendation, RecommendationTechnology
from app.services.logging_service import LoggingService
import time

logger = LoggingService()

class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_recommendation(self, recommendation_data: Dict[str, Any]) -> Recommendation:
        """
        Create a new recommendation with its technologies.
        """
        try:
            start_time = time.time()
            
            # Create recommendation
            recommendation = Recommendation(
                project_description=recommendation_data['project_description'],
                requirements=recommendation_data['requirements'],
                constraints=recommendation_data.get('constraints', []),
                confidence_score=recommendation_data.get('confidence_score', 0.0),
                explanation=recommendation_data.get('explanation', ''),
                metadata=recommendation_data.get('metadata', {})
            )
            self.db.add(recommendation)
            self.db.flush()  # Get recommendation ID
            
            # Add technologies
            if 'technologies' in recommendation_data:
                for tech_data in recommendation_data['technologies']:
                    tech = RecommendationTechnology(
                        recommendation_id=recommendation.id,
                        name=tech_data['name'],
                        category=tech_data['category'],
                        confidence=tech_data.get('confidence', 0.0),
                        is_primary=tech_data.get('is_primary', False)
                    )
                    self.db.add(tech)
            
            self.db.commit()
            
            duration = (time.time() - start_time) * 1000
            logger.info(
                "Recommendation created successfully",
                extra_data={
                    'recommendation_id': recommendation.id,
                    'duration_ms': duration
                }
            )
            
            return recommendation
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Error creating recommendation",
                error=e,
                extra_data={'recommendation_data': recommendation_data}
            )
            raise
    
    def get_recommendation(self, recommendation_id: int) -> Optional[Recommendation]:
        """
        Get a recommendation by ID with its technologies.
        """
        try:
            return self.db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        except Exception as e:
            logger.error(
                "Error getting recommendation",
                error=e,
                extra_data={'recommendation_id': recommendation_id}
            )
            raise
    
    def get_recommendations(
        self,
        skip: int = 0,
        limit: int = 10,
        min_confidence: Optional[float] = None
    ) -> List[Recommendation]:
        """
        Get a list of recommendations with optional filtering.
        """
        try:
            query = self.db.query(Recommendation)
            
            if min_confidence is not None:
                query = query.filter(Recommendation.confidence_score >= min_confidence)
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(
                "Error getting recommendations",
                error=e,
                extra_data={
                    'skip': skip,
                    'limit': limit,
                    'min_confidence': min_confidence
                }
            )
            raise
    
    def get_recommendations_by_technologies(
        self,
        technologies: List[str],
        skip: int = 0,
        limit: int = 10
    ) -> List[Recommendation]:
        """
        Get recommendations that include specific technologies.
        """
        try:
            return (
                self.db.query(Recommendation)
                .join(Recommendation.technologies)
                .filter(RecommendationTechnology.name.in_(technologies))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(
                "Error getting recommendations by technologies",
                error=e,
                extra_data={
                    'technologies': technologies,
                    'skip': skip,
                    'limit': limit
                }
            )
            raise
    
    def update_recommendation(
        self,
        recommendation_id: int,
        recommendation_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """
        Update a recommendation's information.
        """
        try:
            recommendation = self.get_recommendation(recommendation_id)
            if not recommendation:
                return None
            
            # Update basic info
            for key, value in recommendation_data.items():
                if hasattr(recommendation, key):
                    setattr(recommendation, key, value)
            
            # Update technologies
            if 'technologies' in recommendation_data:
                # Remove existing technologies
                self.db.query(RecommendationTechnology).filter(
                    RecommendationTechnology.recommendation_id == recommendation_id
                ).delete()
                
                # Add new technologies
                for tech_data in recommendation_data['technologies']:
                    tech = RecommendationTechnology(
                        recommendation_id=recommendation.id,
                        name=tech_data['name'],
                        category=tech_data['category'],
                        confidence=tech_data.get('confidence', 0.0),
                        is_primary=tech_data.get('is_primary', False)
                    )
                    self.db.add(tech)
            
            self.db.commit()
            return recommendation
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Error updating recommendation",
                error=e,
                extra_data={
                    'recommendation_id': recommendation_id,
                    'recommendation_data': recommendation_data
                }
            )
            raise
    
    def delete_recommendation(self, recommendation_id: int) -> bool:
        """
        Delete a recommendation and its related data.
        """
        try:
            recommendation = self.get_recommendation(recommendation_id)
            if not recommendation:
                return False
            
            self.db.delete(recommendation)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Error deleting recommendation",
                error=e,
                extra_data={'recommendation_id': recommendation_id}
            )
            raise 