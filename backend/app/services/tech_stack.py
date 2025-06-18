from typing import List, Dict, Any
import json
import logging
from pathlib import Path
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class TechStackService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.tech_stacks = self._load_tech_stacks()
        self.tech_stack_embeddings = self._generate_embeddings()

    def _load_tech_stacks(self) -> List[Dict[str, Any]]:
        """
        Load tech stack data from JSON file
        """
        try:
            data_path = Path(__file__).parent.parent / "data" / "tech_stacks.json"
            with open(data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tech stacks: {str(e)}")
            return []

    def _generate_embeddings(self) -> Dict[str, Any]:
        """
        Generate embeddings for all tech stack descriptions
        """
        try:
            descriptions = [stack['description'] for stack in self.tech_stacks]
            embeddings = self.embedding_service.get_embeddings_batch(descriptions)
            return {
                stack['name']: embedding 
                for stack, embedding in zip(self.tech_stacks, embeddings)
            }
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return {}

    def get_recommendations(self, project_description: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get top-k tech stack recommendations based on project description
        """
        try:
            # Generate embedding for project description
            project_embedding = self.embedding_service.get_embedding(project_description)

            # Calculate similarities
            similarities = []
            for stack_name, embedding in self.tech_stack_embeddings.items():
                similarity = self.embedding_service.compute_similarity(
                    project_embedding, 
                    embedding
                )
                similarities.append((stack_name, similarity))

            # Sort by similarity and get top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_stacks = similarities[:top_k]

            # Get full stack information
            recommendations = []
            for stack_name, similarity in top_stacks:
                stack_info = next(
                    (s for s in self.tech_stacks if s['name'] == stack_name),
                    None
                )
                if stack_info:
                    recommendations.append({
                        **stack_info,
                        'similarity_score': similarity
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise 