import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from ..data.processing.data_processor import DataProcessor
from ..data.collection.base_collector import BaseCollector

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.processor = DataProcessor()
        self.index = None
        self.project_data = []
        self._initialize_index()

    def _initialize_index(self):
        """Initialize the FAISS index with project data."""
        try:
            # Load and process project data
            collector = BaseCollector()
            raw_data = collector.get_all_data()
            self.project_data = self.processor.process_data(raw_data)
            
            # Create embeddings
            descriptions = [item['description'] for item in self.project_data]
            embeddings = self.model.encode(descriptions)
            
            # Initialize FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"Initialized FAISS index with {len(self.project_data)} projects")
        except Exception as e:
            logger.error(f"Error initializing index: {str(e)}")
            raise

    async def get_recommendation(
        self,
        description: str,
        requirements: List[str] = None,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get tech stack recommendations based on project description."""
        try:
            # Encode the input description
            query_embedding = self.model.encode([description])[0]
            
            # Search for similar projects
            k = 5  # Number of similar projects to retrieve
            distances, indices = self.index.search(
                query_embedding.reshape(1, -1).astype('float32'),
                k
            )
            
            # Get similar projects
            similar_projects = [self.project_data[i] for i in indices[0]]
            
            # Analyze technology patterns
            tech_patterns = self._analyze_tech_patterns(similar_projects)
            
            # Generate recommendation
            recommendation = {
                'primary_stack': tech_patterns['primary'],
                'alternatives': tech_patterns['alternatives'],
                'explanation': self._generate_explanation(description, similar_projects),
                'confidence': self._calculate_confidence(distances[0]),
                'similar_projects': similar_projects
            }
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            raise

    def _analyze_tech_patterns(self, similar_projects: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze technology patterns in similar projects."""
        tech_counts = {}
        for project in similar_projects:
            for tech in project['technologies']:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        # Sort technologies by frequency
        sorted_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Split into primary and alternative stacks
        primary = [tech for tech, count in sorted_techs if count >= len(similar_projects) // 2]
        alternatives = [tech for tech, count in sorted_techs if count < len(similar_projects) // 2]
        
        return {
            'primary': primary,
            'alternatives': alternatives
        }

    def _generate_explanation(self, description: str, similar_projects: List[Dict[str, Any]]) -> str:
        """Generate explanation for the recommendation."""
        # This is a simple implementation. In a real system, you might want to use an LLM
        # to generate more detailed and contextual explanations.
        return (
            f"Based on {len(similar_projects)} similar projects, we recommend this tech stack "
            f"as it has been successfully used in similar contexts. The stack is optimized for "
            f"scalability and maintainability."
        )

    def _calculate_confidence(self, distances: List[float]) -> float:
        """Calculate confidence score based on similarity distances."""
        # Convert distances to similarity scores (0-1 range)
        similarities = 1 / (1 + np.array(distances))
        # Calculate average similarity
        return float(np.mean(similarities)) 