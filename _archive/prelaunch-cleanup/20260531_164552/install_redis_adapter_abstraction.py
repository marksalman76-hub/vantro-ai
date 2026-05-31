from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"redis_adapter_abstraction_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

ADAPTER_FILE = ROOT / "backend" / "app" / "runtime" / "queue_adapter.py"
TEST_FILE = ROOT / "test_queue_adapter.py"

ADAPTER = r'''"""
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
'''

TEST = r'''from backend.app.runtime.queue_adapter import (
    InMemoryQueueAdapter,
    RedisQueueAdapter,
    create_queue_adapter,
    queue_adapter_live_redis_required,
    queue_adapter_changes_live_execution,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    adapter = InMemoryQueueAdapter()
    health = adapter.health()

    assert_equal(health["adapter"], "in_memory", "memory adapter name")
    assert_equal(health["available"], True, "memory available")
    assert_equal(health["redis_required"], False, "memory redis required")

    msg = adapter.enqueue("client_agent_execution_queue", {"action": "run_agent"}, {"tenant_id": "test"})
    assert msg.id
    assert_equal(msg.status, "queued", "queued status")
    assert_equal(adapter.size("client_agent_execution_queue"), 1, "queue size after enqueue")

    out = adapter.dequeue("client_agent_execution_queue")
    if out is None:
        raise AssertionError("Expected dequeued message")
    assert_equal(out.status, "dequeued", "dequeued status")
    assert_equal(out.attempts, 1, "attempt increment")
    assert_equal(adapter.size("client_agent_execution_queue"), 0, "queue size after dequeue")

    fallback = create_queue_adapter("redis")
    fallback_health = fallback.health()
    if fallback_health["adapter"] not in {"in_memory", "redis"}:
        raise AssertionError(f"Unexpected adapter: {fallback_health}")

    redis_probe = RedisQueueAdapter(redis_url=None)
    redis_health = redis_probe.health()
    assert_equal(redis_health["adapter"], "redis", "redis adapter name")
    assert_equal(redis_health["available"], False, "redis unavailable without url")

    assert_equal(queue_adapter_live_redis_required(), False, "live redis required")
    assert_equal(queue_adapter_changes_live_execution(), False, "live execution changed")

    print("QUEUE_ADAPTER_TEST_PASSED")
    print("Default adapter:", create_queue_adapter().health())


if __name__ == "__main__":
    main()
'''

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def write(path: Path, content: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    write(ADAPTER_FILE, ADAPTER)
    write(TEST_FILE, TEST)

    print("REDIS_ADAPTER_ABSTRACTION_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:")
    print("-", ADAPTER_FILE)
    print("-", TEST_FILE)
    print("Safety:")
    print("- In-memory default")
    print("- Redis optional")
    print("- No live Redis connection required")
    print("- No live route behaviour changed")


if __name__ == "__main__":
    main()