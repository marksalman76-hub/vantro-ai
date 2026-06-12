from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
TARGET = RUNTIME_DIR / "durable_media_queue.py"
TEST = ROOT / "test_durable_media_queue.py"
BACKUP_DIR = ROOT / "backups" / f"durable_media_queue_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

TARGET.write_text(r'''from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import time
import uuid


ROOT = Path(__file__).resolve().parents[3]
LOCAL_MEDIA_QUEUE_DIR = ROOT / "runtime_outputs" / "durable_media_queue"
READY_DIR = LOCAL_MEDIA_QUEUE_DIR / "ready"
IN_FLIGHT_DIR = LOCAL_MEDIA_QUEUE_DIR / "in_flight"
DONE_DIR = LOCAL_MEDIA_QUEUE_DIR / "done"
FAILED_DIR = LOCAL_MEDIA_QUEUE_DIR / "failed"
DLQ_DIR = LOCAL_MEDIA_QUEUE_DIR / "dead_letter"

for directory in [READY_DIR, IN_FLIGHT_DIR, DONE_DIR, FAILED_DIR, DLQ_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "media_queue_message") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def safe_filename(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isalnum() or ch in {"_", "-"}) or safe_id()


@dataclass
class DurableMediaQueueMessage:
    message_id: str
    job_id: str
    queue_name: str = "media_generation"
    status: str = "ready"
    priority: int = 100
    attempt_count: int = 0
    max_attempts: int = 3
    payload: Dict[str, Any] = None
    receipt_handle: str = ""
    visible_after: float = 0.0
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}
        if not self.created_at:
            self.created_at = utc_now()
        if not self.updated_at:
            self.updated_at = utc_now()


class LocalDurableMediaQueue:
    """
    Local implementation of the production MediaQueue contract.

    Production swap target:
    - AWS SQS standard queue for media jobs
    - AWS SQS dead-letter queue for failed jobs
    - RDS job/event records for durable status

    This file-based version is intentionally simple and deterministic for local testing.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root or LOCAL_MEDIA_QUEUE_DIR)
        self.ready_dir = self.root / "ready"
        self.in_flight_dir = self.root / "in_flight"
        self.done_dir = self.root / "done"
        self.failed_dir = self.root / "failed"
        self.dlq_dir = self.root / "dead_letter"

        for directory in [self.ready_dir, self.in_flight_dir, self.done_dir, self.failed_dir, self.dlq_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _message_path(self, directory: Path, message_id: str) -> Path:
        return directory / f"{safe_filename(message_id)}.json"

    def _write_message(self, directory: Path, message: Dict[str, Any]) -> Dict[str, Any]:
        message["updated_at"] = utc_now()
        message["customer_safe"] = True
        message["credential_values_exposed"] = False
        message["internal_config_exposed"] = False

        path = self._message_path(directory, message["message_id"])
        temp = path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(message, indent=2, default=str), encoding="utf-8")
        temp.replace(path)
        return message

    def _read_message_path(self, path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def enqueue(
        self,
        job_id: str,
        payload: Dict[str, Any],
        queue_name: str = "media_generation",
        priority: int = 100,
        max_attempts: int = 3,
    ) -> Dict[str, Any]:
        message = DurableMediaQueueMessage(
            message_id=safe_id("media_queue_message"),
            job_id=job_id,
            queue_name=queue_name,
            status="ready",
            priority=int(priority),
            attempt_count=0,
            max_attempts=int(max_attempts),
            payload=dict(payload or {}),
            visible_after=0.0,
        )

        data = asdict(message)
        self._write_message(self.ready_dir, data)

        return {
            "success": True,
            "accepted": True,
            "message_id": data["message_id"],
            "job_id": job_id,
            "queue_name": queue_name,
            "status": "ready",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def claim_next(self, queue_name: str = "media_generation", visibility_timeout_seconds: int = 900) -> Dict[str, Any]:
        now = time.time()
        candidates: List[Dict[str, Any]] = []

        for path in self.ready_dir.glob("*.json"):
            try:
                message = self._read_message_path(path)
                if message.get("queue_name") != queue_name:
                    continue
                if float(message.get("visible_after") or 0) > now:
                    continue
                message["_path"] = str(path)
                candidates.append(message)
            except Exception:
                continue

        if not candidates:
            return {
                "success": False,
                "status": "empty",
                "queue_name": queue_name,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        candidates.sort(key=lambda m: (int(m.get("priority") or 100), str(m.get("created_at") or "")))
        message = candidates[0]
        old_path = Path(message.pop("_path"))
        message["status"] = "in_flight"
        message["attempt_count"] = int(message.get("attempt_count") or 0) + 1
        message["receipt_handle"] = safe_id("receipt")
        message["visible_after"] = now + max(1, int(visibility_timeout_seconds))

        self._write_message(self.in_flight_dir, message)
        try:
            old_path.unlink()
        except FileNotFoundError:
            pass

        return {
            "success": True,
            "message": message,
            "message_id": message["message_id"],
            "job_id": message["job_id"],
            "receipt_handle": message["receipt_handle"],
            "status": "in_flight",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def complete(self, message_id: str, receipt_handle: str = "") -> Dict[str, Any]:
        path = self._message_path(self.in_flight_dir, message_id)
        if not path.exists():
            return {
                "success": False,
                "message_id": message_id,
                "status": "not_found_in_flight",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        message = self._read_message_path(path)
        if receipt_handle and message.get("receipt_handle") != receipt_handle:
            return {
                "success": False,
                "message_id": message_id,
                "status": "receipt_handle_mismatch",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        message["status"] = "done"
        self._write_message(self.done_dir, message)
        path.unlink(missing_ok=True)

        return {
            "success": True,
            "message_id": message_id,
            "job_id": message.get("job_id"),
            "status": "done",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def fail(
        self,
        message_id: str,
        error: str,
        receipt_handle: str = "",
        retry: bool = True,
    ) -> Dict[str, Any]:
        path = self._message_path(self.in_flight_dir, message_id)
        if not path.exists():
            return {
                "success": False,
                "message_id": message_id,
                "status": "not_found_in_flight",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        message = self._read_message_path(path)
        if receipt_handle and message.get("receipt_handle") != receipt_handle:
            return {
                "success": False,
                "message_id": message_id,
                "status": "receipt_handle_mismatch",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        message["last_error"] = str(error or "")[:1000]
        attempts = int(message.get("attempt_count") or 0)
        max_attempts = int(message.get("max_attempts") or 3)

        if retry and attempts < max_attempts:
            message["status"] = "ready"
            message["visible_after"] = time.time() + min(300, 15 * attempts)
            self._write_message(self.ready_dir, message)
            final_status = "requeued"
        else:
            message["status"] = "dead_letter"
            self._write_message(self.dlq_dir, message)
            final_status = "dead_letter"

        path.unlink(missing_ok=True)

        return {
            "success": True,
            "message_id": message_id,
            "job_id": message.get("job_id"),
            "status": final_status,
            "attempt_count": attempts,
            "max_attempts": max_attempts,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def requeue_expired(self) -> Dict[str, Any]:
        now = time.time()
        requeued = 0

        for path in list(self.in_flight_dir.glob("*.json")):
            try:
                message = self._read_message_path(path)
                if float(message.get("visible_after") or 0) <= now:
                    message["status"] = "ready"
                    message["receipt_handle"] = ""
                    self._write_message(self.ready_dir, message)
                    path.unlink(missing_ok=True)
                    requeued += 1
            except Exception:
                continue

        return {
            "success": True,
            "requeued": requeued,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def stats(self) -> Dict[str, Any]:
        return {
            "success": True,
            "ready": len(list(self.ready_dir.glob("*.json"))),
            "in_flight": len(list(self.in_flight_dir.glob("*.json"))),
            "done": len(list(self.done_dir.glob("*.json"))),
            "failed": len(list(self.failed_dir.glob("*.json"))),
            "dead_letter": len(list(self.dlq_dir.glob("*.json"))),
            "queue_backend": "local_dev",
            "aws_target": "sqs_with_dead_letter_queue",
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def get_media_queue() -> LocalDurableMediaQueue:
    return LocalDurableMediaQueue()
''', encoding="utf-8")

