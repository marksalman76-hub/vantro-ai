from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
TARGET = RUNTIME_DIR / "media_job_acceptance_service.py"
TEST = ROOT / "test_media_job_acceptance_service.py"
BACKUP_DIR = ROOT / "backups" / f"media_job_acceptance_service_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

TARGET.write_text(r'''from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.runtime.durable_media_job_store import LocalDurableMediaJobStore
from backend.app.runtime.durable_media_asset_store import LocalDurableMediaAssetStore
from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue
from backend.app.runtime.portal_authority_context import (
    build_portal_authority_context,
    enforce_execution_authority,
    redact_for_portal,
)


class MediaJobAcceptanceService:
    """
    AWS-ready API job acceptance foundation.

    Current local/dev implementation:
    - normalize request authority
    - create durable job
    - enqueue queue message
    - return job_id quickly

    Production target:
    - API service on ECS/Fargate
    - RDS durable job record
    - SQS enqueue
    - S3 assets
    - portal-safe response shaping
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

    def accept_media_job(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request = dict(request or {})

        authority = build_portal_authority_context(request)
        decision = enforce_execution_authority(request, authority)

        if not decision.get("allowed"):
            return {
                "success": False,
                "accepted": False,
                "status": "rejected",
                "reason": decision.get("reason") or "not_allowed",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        job_payload = {
            **request,
            "portal_mode": authority.get("portal_mode"),
            "tenant_id": request.get("tenant_id") or request.get("client_id") or authority.get("tenant_id") or "",
            "client_id": request.get("client_id") or authority.get("client_id") or "",
            "status": "queued",
            "provider_plan": {
                "video_provider": request.get("video_provider") or "runway",
                "audio_provider": request.get("audio_provider") or "elevenlabs",
                "composition": request.get("composition_provider") or "ffmpeg",
                "queue_backend": "local_dev",
                "aws_target": "ecs_fargate_worker_sqs_s3_rds",
            },
            "progress": {"stage": "queued", "percent": 0},
        }

        job = self.job_store.create_job(job_payload)
        job_id = job["job_id"]

        enqueue_payload = {
            "job_id": job_id,
            "portal_mode": authority.get("portal_mode"),
            "actor_id": request.get("actor_id") or request.get("admin_id") or request.get("client_id") or "",
            "client_id": job_payload.get("client_id") or "",
            "tenant_id": job_payload.get("tenant_id") or "",
            "role": request.get("role") or authority.get("role") or "",
            "is_owner": authority.get("is_owner"),
            "is_admin": authority.get("is_admin"),
            "media_type": request.get("media_type") or "complete_video",
            "requires_credit_check": decision.get("requires_credit_check"),
            "requires_package_check": decision.get("requires_package_check"),
            "requires_owner_approval": decision.get("requires_owner_approval"),
            "provider_plan": job_payload["provider_plan"],
        }

        enqueued = self.queue.enqueue(
            job_id=job_id,
            payload=enqueue_payload,
            queue_name="media_generation",
            priority=int(request.get("priority") or 100),
            max_attempts=int(request.get("max_attempts") or 3),
        )

        if not enqueued.get("success"):
            self.job_store.update_status(
                job_id,
                "queue_failed",
                progress={"stage": "queue_failed", "percent": 0},
                event={"event": "queue_enqueue_failed", "queue_result": enqueued},
            )
            return {
                "success": False,
                "accepted": False,
                "status": "queue_failed",
                "job_id": job_id,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        self.job_store.update_status(
            job_id,
            "queued",
            progress={"stage": "queued", "percent": 1},
            event={
                "event": "media_job_accepted_and_queued",
                "message_id": enqueued.get("message_id"),
                "portal_mode": authority.get("portal_mode"),
                "authority_reason": decision.get("reason"),
            },
        )

        fresh_job = self.job_store.get_job(job_id)
        safe_job = redact_for_portal(fresh_job, authority)

        response = {
            "success": True,
            "accepted": True,
            "status": "queued",
            "job_id": job_id,
            "message_id": enqueued.get("message_id"),
            "portal_mode": authority.get("portal_mode"),
            "authority": authority,
            "decision": decision,
            "job": safe_job,
            "customer_safe": True,
            "credential_values_exposed": False,
            "next": {
                "worker": "media_worker_process_next",
                "status_route_target": "GET /media/jobs/{job_id}",
                "aws_target": "api_accepts_job_sqs_worker_processes",
            },
        }

        return redact_for_portal(response, authority)

    def get_media_job_status(self, job_id: str, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        request = dict(request or {})
        authority = build_portal_authority_context(request)
        job = self.job_store.get_job(job_id)
        return redact_for_portal(job, authority)


def accept_media_job(request: Dict[str, Any]) -> Dict[str, Any]:
    return MediaJobAcceptanceService().accept_media_job(request)


def get_media_job_status(job_id: str, request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return MediaJobAcceptanceService().get_media_job_status(job_id, request)
''', encoding="utf-8")

