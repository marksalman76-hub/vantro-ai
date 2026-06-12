from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
WORKERS_DIR = ROOT / "backend" / "app" / "workers"
TARGET = WORKERS_DIR / "media_worker.py"
TEST = ROOT / "test_media_worker_foundation.py"
BACKUP_DIR = ROOT / "backups" / f"media_worker_foundation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

WORKERS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

TARGET.write_text(r'''from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime, timezone

from backend.app.runtime.durable_media_job_store import LocalDurableMediaJobStore
from backend.app.runtime.durable_media_asset_store import LocalDurableMediaAssetStore
from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue
from backend.app.runtime.portal_authority_context import (
    build_portal_authority_context,
    enforce_execution_authority,
    redact_for_portal,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MediaWorker:
    """
    AWS-ready media worker foundation.

    Current local/dev implementation:
    - claim message from LocalDurableMediaQueue
    - load job from LocalDurableMediaJobStore
    - apply PortalAuthorityContext
    - update durable job status/events
    - complete/fail queue message

    Production target:
    - ECS/Fargate worker container
    - SQS media queue + dead-letter queue
    - RDS job/event store
    - S3 asset store
    - CloudWatch logs

    This foundation intentionally does not call external providers yet.
    """

    def __init__(
        self,
        job_store: Optional[LocalDurableMediaJobStore] = None,
        asset_store: Optional[LocalDurableMediaAssetStore] = None,
        queue: Optional[LocalDurableMediaQueue] = None,
    ):
        self.job_store = job_store or LocalDurableMediaJobStore()
        self.asset_store = asset_store or LocalDurableMediaAssetStore()
        self.queue = queue or LocalDurableMediaQueue()

    def process_next(self, queue_name: str = "media_generation") -> Dict[str, Any]:
        claimed = self.queue.claim_next(queue_name=queue_name, visibility_timeout_seconds=900)
        if not claimed.get("success"):
            return {
                "success": False,
                "status": "no_job_available",
                "queue_name": queue_name,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        message = dict(claimed.get("message") or {})
        message_id = str(claimed.get("message_id") or message.get("message_id") or "")
        receipt_handle = str(claimed.get("receipt_handle") or message.get("receipt_handle") or "")
        job_id = str(claimed.get("job_id") or message.get("job_id") or "")

        try:
            return self.process_claimed_message(message, message_id, receipt_handle, job_id)
        except Exception as error:
            self.queue.fail(
                message_id=message_id,
                receipt_handle=receipt_handle,
                error=str(error),
                retry=True,
            )
            if job_id:
                self.job_store.update_status(
                    job_id,
                    "worker_failed",
                    progress={"stage": "worker_failed", "percent": 0},
                    event={"event": "worker_exception", "error": str(error)[:500]},
                )
            return {
                "success": False,
                "status": "worker_failed",
                "job_id": job_id,
                "message_id": message_id,
                "error": str(error)[:500],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

    def process_claimed_message(
        self,
        message: Dict[str, Any],
        message_id: str,
        receipt_handle: str,
        job_id: str,
    ) -> Dict[str, Any]:
        job = self.job_store.get_job(job_id)
        if not job.get("success"):
            self.queue.fail(
                message_id=message_id,
                receipt_handle=receipt_handle,
                error="job_not_found",
                retry=False,
            )
            return {
                "success": False,
                "status": "job_not_found",
                "job_id": job_id,
                "message_id": message_id,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        payload = dict(message.get("payload") or {})
        portal_payload = {
            "portal_mode": job.get("portal_mode") or payload.get("portal_mode"),
            "role": payload.get("role"),
            "actor_id": payload.get("actor_id"),
            "client_id": job.get("client_id") or payload.get("client_id"),
            "tenant_id": job.get("tenant_id") or payload.get("tenant_id"),
            "is_owner": payload.get("is_owner"),
            "is_admin": payload.get("is_admin"),
        }

        authority = build_portal_authority_context(portal_payload)
        decision = enforce_execution_authority(payload, authority)

        self.job_store.update_status(
            job_id,
            "worker_running",
            progress={"stage": "worker_running", "percent": 10},
            event={
                "event": "worker_claimed_job",
                "message_id": message_id,
                "portal_mode": authority.get("portal_mode"),
                "authority_reason": decision.get("reason"),
            },
        )

        # Placeholder processing. Real provider execution will be wired in a later step.
        worker_event = {
            "event": "worker_foundation_processed",
            "processed_at": utc_now(),
            "provider_calls_executed": False,
            "external_media_generated": False,
            "portal_mode": authority.get("portal_mode"),
            "requires_credit_check": decision.get("requires_credit_check"),
            "requires_package_check": decision.get("requires_package_check"),
            "requires_owner_approval": decision.get("requires_owner_approval"),
        }

        self.job_store.update_status(
            job_id,
            "worker_foundation_completed",
            progress={"stage": "worker_foundation_completed", "percent": 100},
            event=worker_event,
        )

        completed = self.queue.complete(message_id=message_id, receipt_handle=receipt_handle)

        fresh_job = self.job_store.get_job(job_id)
        portal_safe_job = redact_for_portal(fresh_job, authority)

        return {
            "success": True,
            "status": "worker_foundation_completed",
            "job_id": job_id,
            "message_id": message_id,
            "queue_status": completed.get("status"),
            "authority": authority,
            "decision": decision,
            "job": portal_safe_job,
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def run_one_media_worker_cycle() -> Dict[str, Any]:
    return MediaWorker().process_next()
''', encoding="utf-8")

