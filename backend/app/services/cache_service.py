from typing import Any, Optional, Dict, List
import json
import time
from redis import Redis
from app.core.config import settings
from app.services.logging_service import LoggingService

logger = LoggingService()

class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
        self.default_ttl = settings.CACHE_TTL
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        """
        try:
            start_time = time.time()
            value = self.redis.get(key)
            duration = (time.time() - start_time) * 1000
            
            if value is None:
                logger.debug(
                    "Cache miss",
                    extra_data={
                        'key': key,
                        'duration_ms': duration
                    }
                )
                return None
            
            logger.debug(
                "Cache hit",
                extra_data={
                    'key': key,
                    'duration_ms': duration
                }
            )
            
            return json.loads(value)
            
        except Exception as e:
            logger.error(
                "Error getting from cache",
                error=e,
                extra_data={'key': key}
            )
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache with optional TTL.
        """
        try:
            start_time = time.time()
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            
            success = self.redis.setex(
                key,
                ttl,
                serialized
            )
            
            duration = (time.time() - start_time) * 1000
            logger.debug(
                "Cache set",
                extra_data={
                    'key': key,
                    'ttl': ttl,
                    'duration_ms': duration
                }
            )
            
            return success
            
        except Exception as e:
            logger.error(
                "Error setting cache",
                error=e,
                extra_data={
                    'key': key,
                    'ttl': ttl
                }
            )
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        """
        try:
            start_time = time.time()
            success = self.redis.delete(key)
            duration = (time.time() - start_time) * 1000
            
            logger.debug(
                "Cache delete",
                extra_data={
                    'key': key,
                    'duration_ms': duration
                }
            )
            
            return bool(success)
            
        except Exception as e:
            logger.error(
                "Error deleting from cache",
                error=e,
                extra_data={'key': key}
            )
            return False
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        """
        try:
            start_time = time.time()
            values = self.redis.mget(keys)
            duration = (time.time() - start_time) * 1000
            
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = json.loads(value)
            
            logger.debug(
                "Cache multi-get",
                extra_data={
                    'keys': keys,
                    'hits': len(result),
                    'duration_ms': duration
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Error getting multiple from cache",
                error=e,
                extra_data={'keys': keys}
            )
            return {}
    
    def set_many(
        self,
        mapping: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set multiple values in cache.
        """
        try:
            start_time = time.time()
            ttl = ttl or self.default_ttl
            
            # Use pipeline for atomic operation
            pipe = self.redis.pipeline()
            for key, value in mapping.items():
                serialized = json.dumps(value)
                pipe.setex(key, ttl, serialized)
            
            results = pipe.execute()
            duration = (time.time() - start_time) * 1000
            
            success = all(results)
            logger.debug(
                "Cache multi-set",
                extra_data={
                    'keys': list(mapping.keys()),
                    'ttl': ttl,
                    'duration_ms': duration
                }
            )
            
            return success
            
        except Exception as e:
            logger.error(
                "Error setting multiple in cache",
                error=e,
                extra_data={
                    'keys': list(mapping.keys()),
                    'ttl': ttl
                }
            )
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """
        Delete multiple values from cache.
        """
        try:
            start_time = time.time()
            success = self.redis.delete(*keys)
            duration = (time.time() - start_time) * 1000
            
            logger.debug(
                "Cache multi-delete",
                extra_data={
                    'keys': keys,
                    'duration_ms': duration
                }
            )
            
            return bool(success)
            
        except Exception as e:
            logger.error(
                "Error deleting multiple from cache",
                error=e,
                extra_data={'keys': keys}
            )
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        """
        try:
            start_time = time.time()
            success = self.redis.flushdb()
            duration = (time.time() - start_time) * 1000
            
            logger.info(
                "Cache cleared",
                extra_data={'duration_ms': duration}
            )
            
            return success
            
        except Exception as e:
            logger.error(
                "Error clearing cache",
                error=e
            )
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        """
        try:
            info = self.redis.info()
            return {
                'used_memory': info['used_memory'],
                'used_memory_peak': info['used_memory_peak'],
                'connected_clients': info['connected_clients'],
                'total_keys': info['db0']['keys'],
                'hits': info['keyspace_hits'],
                'misses': info['keyspace_misses']
            }
        except Exception as e:
            logger.error(
                "Error getting cache stats",
                error=e
            )
            return {} 