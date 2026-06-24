import os
from slowapi import Limiter
from slowapi.util import get_remote_address

REDIS_URL = os.getenv("REDIS_URL", "")
_TESTING = os.getenv("TESTING", "0") == "1"

# Use Redis storage when available so rate limits are enforced consistently
# across all ECS task replicas. Falls back to in-process memory (single-task only).
# Disabled entirely in test environment to prevent per-IP limits across test fixtures.
_storage_uri = REDIS_URL if REDIS_URL else "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,
    enabled=not _TESTING,
)
