import os
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "")

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not REDIS_URL:
        return None
    try:
        import redis
        _client = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
        _client.ping()
        logger.info("Redis cache connected: %s", REDIS_URL.split("@")[-1])
        return _client
    except Exception as e:
        logger.warning("Redis unavailable — falling back to no-cache: %s", e)
        return None


def get(key: str) -> Optional[Any]:
    r = _get_client()
    if r is None:
        return None
    try:
        raw = r.get(key)
        return json.loads(raw) if raw else None
    except Exception as e:
        logger.debug("Cache get error for %s: %s", key, e)
        return None


def set(key: str, value: Any, ttl: int = 60) -> None:
    r = _get_client()
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.debug("Cache set error for %s: %s", key, e)


def delete(*keys: str) -> None:
    r = _get_client()
    if r is None:
        return
    try:
        r.delete(*keys)
    except Exception as e:
        logger.debug("Cache delete error: %s", e)


def credits_key(user_id: str) -> str:
    return f"credits:{user_id}"


def media_jobs_key(user_id: str) -> str:
    return f"media_jobs:{user_id}"
