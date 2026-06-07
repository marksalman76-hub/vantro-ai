from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.app.runtime.durable_execution_history_evidence_runtime import (
    ensure_execution_history_evidence_tables,
    list_execution_history,
    record_execution_evidence,
    record_execution_history,
    record_latest_deliverable,
)


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "runtime_data"
HISTORY_FILE = DATA_DIR / "action_execution_history.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_action_execution(
    *,
    tenant_id: str,
    packet_id: str | None,
    assigned_agent: str,
    execution_payload: Dict[str, Any],
) -> Dict[str, Any]:
    deliverable = execution_payload.get("deliverable") if isinstance(execution_payload.get("deliverable"), dict) else {}
    execution_id = str(execution_payload.get("execution_id") or execution_payload.get("run_id") or "")
    action_type = str(execution_payload.get("action_type") or execution_payload.get("autonomous_route") or execution_payload.get("execution_status") or "action_execution")
    status = str(execution_payload.get("execution_status") or execution_payload.get("status") or "recorded")
    summary = str(
        execution_payload.get("completed_output")
        or execution_payload.get("customer_safe_message")
        or deliverable.get("summary")
        or status
    )[:2000]

    result = record_execution_history(
        tenant_id=tenant_id,
        project_id=str(execution_payload.get("project_id") or execution_payload.get("orchestration_id") or "default_project"),
        execution_id=execution_id,
        agent_id=assigned_agent,
        workflow_id=str(execution_payload.get("workflow_id") or ""),
        orchestration_id=str(execution_payload.get("orchestration_id") or ""),
        provider_execution_id=str(execution_payload.get("provider_execution_id") or ""),
        queue_job_id=str(execution_payload.get("queue_job_id") or ""),
        action_type=action_type,
        status=status,
        summary=summary,
        payload={
            **execution_payload,
            "packet_id": packet_id,
            "assigned_agent": assigned_agent,
            "compatibility_wrapper": "persistent_action_execution_history",
        },
        completed=status in {"completed", "autonomously_executed", "owner_approved_executed"},
        failed=status in {"failed", "blocked", "manual_review_required"},
    )

    if result.get("success"):
        history = dict(result.get("history") or result.get("record") or {})
        if deliverable:
            record_latest_deliverable(
                tenant_id=tenant_id,
                project_id=str(execution_payload.get("project_id") or execution_payload.get("orchestration_id") or "default_project"),
                execution_id=execution_id,
                agent_id=assigned_agent,
                title=str(deliverable.get("title") or f"{assigned_agent} deliverable")[:500],
                summary=str(deliverable.get("summary") or summary)[:2000],
                deliverable_type=str(deliverable.get("type") or "action_deliverable"),
                status="ready",
                payload=deliverable,
                deliverable_id=str(deliverable.get("deliverable_id") or ""),
            )
            record_execution_evidence(
                tenant_id=tenant_id,
                project_id=str(execution_payload.get("project_id") or execution_payload.get("orchestration_id") or "default_project"),
                execution_id=execution_id,
                evidence_type="action_execution_history",
                title=str(deliverable.get("title") or "Action execution evidence"),
                summary=summary,
                source_type="action_execution_history",
                source_id=str(history.get("history_id") or ""),
                status=status,
                payload={"deliverable": deliverable, "packet_id": packet_id},
            )
        return {
            **history,
            "history_id": history.get("history_id") or result.get("history_id"),
            "tenant_id": tenant_id or "unknown",
            "packet_id": packet_id,
            "assigned_agent": assigned_agent,
            "execution_status": status,
            "autonomous_route": execution_payload.get("autonomous_route"),
            "performed_actual_action": execution_payload.get("performed_actual_action", False),
            "adapter": execution_payload.get("adapter") or deliverable.get("adapter"),
            "actions_performed": execution_payload.get("actions_performed") or deliverable.get("actions_performed", []),
            "deliverable": deliverable or execution_payload.get("deliverable"),
            "customer_safe": True,
            "credential_values_exposed": False,
            "created_at": history.get("created_at") or _now(),
        }

    return result


def list_action_execution_history(
    *,
    tenant_id: str | None = None,
    limit: int = 50,
) -> Dict[str, Any]:
    result = list_execution_history(tenant_id=tenant_id or "", limit=limit)
    records = result.get("records", [])
    return {
        **result,
        "success": bool(result.get("success")),
        "profile": "persistent_action_execution_history_v1",
        "canonical_runtime": "durable_execution_history_evidence_runtime",
        "tenant_id": tenant_id,
        "count": len(records),
        "records": records,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def action_execution_history_readiness() -> Dict[str, Any]:
    readiness = ensure_execution_history_evidence_tables()
    return {
        **readiness,
        "success": bool(readiness.get("success")),
        "profile": "persistent_action_execution_history_v1",
        "canonical_runtime": "durable_execution_history_evidence_runtime",
        "history_file": str(HISTORY_FILE),
        "history_file_exists": HISTORY_FILE.exists(),
        "compatibility_wrapper_only": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
