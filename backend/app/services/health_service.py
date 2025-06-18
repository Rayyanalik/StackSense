import logging
from typing import Dict, Any
import psutil
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

logger = logging.getLogger(__name__)

class HealthService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)  # Dimension for all-MiniLM-L6-v2

    async def check_health(self) -> Dict[str, Any]:
        """Check the health of the API and its dependencies."""
        try:
            health_status = {
                'status': 'healthy',
                'components': {
                    'api': self._check_api_health(),
                    'model': self._check_model_health(),
                    'index': self._check_index_health(),
                    'system': self._check_system_health()
                }
            }
            
            # Overall status is healthy only if all components are healthy
            if not all(comp['status'] == 'healthy' for comp in health_status['components'].values()):
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def _check_api_health(self) -> Dict[str, Any]:
        """Check API health."""
        return {
            'status': 'healthy',
            'message': 'API is running'
        }

    def _check_model_health(self) -> Dict[str, Any]:
        """Check if the embedding model is working."""
        try:
            # Test the model with a simple sentence
            test_text = "Test sentence for health check"
            embedding = self.model.encode([test_text])
            
            return {
                'status': 'healthy',
                'message': 'Model is working',
                'embedding_shape': embedding.shape
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Model error: {str(e)}'
            }

    def _check_index_health(self) -> Dict[str, Any]:
        """Check if the FAISS index is working."""
        try:
            # Test the index with a random vector
            test_vector = np.random.rand(1, 384).astype('float32')
            self.index.search(test_vector, 1)
            
            return {
                'status': 'healthy',
                'message': 'Index is working',
                'dimension': self.index.d
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Index error: {str(e)}'
            }

    def _check_system_health(self) -> Dict[str, Any]:
        """Check system resources."""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'status': 'healthy',
                'message': 'System resources are available',
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                }
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'System check error: {str(e)}'
            } 