TEST.write_text(r'''from pathlib import Path
import shutil

from backend.app.runtime.durable_media_job_store import LocalDurableMediaJobStore
from backend.app.runtime.durable_media_asset_store import LocalDurableMediaAssetStore
from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue
from backend.app.workers.media_worker import MediaWorker


def make_isolated_worker(name: str):
    root = Path("runtime_outputs") / name
    if root.exists():
        shutil.rmtree(root)

    job_store = LocalDurableMediaJobStore(root=root / "jobs")
    asset_store = LocalDurableMediaAssetStore(root=root / "assets")
    queue = LocalDurableMediaQueue(root=root / "queue")
    worker = MediaWorker(job_store=job_store, asset_store=asset_store, queue=queue)
    return worker, job_store, asset_store, queue


def test_admin_worker_flow():
    worker, job_store, asset_store, queue = make_isolated_worker("media_worker_test_admin")

    job = job_store.create_job({
        "portal_mode": "admin",
        "role": "owner",
        "prompt": "Create a cinematic full-stack media test.",
        "duration_seconds": 30,
        "selected_agent": "marketing_specialist_agent",
        "media_type": "complete_video",
    })

    enqueued = queue.enqueue(
        job_id=job["job_id"],
        payload={
            "portal_mode": "admin",
            "role": "owner",
            "actor_id": "owner_test",
            "media_type": "complete_video",
        },
    )
    assert enqueued["success"] is True

    result = worker.process_next()
    assert result["success"] is True
    assert result["status"] == "worker_foundation_completed"
    assert result["authority"]["portal_mode"] == "admin"
    assert result["authority"]["unrestricted_execution"] is True
    assert result["decision"]["requires_credit_check"] is False
    assert result["decision"]["requires_package_check"] is False
    assert result["decision"]["requires_owner_approval"] is False

    loaded = job_store.get_job(job["job_id"])
    assert loaded["status"] == "worker_foundation_completed"

    stats = queue.stats()
    assert stats["done"] == 1


def test_client_worker_flow():
    worker, job_store, asset_store, queue = make_isolated_worker("media_worker_test_client")

    job = job_store.create_job({
        "portal_mode": "client",
        "client_id": "client_test",
        "tenant_id": "client_test",
        "prompt": "Create a governed client media test.",
        "duration_seconds": 30,
        "selected_agent": "marketing_specialist_agent",
        "media_type": "complete_video",
    })

    enqueued = queue.enqueue(
        job_id=job["job_id"],
        payload={
            "portal_mode": "client",
            "client_id": "client_test",
            "actor_id": "client_test",
            "owner_approval_required": True,
            "media_type": "complete_video",
            "provider_diagnostics": {"should": "not leak to client"},
            "api_key": "secret-test-value",
        },
    )
    assert enqueued["success"] is True

    result = worker.process_next()
    assert result["success"] is True
    assert result["status"] == "worker_foundation_completed"
    assert result["authority"]["portal_mode"] == "client"
    assert result["authority"]["unrestricted_execution"] is False
    assert result["decision"]["requires_credit_check"] is True
    assert result["decision"]["requires_package_check"] is True
    assert result["decision"]["requires_owner_approval"] is True

    assert result["job"]["credential_values_exposed"] is False
    assert result["job"]["internal_config_exposed"] is False

    loaded = job_store.get_job(job["job_id"])
    assert loaded["status"] == "worker_foundation_completed"

    stats = queue.stats()
    assert stats["done"] == 1


def main():
    test_admin_worker_flow()
    test_client_worker_flow()
    print("MEDIA_WORKER_FOUNDATION_TEST_PASSED")


if __name__ == "__main__":
    main()
''', encoding="utf-8")

print("MEDIA_WORKER_FOUNDATION_INSTALLED")
print(f"Updated: {TARGET}")
print(f"Created test: {TEST}")
print(f"Backup folder: {BACKUP_DIR}")