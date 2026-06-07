"""
Persistent workflow runtime compatibility wrapper.

Canonical state is stored by durable_orchestration_state_runtime. This module
keeps the older workflow API surface intact for routes/tests that still call it.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.runtime.durable_orchestration_state_runtime import (
    create_orchestration_plan,
    create_recovery_checkpoint,
    ensure_orchestration_tables,
    get_orchestration_context,
    get_orchestration_plan,
    record_orchestration_event,
    record_orchestration_result_memory,
    update_orchestration_plan_status,
)


OWNER_APPROVAL_ACTIONS = {
    "increase_ad_spend",
    "scale_campaign",
    "change_budget",
    "approve_contract",
    "sign_contract",
    "purchase_media",
    "publish_live_campaign",
    "commit_financial_action",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_persistent_workflow_store() -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    return {
        **readiness,
        "success": readiness.get("success", False),
        "status": "persistent_workflow_store_ready" if readiness.get("success") else readiness.get("status"),
        "db_path": "canonical_postgres_or_dev_memory",
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def action_requires_owner_approval(action_type: Optional[str]) -> bool:
    return str(action_type or "").strip().lower() in OWNER_APPROVAL_ACTIONS


def _workflow_payload(
    *,
    workflow_type: str,
    payload: Optional[Dict[str, Any]],
    current_step: int = 0,
    max_retries: int = 3,
    retry_count: int = 0,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "workflow_type": workflow_type,
        "payload": deepcopy(payload or {}),
        "current_step": int(current_step or 0),
        "max_retries": int(max_retries or 3),
        "retry_count": int(retry_count or 0),
        "result": deepcopy(result or {}),
        "error": deepcopy(error or {}),
        "compatibility_wrapper": "persistent_workflow_runtime",
    }


def _from_plan(plan_result: Dict[str, Any]) -> Dict[str, Any]:
    if not plan_result.get("success"):
        return {
            **plan_result,
            "workflow_id": plan_result.get("orchestration_id"),
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    plan = plan_result.get("plan") or {}
    payload = plan.get("payload") or {}
    workflow_type = str(payload.get("workflow_type") or plan.get("plan_type") or "")
    context = get_orchestration_context(str(plan.get("orchestration_id") or ""), limit=200)
    events = [
        {
            "event_type": event.get("event_type"),
            "event_status": event.get("payload", {}).get("status") or event.get("event_type"),
            "created_at": event.get("created_at"),
            "details": event.get("payload") or {},
        }
        for event in context.get("events", [])
    ] if context.get("success") else []

    return {
        "success": True,
        "status": plan.get("status"),
        "workflow_id": plan.get("orchestration_id"),
        "tenant_id": plan.get("tenant_id"),
        "actor_role": plan.get("root_agent_id"),
        "workflow_type": workflow_type,
        "current_step": int(payload.get("current_step") or 0),
        "max_retries": int(payload.get("max_retries") or 3),
        "retry_count": int(payload.get("retry_count") or 0),
        "owner_approval_required": action_requires_owner_approval(workflow_type),
        "created_at": plan.get("created_at"),
        "updated_at": plan.get("updated_at"),
        "payload": deepcopy(payload.get("payload") or {}),
        "result": deepcopy(payload.get("result") or {}),
        "error": deepcopy(payload.get("error") or {}),
        "events": events,
        "canonical_storage_mode": plan_result.get("storage_mode"),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def create_workflow(
    workflow_id: str,
    workflow_type: str,
    payload: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[str] = None,
    actor_role: str = "system",
    max_retries: int = 3,
) -> Dict[str, Any]:
    workflow_type_key = str(workflow_type or "").strip().lower()
    approval_required = action_requires_owner_approval(workflow_type_key)
    status = "blocked_pending_owner_approval" if approval_required else "pending"

    created = create_orchestration_plan(
        orchestration_id=workflow_id,
        tenant_id=tenant_id or "unknown",
        project_id=workflow_id,
        root_agent_id=actor_role,
        status=status,
        plan_type=workflow_type_key,
        payload=_workflow_payload(
            workflow_type=workflow_type_key,
            payload=payload,
            max_retries=max_retries,
        ),
    )
    if not created.get("success"):
        return created

    record_orchestration_event(
        orchestration_id=workflow_id,
        tenant_id=tenant_id or "unknown",
        event_type="workflow_created",
        payload={
            "workflow_type": workflow_type_key,
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "owner_approval_required": approval_required,
            "status": status,
        },
    )
    create_recovery_checkpoint(
        orchestration_id=workflow_id,
        tenant_id=tenant_id or "unknown",
        checkpoint_type="workflow_created",
        recoverable_status=status,
        payload={"workflow_type": workflow_type_key},
    )
    return get_workflow(workflow_id)


def get_workflow(workflow_id: str) -> Dict[str, Any]:
    result = get_orchestration_plan(workflow_id)
    if not result.get("success") and result.get("status") == "orchestration_not_found":
        return {
            "success": False,
            "status": "workflow_not_found",
            "workflow_id": workflow_id,
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }
    return _from_plan(result)


def _update_workflow(
    workflow_id: str,
    *,
    status: str,
    current_step: Optional[int] = None,
    retry_count: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
    completed: bool = False,
    failed: bool = False,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    payload = _workflow_payload(
        workflow_type=current["workflow_type"],
        payload=current.get("payload") or {},
        current_step=current_step if current_step is not None else int(current.get("current_step") or 0),
        max_retries=int(current.get("max_retries") or 3),
        retry_count=retry_count if retry_count is not None else int(current.get("retry_count") or 0),
        result=result if result is not None else current.get("result") or {},
        error=error if error is not None else current.get("error") or {},
    )
    updated = update_orchestration_plan_status(
        orchestration_id=workflow_id,
        status=status,
        payload=payload,
        completed=completed,
        failed=failed,
    )
    if not updated.get("success"):
        return updated
    return get_workflow(workflow_id)


def advance_workflow(
    workflow_id: str,
    step_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    if current["owner_approval_required"]:
        return {
            **current,
            "success": False,
            "status": "blocked_pending_owner_approval",
            "execution_status": "not_advanced",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    next_step = int(current["current_step"]) + 1
    record_orchestration_event(
        orchestration_id=workflow_id,
        tenant_id=current.get("tenant_id") or "unknown",
        event_type="workflow_advanced",
        payload={"current_step": next_step, "step_result": step_result or {}, "status": "in_progress"},
    )
    record_orchestration_result_memory(
        orchestration_id=workflow_id,
        tenant_id=current.get("tenant_id") or "unknown",
        agent_id=current.get("actor_role") or "system",
        result_type="workflow_step_result",
        result_summary=str(step_result or "")[:500],
        payload=step_result or {},
    )
    return _update_workflow(workflow_id, status="in_progress", current_step=next_step, result=step_result or {})


def fail_workflow(
    workflow_id: str,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    retry_count = int(current["retry_count"]) + 1
    max_retries = int(current["max_retries"])
    status = "retry_ready" if retry_count <= max_retries else "failed_manual_review_required"

    record_orchestration_event(
        orchestration_id=workflow_id,
        tenant_id=current.get("tenant_id") or "unknown",
        event_type="workflow_failed",
        payload={"retry_count": retry_count, "max_retries": max_retries, "error": error or {}, "status": status},
    )
    create_recovery_checkpoint(
        orchestration_id=workflow_id,
        tenant_id=current.get("tenant_id") or "unknown",
        checkpoint_type="workflow_failure",
        recoverable_status=status,
        payload={"retry_count": retry_count, "max_retries": max_retries, "error": error or {}},
    )
    return _update_workflow(workflow_id, status=status, retry_count=retry_count, error=error or {}, failed=status != "retry_ready")


def complete_workflow(
    workflow_id: str,
    result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_workflow(workflow_id)
    if not current.get("success"):
        return current

    if current["owner_approval_required"]:
        return {
            **current,
            "success": False,
            "status": "blocked_pending_owner_approval",
            "execution_status": "not_completed",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
        }

    record_orchestration_event(
        orchestration_id=workflow_id,
        tenant_id=current.get("tenant_id") or "unknown",
        event_type="workflow_completed",
        payload=result or {},
    )
    record_orchestration_result_memory(
        orchestration_id=workflow_id,
        tenant_id=current.get("tenant_id") or "unknown",
        agent_id=current.get("actor_role") or "system",
        result_type="workflow_final_result",
        result_summary=str(result or "")[:500],
        payload=result or {},
    )
    return _update_workflow(workflow_id, status="completed", result=result or {}, completed=True)


def readiness() -> Dict[str, Any]:
    store = init_persistent_workflow_store()
    return {
        "success": store.get("success", False),
        "status": "persistent_workflow_runtime_ready" if store.get("success") else store.get("status"),
        "store_status": store["status"],
        "db_path": store["db_path"],
        "storage_mode": store.get("storage_mode"),
        "supports_persistent_state": True,
        "supports_retry_recovery_foundation": True,
        "spend_scaling_contracts_owner_gated": True,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "credential_values_exposed": False,
    }