TEST.write_text(r'''from backend.app.runtime.durable_media_queue import get_media_queue


def main():
    queue = get_media_queue()

    enqueued = queue.enqueue(
        job_id="durable_media_job_queue_test_001",
        payload={
            "media_type": "complete_video",
            "duration_seconds": 30,
            "human_mode": "Generate new avatar/person",
            "provider_plan": {
                "video": "runway",
                "audio": "elevenlabs",
                "composition": "ffmpeg",
            },
        },
        priority=10,
        max_attempts=2,
    )
    assert enqueued["success"] is True
    assert enqueued["accepted"] is True
    assert enqueued["status"] == "ready"

    claimed = queue.claim_next(visibility_timeout_seconds=60)
    assert claimed["success"] is True
    assert claimed["status"] == "in_flight"
    assert claimed["job_id"] == "durable_media_job_queue_test_001"
    assert claimed["message"]["attempt_count"] == 1

    failed = queue.fail(
        claimed["message_id"],
        error="temporary provider delay",
        receipt_handle=claimed["receipt_handle"],
        retry=True,
    )
    assert failed["success"] is True
    assert failed["status"] == "requeued"

    claimed_again = queue.claim_next(visibility_timeout_seconds=60)
    assert claimed_again["success"] is True
    assert claimed_again["message"]["attempt_count"] == 2

    dead = queue.fail(
        claimed_again["message_id"],
        error="provider failed after retry",
        receipt_handle=claimed_again["receipt_handle"],
        retry=True,
    )
    assert dead["success"] is True
    assert dead["status"] == "dead_letter"

    enqueued_2 = queue.enqueue(
        job_id="durable_media_job_queue_test_002",
        payload={"media_type": "complete_video"},
        priority=20,
    )
    assert enqueued_2["success"] is True

    claimed_2 = queue.claim_next(visibility_timeout_seconds=60)
    assert claimed_2["success"] is True

    completed = queue.complete(
        claimed_2["message_id"],
        receipt_handle=claimed_2["receipt_handle"],
    )
    assert completed["success"] is True
    assert completed["status"] == "done"

    stats = queue.stats()
    assert stats["success"] is True
    assert stats["queue_backend"] == "local_dev"
    assert stats["aws_target"] == "sqs_with_dead_letter_queue"
    assert stats["dead_letter"] >= 1
    assert stats["done"] >= 1

    print("DURABLE_MEDIA_QUEUE_TEST_PASSED")
    print("dead_letter:", stats["dead_letter"])
    print("done:", stats["done"])


if __name__ == "__main__":
    main()
''', encoding="utf-8")

print("DURABLE_MEDIA_QUEUE_INSTALLED")
print(f"Updated: {TARGET}")
print(f"Created test: {TEST}")
print(f"Backup folder: {BACKUP_DIR}")