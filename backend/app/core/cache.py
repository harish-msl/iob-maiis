"""
Redis cache management
"""
import json
from typing import Any, Optional

import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
    socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
)

async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

async def set_cache(key: str, value: Any, expire: int = None) -> bool:
    """Set value in cache"""
    try:
        serialized = json.dumps(value)
        if expire:
            await redis_client.setex(key, expire, serialized)
        else:
            await redis_client.set(key, serialized)
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False

async def delete_cache(key: str) -> bool:
    """Delete key from cache"""
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False

async def clear_cache_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            return await redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Cache clear pattern error: {e}")
        return 0
