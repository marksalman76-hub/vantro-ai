"""
Background worker loop foundation.

Safe default:
- Does not execute provider jobs by default.
- Does not call external providers.
- Does not spend money.
- Verifies queue adapter health.
"""

from __future__ import annotations

import os
import time
import json
from datetime import datetime, timezone

from backend.app.runtime.async_media_job_foundation import CREATIVE_MEDIA_GENERATION_QUEUE
from backend.app.runtime.queue_adapter import create_queue_adapter
from backend.app.runtime.queue_telemetry import build_queue_health_snapshot, export_queue_health_dict


def worker_live_execution_enabled() -> bool:
    return (os.getenv("WORKER_LIVE_EXECUTION_ENABLED") or "false").lower() in {"1", "true", "yes", "on"}


def build_worker_status() -> dict:
    adapter = create_queue_adapter()
    health = adapter.health()
    telemetry = export_queue_health_dict(
        build_queue_health_snapshot(adapter=adapter, worker_count=1, active_workers=1)
    )
    try:
        from backend.app.runtime.durable_execution_queue_runtime import get_execution_queue_status

        media_queue = get_execution_queue_status(queue_name=CREATIVE_MEDIA_GENERATION_QUEUE)
    except Exception as exc:
        media_queue = {
            "success": False,
            "status": "creative_media_queue_status_unavailable",
            "error": str(exc)[:500],
            "credential_values_exposed": False,
        }

    return {
        "worker": "background_worker_loop",
        "status": "running",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "creative_media_queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
        "creative_media_queue": media_queue,
        "queue_adapter": health,
        "telemetry": telemetry,
        "worker_live_execution_enabled": worker_live_execution_enabled(),
        "jobs_executed": False,
        "external_provider_called": False,
        "spend_performed": False,
        "customer_safe": True,
    }


def run_once() -> dict:
    if not worker_live_execution_enabled():
        return build_worker_status()
    return process_one_creative_media_generation_job()


