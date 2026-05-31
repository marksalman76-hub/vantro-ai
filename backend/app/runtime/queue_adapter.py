"""
Queue adapter abstraction.

Safe foundation for Redis-backed queue migration.

Default behaviour:
- Uses in-memory queue adapter.
- Does not require Redis.
- Does not connect to Redis unless explicitly requested and dependency/config exists.
- Does not execute provider actions.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional
import json
import os
import uuid


@dataclass
class QueueMessage:
    id: str
    queue_name: str
    payload: Dict[str, Any]
    created_at: str
    attempts: int = 0
    status: str = "queued"
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseQueueAdapter:
    adapter_name = "base"

    def enqueue(self, queue_name: str, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> QueueMessage:
        raise NotImplementedError

    def dequeue(self, queue_name: str) -> Optional[QueueMessage]:
        raise NotImplementedError

    def size(self, queue_name: str) -> int:
        raise NotImplementedError

    def health(self) -> Dict[str, Any]:
        raise NotImplementedError


class InMemoryQueueAdapter(BaseQueueAdapter):
    adapter_name = "in_memory"

    def __init__(self) -> None:
        self._queues: Dict[str, Deque[QueueMessage]] = defaultdict(deque)

    def enqueue(self, queue_name: str, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> QueueMessage:
        message = QueueMessage(
            id=str(uuid.uuid4()),
            queue_name=queue_name,
            payload=dict(payload or {}),
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=dict(metadata or {}),
        )
        self._queues[queue_name].append(message)
        return message

    def dequeue(self, queue_name: str) -> Optional[QueueMessage]:
        if not self._queues[queue_name]:
            return None
        message = self._queues[queue_name].popleft()
        message.status = "dequeued"
        message.attempts += 1
        return message

    def size(self, queue_name: str) -> int:
        return len(self._queues[queue_name])

    def health(self) -> Dict[str, Any]:
        return {
            "adapter": self.adapter_name,
            "available": True,
            "redis_required": False,
            "queue_count": len(self._queues),
            "total_messages": sum(len(queue) for queue in self._queues.values()),
        }


class RedisQueueAdapter(BaseQueueAdapter):
    adapter_name = "redis"

    def __init__(self, redis_url: Optional[str] = None) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self._client = None
        self._available = False
        self._error = None

        if not self.redis_url:
            self._error = "REDIS_URL not configured"
            return

        try:
            import redis  # type: ignore

            self._client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self._client.ping()
            self._available = True
        except Exception as exc:
            self._client = None
            self._available = False
            self._error = repr(exc)

    def _key(self, queue_name: str) -> str:
        return f"platform:queue:{queue_name}"

    def enqueue(self, queue_name: str, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> QueueMessage:
        if not self._available or self._client is None:
            raise RuntimeError(f"Redis queue adapter unavailable: {self._error}")

        message = QueueMessage(
            id=str(uuid.uuid4()),
            queue_name=queue_name,
            payload=dict(payload or {}),
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=dict(metadata or {}),
        )
        self._client.rpush(self._key(queue_name), json.dumps(message.__dict__))
        return message

    def dequeue(self, queue_name: str) -> Optional[QueueMessage]:
        if not self._available or self._client is None:
            raise RuntimeError(f"Redis queue adapter unavailable: {self._error}")

        raw = self._client.lpop(self._key(queue_name))
        if raw is None:
            return None

        data = json.loads(raw)
        data["status"] = "dequeued"
        data["attempts"] = int(data.get("attempts", 0)) + 1
        return QueueMessage(**data)

    def size(self, queue_name: str) -> int:
        if not self._available or self._client is None:
            return 0
        return int(self._client.llen(self._key(queue_name)))

    def health(self) -> Dict[str, Any]:
        return {
            "adapter": self.adapter_name,
            "available": self._available,
            "redis_required": True,
            "redis_url_configured": bool(self.redis_url),
            "error": self._error,
        }


def create_queue_adapter(preferred: Optional[str] = None) -> BaseQueueAdapter:
    mode = (preferred or os.getenv("QUEUE_BACKEND") or "memory").lower().strip()

    if mode in {"redis", "managed_redis"}:
        redis_adapter = RedisQueueAdapter()
        if redis_adapter.health().get("available"):
            return redis_adapter

    return InMemoryQueueAdapter()


def queue_adapter_live_redis_required() -> bool:
    return False


def queue_adapter_changes_live_execution() -> bool:
    return False
