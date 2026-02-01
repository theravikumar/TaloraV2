# api/database/redis_client.py
"""
Redis client for session management and caching
"""
import redis
import json
from typing import Any, Optional
from datetime import timedelta
from api.config import get_settings

settings = get_settings()

# Redis connection pool
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=10
)


class RedisCache:
    """Redis cache wrapper with JSON serialization"""
    
    @staticmethod
    def get(key: str) -> Optional[dict]:
        """Get value from Redis"""
        value = redis_client.get(key)
        return json.loads(value) if value else None
    
    @staticmethod
    def set(key: str, value: dict, ttl: int = None):
        """Set value in Redis with optional TTL (seconds)"""
        redis_client.set(key, json.dumps(value), ex=ttl)
    
    @staticmethod
    def delete(key: str):
        """Delete key from Redis"""
        redis_client.delete(key)
    
    @staticmethod
    def exists(key: str) -> bool:
        """Check if key exists"""
        return redis_client.exists(key) > 0
    
    @staticmethod
    def update_heartbeat(session_id: str, ttl: int = 300):
        """Update session heartbeat timestamp"""
        key = f"session:{session_id}"
        if redis_client.exists(key):
            # Refresh TTL
            redis_client.expire(key, ttl)
            return True
        return False


def get_redis() -> redis.Redis:
    """Get Redis client (for dependency injection)"""
    return redis_client
