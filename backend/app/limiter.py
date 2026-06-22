import os
from slowapi import Limiter
from slowapi.util import get_remote_address

REDIS_URL = os.getenv("REDIS_URL", "")

# Use Redis storage when available so rate limits are enforced consistently
# across all ECS task replicas. Falls back to in-process memory (single-task only).
_storage_uri = REDIS_URL if REDIS_URL else "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,
)
