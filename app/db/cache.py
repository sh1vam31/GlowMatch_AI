import time
import logging
from typing import Optional, Any
import json
from app.config import settings

logger = logging.getLogger(__name__)


class InMemoryCache:
    def __init__(self):
        self._store: dict[str, tuple[Any, Optional[float]]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[str]:
        if key in self._store:
            val, expire_at = self._store[key]
            if expire_at is None or time.time() < expire_at:
                self._hits += 1
                return val
            else:
                del self._store[key]
        self._misses += 1
        return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        expire_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expire_at)
        return True

    def incr(self, key: str, ttl: Optional[int] = None) -> int:
        current_str = self.get(key)
        val = int(current_str) if current_str else 0
        val += 1
        self.set(key, str(val), ttl=ttl)
        return val

    def metrics(self) -> dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0.0
        return {
            "backend": "in_memory_dict",
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "keys_count": len(self._store)
        }


class RedisCacheWrapper:
    def __init__(self, redis_url: str):
        import redis
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[str]:
        try:
            val = self._client.get(key)
            if val is not None:
                self._hits += 1
            else:
                self._misses += 1
            return val
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
            self._misses += 1
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        try:
            if ttl:
                self._client.setex(key, ttl, value)
            else:
                self._client.set(key, value)
            return True
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
            return False

    def incr(self, key: str, ttl: Optional[int] = None) -> int:
        try:
            val = self._client.incr(key)
            if ttl and val == 1:
                self._client.expire(key, ttl)
            return val
        except Exception as e:
            logger.warning(f"Redis incr failed: {e}")
            return 1

    def metrics(self) -> dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0.0
        return {
            "backend": "upstash_redis",
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }


_cache_instance = None


def get_cache():
    global _cache_instance
    if _cache_instance is None:
        if settings.REDIS_URL:
            logger.info(f"Initializing Redis cache backend with URL: {settings.REDIS_URL}")
            try:
                _cache_instance = RedisCacheWrapper(settings.REDIS_URL)
            except Exception as e:
                logger.error(f"Failed to initialize Redis, falling back to dict cache: {e}")
                _cache_instance = InMemoryCache()
        else:
            logger.warning("REDIS_URL unset — using in-process dict cache fallback (local dev only).")
            _cache_instance = InMemoryCache()
    return _cache_instance


def check_cache_health() -> dict:
    cache = get_cache()
    return cache.metrics()