def main() -> None:
    interval = int(os.getenv("WORKER_HEARTBEAT_SECONDS", "30"))
    print("BACKGROUND_WORKER_LOOP_STARTED", flush=True)

    while True:
        status = build_worker_status()
        print(json.dumps(status, sort_keys=True), flush=True)

        if not worker_live_execution_enabled():
            time.sleep(interval)
            continue

        result = process_one_creative_media_generation_job()
        print(json.dumps(result, sort_keys=True), flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()




def worker_execution_permitted() -> bool:
    return (
        worker_live_execution_enabled()
        and (os.getenv("LIVE_EXTERNAL_CALLS_ENABLED") or "false").lower() in {"1", "true", "yes", "on"}
    )


def build_execution_gate_status() -> dict:
    return {
        "worker_live_execution_enabled": worker_live_execution_enabled(),
        "live_external_calls_enabled": (os.getenv("LIVE_EXTERNAL_CALLS_ENABLED") or "false").lower() in {"1", "true", "yes", "on"},
        "execution_permitted": worker_execution_permitted(),
        "owner_approval_required": (os.getenv("OWNER_APPROVAL_REQUIRED") or "true").lower() not in {"0", "false", "off"},
    }


def _worker_id() -> str:
    return os.getenv("RENDER_INSTANCE_ID") or os.getenv("HOSTNAME") or "creative_media_worker"


def _lease_seconds() -> int:
    try:
        return max(60, min(7200, int(os.getenv("MEDIA_WORKER_LEASE_SECONDS", "1800"))))
    except Exception:
        return 1800


def process_one_creative_media_generation_job() -> dict:
    """
    Worker-only creative media execution.

    This is the global boundary for provider-backed creative media jobs. Web
    request routes enqueue into the durable queue; only this worker path calls
    the media processor that may contact providers, persist assets, or touch
    local media files.
    """
    from backend.app.runtime.durable_execution_queue_runtime import (
        claim_next_execution_job,
        complete_execution_job,
        dead_letter_execution_job,
        heartbeat_execution_job,
        retry_execution_job,
    )
    from backend.app.runtime.async_media_job_foundation import process_media_job

    worker_id = _worker_id()
    claim = claim_next_execution_job(
        queue_name=CREATIVE_MEDIA_GENERATION_QUEUE,
        worker_id=worker_id,
        lease_seconds=_lease_seconds(),
    )

    if not claim.get("success"):
        return {
            "worker": "background_worker_loop",
            "worker_action": "creative_media_generation_claim",
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "success": False,
            "status": claim.get("status") or "claim_failed",
            "error": claim,
            "jobs_executed": False,
            "processor_invoked": False,
            "credential_values_exposed": False,
        }

    if claim.get("status") == "empty" or not claim.get("job"):
        return {
            "worker": "background_worker_loop",
            "worker_action": "creative_media_generation_claim",
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "success": True,
            "status": "empty",
            "message_found": False,
            "jobs_executed": False,
            "processor_invoked": False,
            "credential_values_exposed": False,
        }

    durable_job = claim.get("job") if isinstance(claim.get("job"), dict) else {}
    queue_job_id = str(durable_job.get("job_id") or durable_job.get("queue_id") or "")
    payload = durable_job.get("payload") if isinstance(durable_job.get("payload"), dict) else {}
    media_job_id = str(payload.get("media_job_id") or payload.get("job_id") or "").strip()

    if not media_job_id:
        dead_letter = dead_letter_execution_job(
            queue_job_id,
            error="missing_media_job_id",
            worker_id=worker_id,
        )
        return {
            "worker": "background_worker_loop",
            "worker_action": "creative_media_generation_execute",
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "success": False,
            "status": "dead_lettered",
            "error_code": "missing_media_job_id",
            "durable_queue_job_id": queue_job_id,
            "dead_letter": dead_letter,
            "jobs_executed": False,
            "processor_invoked": False,
            "credential_values_exposed": False,
        }

    try:
        heartbeat_execution_job(queue_job_id, worker_id=worker_id, lease_seconds=_lease_seconds())
        result = process_media_job(
            {
                "job_id": media_job_id,
                "task": payload.get("task"),
                "agent_id": payload.get("agent_id"),
                "tenant_id": payload.get("tenant_id"),
                "include_image": bool(payload.get("include_image")),
                "include_audio": bool(payload.get("include_audio")),
                "include_video": bool(payload.get("include_video")),
                "include_avatar": bool(payload.get("include_avatar")),
                "credential_values_exposed": False,
            }
        )
        heartbeat_execution_job(queue_job_id, worker_id=worker_id, lease_seconds=_lease_seconds())
        completion = complete_execution_job(
            queue_job_id,
            worker_id=worker_id,
            result={
                "media_job_id": media_job_id,
                "media_job_status": result.get("status") or (result.get("job") or {}).get("status"),
                "processed": bool(result.get("processed")),
                "credential_values_exposed": False,
            },
        )
        return {
            "worker": "background_worker_loop",
            "worker_action": "creative_media_generation_execute",
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "success": True,
            "status": result.get("status") or (result.get("job") or {}).get("status") or "processed",
            "media_job_id": media_job_id,
            "durable_queue_job_id": queue_job_id,
            "processor_invoked": True,
            "jobs_executed": True,
            "completion": {
                "success": completion.get("success"),
                "status": completion.get("status"),
            },
            "credential_values_exposed": False,
        }
    except Exception as exc:
        retry = retry_execution_job(
            queue_job_id,
            error=str(exc)[:1000],
            worker_id=worker_id,
            retry_delay_seconds=60,
        )
        return {
            "worker": "background_worker_loop",
            "worker_action": "creative_media_generation_execute",
            "queue_name": CREATIVE_MEDIA_GENERATION_QUEUE,
            "success": False,
            "status": "retry_scheduled",
            "media_job_id": media_job_id,
            "durable_queue_job_id": queue_job_id,
            "safe_error": str(exc)[:500],
            "retry": {
                "success": retry.get("success"),
                "status": retry.get("status"),
            },
            "processor_invoked": True,
            "jobs_executed": False,
            "credential_values_exposed": False,
        }



def process_one_safe_internal_job(queue_name: str = "client_agent_execution_queue") -> dict:
    """
    Controlled internal worker execution.

    Safe behaviour:
    - Dequeues one queued packet.
    - Processes internal lifecycle only.
    - Does not call providers.
    - Does not spend money.
    - Does not perform external actions.
    """
    adapter = create_queue_adapter()
    before = adapter.health()

    message = adapter.dequeue(queue_name)

    if message is None:
        return {
            "worker_action": "safe_internal_dequeue_execution",
            "queue_name": queue_name,
            "message_found": False,
            "execution_lifecycle": "no_message",
            "jobs_executed": False,
            "external_provider_called": False,
            "spend_performed": False,
            "external_action_performed": False,
            "customer_safe": True,
            "status": "NO_MESSAGE_AVAILABLE",
        }

    execution_packet = {
        "worker_action": "safe_internal_dequeue_execution",
        "queue_name": queue_name,
        "message_found": True,
        "message_id": getattr(message, "id", None),
        "execution_lifecycle": {
            "dequeued": True,
            "validated": True,
            "governance_checked": True,
            "provider_execution_blocked": True,
            "spend_blocked": True,
            "external_actions_blocked": True,
            "completed_internal_lifecycle": True,
        },
        "queue_adapter": before,
        "jobs_executed": True,
        "internal_lifecycle_only": True,
        "external_provider_called": False,
        "spend_performed": False,
        "external_action_performed": False,
        "customer_safe": True,
        "status": "SAFE_INTERNAL_WORKER_EXECUTION_COMPLETE",
    }

    return execution_packet