TEST.write_text(r'''from pathlib import Path
import shutil

from backend.app.runtime.durable_media_job_store import LocalDurableMediaJobStore
from backend.app.runtime.durable_media_asset_store import LocalDurableMediaAssetStore
from backend.app.runtime.durable_media_queue import LocalDurableMediaQueue
from backend.app.runtime.media_job_acceptance_service import MediaJobAcceptanceService


def make_service(name: str):
    root = Path("runtime_outputs") / name
    if root.exists():
        shutil.rmtree(root)

    job_store = LocalDurableMediaJobStore(root=root / "jobs")
    asset_store = LocalDurableMediaAssetStore(root=root / "assets")
    queue = LocalDurableMediaQueue(root=root / "queue")
    service = MediaJobAcceptanceService(job_store=job_store, asset_store=asset_store, queue=queue)
    return service, job_store, asset_store, queue


def test_admin_acceptance():
    service, job_store, asset_store, queue = make_service("media_job_acceptance_admin")

    result = service.accept_media_job({
        "portal_mode": "admin",
        "role": "owner",
        "actor_id": "owner_test",
        "prompt": "Create a cinematic brand video.",
        "duration_seconds": 60,
        "media_type": "complete_video",
        "selected_agent": "marketing_specialist_agent",
        "human_mode": "No human/avatar",
        "api_key": "should-never-leak",
    })

    assert result["success"] is True
    assert result["accepted"] is True
    assert result["status"] == "queued"
    assert result["portal_mode"] == "admin"
    assert result["decision"]["requires_credit_check"] is False
    assert result["decision"]["requires_package_check"] is False
    assert result["decision"]["requires_owner_approval"] is False
    assert result["credential_values_exposed"] is False

    job = job_store.get_job(result["job_id"])
    assert job["success"] is True
    assert job["status"] == "queued"
    assert job["creative_controls"]["duration_seconds"] == 60

    stats = queue.stats()
    assert stats["ready"] == 1


def test_client_acceptance():
    service, job_store, asset_store, queue = make_service("media_job_acceptance_client")

    result = service.accept_media_job({
        "portal_mode": "client",
        "client_id": "client_test",
        "tenant_id": "client_test",
        "actor_id": "client_test",
        "prompt": "Create a client paid media video.",
        "duration_seconds": 30,
        "media_type": "complete_video",
        "selected_agent": "marketing_specialist_agent",
        "human_mode": "Use client-uploaded face/likeness",
        "uploaded_likeness_asset_id": "asset_face_ref_001",
        "explicit_likeness_consent": True,
        "owner_approval_required": True,
        "provider_diagnostics": {"should": "not leak"},
        "api_key": "should-never-leak",
    })

    assert result["success"] is True
    assert result["accepted"] is True
    assert result["status"] == "queued"
    assert result["portal_mode"] == "client"
    assert result["decision"]["requires_credit_check"] is True
    assert result["decision"]["requires_package_check"] is True
    assert result["decision"]["requires_owner_approval"] is True
    assert result["credential_values_exposed"] is False

    response_text = str(result)
    assert "should-never-leak" not in response_text
    assert "not leak" not in response_text

    job = job_store.get_job(result["job_id"])
    assert job["success"] is True
    assert job["creative_controls"]["human"]["human_mode"] == "Use client-uploaded face/likeness"
    assert job["creative_controls"]["human"]["explicit_likeness_consent"] is True

    client_status = service.get_media_job_status(result["job_id"], {
        "portal_mode": "client",
        "client_id": "client_test",
    })
    assert client_status["credential_values_exposed"] is False
    assert "provider_diagnostics" not in str(client_status)

    stats = queue.stats()
    assert stats["ready"] == 1


def main():
    test_admin_acceptance()
    test_client_acceptance()
    print("MEDIA_JOB_ACCEPTANCE_SERVICE_TEST_PASSED")


if __name__ == "__main__":
    main()
''', encoding="utf-8")

print("MEDIA_JOB_ACCEPTANCE_SERVICE_INSTALLED")
print(f"Updated: {TARGET}")
print(f"Created test: {TEST}")
print(f"Backup folder: {BACKUP_DIR}")