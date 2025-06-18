from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.cache_service import CacheService
from app.services.data_processor import DataProcessor
from app.services.recommendation_engine import RecommendationEngine
from app.models.recommendation import ProjectDescription, TechStackRecommendation, SimilarProject
from app.data.collection.github_collector import GitHubCollector
from app.data.collection.stackoverflow_collector import StackOverflowCollector
from app.services.logging_service import LoggingService
from app.database.base import get_db
from fastapi import Depends
import hashlib
import json
import logging

logger = LoggingService()

class RecommendationService:
    def __init__(self, db: Session = Depends(get_db), cache: CacheService = Depends(CacheService)):
        """Initialize the recommendation service with collectors and cache."""
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.cache = cache
        self.data_processor = DataProcessor()
        self.engine = RecommendationEngine(self.data_processor)
        self.github_collector = GitHubCollector()
        self.stackoverflow_collector = StackOverflowCollector()
    
    def _generate_cache_key(self, description: ProjectDescription) -> str:
        # Use a hash of the description and requirements/constraints for the cache key
        key_data = {
            'description': description.description,
            'requirements': description.requirements,
            'constraints': description.constraints
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"recommendation:{hashlib.md5(key_str.encode()).hexdigest()}"

    async def get_recommendation(self, description: ProjectDescription) -> TechStackRecommendation:
        cache_key = self._generate_cache_key(description)
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("Cache hit for recommendation", extra_data={'cache_key': cache_key})
            return TechStackRecommendation(**cached)

        logger.info("Cache miss for recommendation", extra_data={'cache_key': cache_key})
        # Collect and process data (mocked for now)
        processed_data = self.data_processor.process_github_data([])  # Replace with real data
        recommendation = self.engine.generate_recommendation(
            description.description,
            description.requirements,
            description.constraints,
            processed_data
        )
        # Save to DB
        self.recommendation_repo.create_recommendation({
            'project_description': description.description,
            'requirements': description.requirements,
            'constraints': description.constraints,
            'confidence_score': recommendation.confidence_level,
            'explanation': recommendation.explanation,
            'metadata': {},
            'technologies': [
                {'name': t, 'category': 'unknown', 'confidence': recommendation.confidence_level, 'is_primary': True}
                for t in recommendation.primary_tech_stack
            ]
        })
        # Cache the result
        self.cache.set(cache_key, recommendation.dict())
        return recommendation
    
    async def get_available_technologies(self) -> List[str]:
        """
        Get a list of all available technologies.
        
        Returns:
            List of technology names
        """
        try:
            # Get all technologies from processed data
            all_technologies = set()
            
            # Collect sample data
            sample_description = "web application"
            github_data = await self.github_collector.collect_data(sample_description)
            stackoverflow_data = await self.stackoverflow_collector.collect_data(sample_description)
            
            # Process data and extract technologies
            processed_data = self.data_processor.process_data(github_data + stackoverflow_data)
            for item in processed_data:
                all_technologies.update(item.get('technologies', []))
            
            return sorted(list(all_technologies))
            
        except Exception as e:
            logger.error(f"Error getting available technologies: {str(e)}")
            return []
    
    def _generate_recommendation(self, processed_data: List[Dict[str, Any]], project_description: ProjectDescription) -> TechStackRecommendation:
        """
        Generate a tech stack recommendation based on processed data.
        
        Args:
            processed_data: Processed data from collectors
            project_description: Project description and requirements
            
        Returns:
            Tech stack recommendation
        """
        # TODO: Implement actual recommendation logic
        # For now, return a mock recommendation
        return TechStackRecommendation(
            primary_tech_stack=['React', 'Node.js', 'MongoDB'],
            alternatives=['Vue.js', 'Express', 'PostgreSQL'],
            explanation='Based on your requirements, we recommend...',
            confidence_level=0.85,
            similar_projects=[
                SimilarProject(
                    name='Project 1',
                    description='A similar project',
                    technologies=['React', 'Node.js'],
                    metadata={'stars': 1000}
                )
            ]
        ) 