import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError

from .config import get_redis_url, db_settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache utility class."""
    
    def __init__(self):
        self.redis_url = get_redis_url()
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.client.ping()
            logger.info("Redis connection established")
        except RedisError as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except RedisError:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected():
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if not self.is_connected():
            return False
        
        try:
            serialized_value = json.dumps(value)
            return self.client.setex(key, ttl, serialized_value)
        except (RedisError, TypeError) as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.client.expire(key, ttl))
        except RedisError as e:
            logger.error(f"Error setting TTL for cache key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key."""
        if not self.is_connected():
            return -1
        
        try:
            return self.client.ttl(key)
        except RedisError as e:
            logger.error(f"Error getting TTL for cache key {key}: {e}")
            return -1
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.is_connected():
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all cache."""
        if not self.is_connected():
            return False
        
        try:
            self.client.flushdb()
            return True
        except RedisError as e:
            logger.error(f"Error clearing all cache: {e}")
            return False


class CacheManager:
    """High-level cache manager with business logic."""
    
    def __init__(self):
        self.redis = RedisCache()
    
    def cache_analysis_result(self, analysis_id: str, result: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache data analysis result."""
        key = f"analysis_result:{analysis_id}"
        return self.redis.set(key, result, ttl)
    
    def get_cached_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get cached data analysis result."""
        key = f"analysis_result:{analysis_id}"
        return self.redis.get(key)
    
    def cache_tool_generation(self, tool_id: str, tool_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache tool generation result."""
        key = f"tool_generation:{tool_id}"
        return self.redis.set(key, tool_data, ttl)
    
    def get_cached_tool_generation(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get cached tool generation result."""
        key = f"tool_generation:{tool_id}"
        return self.redis.get(key)
    
    def cache_user_data(self, user_id: str, user_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache user data."""
        key = f"user:{user_id}"
        return self.redis.set(key, user_data, ttl)
    
    def get_cached_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user data."""
        key = f"user:{user_id}"
        return self.redis.get(key)
    
    def cache_analysis_list(self, user_id: str, analyses: List[Dict[str, Any]], ttl: int = 300) -> bool:
        """Cache user's analysis list."""
        key = f"user_analyses:{user_id}"
        return self.redis.set(key, analyses, ttl)
    
    def get_cached_analysis_list(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached user's analysis list."""
        key = f"user_analyses:{user_id}"
        return self.redis.get(key)
    
    def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries for a user."""
        patterns = [
            f"user:{user_id}",
            f"user_analyses:{user_id}",
            f"analysis_result:*"  # Will need more specific pattern
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.redis.clear_pattern(pattern)
        
        return total_deleted > 0
    
    def cache_system_stats(self, stats: Dict[str, Any], ttl: int = 600) -> bool:
        """Cache system statistics."""
        key = "system_stats"
        return self.redis.set(key, stats, ttl)
    
    def get_cached_system_stats(self) -> Optional[Dict[str, Any]]:
        """Get cached system statistics."""
        key = "system_stats"
        return self.redis.get(key)
    
    def cache_api_response(self, endpoint: str, params: Dict[str, Any], response: Any, ttl: int = 300) -> bool:
        """Cache API response."""
        # Create a hash of the endpoint and parameters
        import hashlib
        param_str = json.dumps(params, sort_keys=True)
        cache_key = f"api:{endpoint}:{hashlib.md5(param_str.encode()).hexdigest()}"
        return self.redis.set(cache_key, response, ttl)
    
    def get_cached_api_response(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached API response."""
        import hashlib
        param_str = json.dumps(params, sort_keys=True)
        cache_key = f"api:{endpoint}:{hashlib.md5(param_str.encode()).hexdigest()}"
        return self.redis.get(cache_key)


# Global cache manager instance
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return cache_manager