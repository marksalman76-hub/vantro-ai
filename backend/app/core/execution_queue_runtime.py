from __future__ import annotations

from typing import Any, Dict

from backend.app.runtime.durable_execution_queue_runtime import (
    enqueue_execution_job,
    fail_execution_job,
    get_execution_queue_status,
    list_execution_jobs,
)


def enqueue_execution(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload or {})
    result = enqueue_execution_job(
        queue_name=str(payload.get("queue_name") or "execution_queue"),
        tenant_id=str(payload.get("tenant_id") or "").strip(),
        project_id=str(payload.get("project_id") or "default_project").strip(),
        agent_id=str(payload.get("agent_id") or payload.get("requested_agent") or "").strip(),
        action_type=str(payload.get("action_type") or payload.get("action") or "").strip(),
        payload=payload,
        idempotency_key=str(payload.get("idempotency_key") or "").strip(),
        max_attempts=int(payload.get("max_attempts") or payload.get("max_retries") or 3),
    )
    if result.get("job_id") and "queue_id" not in result:
        result["queue_id"] = result["job_id"]
    return result


def list_execution_queue(tenant_id: str = "", status: str = "", limit: int = 50) -> Dict[str, Any]:
    return list_execution_jobs(
        queue_name="execution_queue",
        tenant_id=tenant_id,
        status=status,
        limit=limit,
    )


def mark_execution_failed(queue_id: Any, error: str) -> Dict[str, Any]:
    return fail_execution_job(
        job_id=str(queue_id or ""),
        error=str(error or "execution_failed"),
        worker_id="admin_mark_failed",
    )


def queue_readiness() -> Dict[str, Any]:
    return get_execution_queue_status(queue_name="execution_queue")
