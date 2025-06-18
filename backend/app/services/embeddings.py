from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Initialize the model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Initialized SentenceTransformer model")

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text input
        """
        try:
            embedding = self.model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts
        """
        try:
            embeddings = self.model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        """
        try:
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise 