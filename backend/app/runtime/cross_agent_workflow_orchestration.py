from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.runtime.durable_orchestration_state_runtime import (
    create_orchestration_plan,
    create_orchestration_step,
    create_recovery_checkpoint,
    ensure_orchestration_tables,
    get_orchestration_context,
    get_orchestration_plan,
    record_orchestration_event,
    record_orchestration_result_memory,
    update_orchestration_plan_status,
    update_orchestration_step_status,
)
from backend.app.runtime.persistent_workflow_runtime import (
    action_requires_owner_approval,
    create_workflow,
    get_workflow,
)


HEAD_AGENT_IDS = {"head_agent", "ceo_agent", "orchestration_agent"}

SPECIALIST_AGENT_ALLOWLIST = {
    "marketing_specialist_agent",
    "email_reply_agent",
    "crm_ai_agent",
    "seo_agent",
    "social_media_manager_agent",
    "content_creator_agent",
    "product_description_agent",
    "influencer_collaboration_agent",
    "customer_support_agent",
    "analytics_agent",
    "website_builder_agent",
    "shopify_agent",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_cross_agent_orchestration_store() -> Dict[str, Any]:
    readiness = ensure_orchestration_tables()
    return {
        **readiness,
        "success": readiness.get("success", False),
        "status": "cross_agent_orchestration_store_ready" if readiness.get("success") else readiness.get("status"),
        "db_path": "canonical_postgres_or_dev_memory",
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
    }


def _normalise_agent(agent_id: str) -> str:
    return str(agent_id or "").strip().lower()


def can_head_agent_orchestrate(head_agent_id: str, active_agent_count: int = 2) -> bool:
    return _normalise_agent(head_agent_id) in HEAD_AGENT_IDS and int(active_agent_count) >= 2


def _task_from_step(step: Dict[str, Any], event_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = deepcopy(event_payload or {})
    return {
        "task_id": step.get("step_id"),
        "assigned_agent_id": step.get("agent_id"),
        "task_type": step.get("action_type"),
        "status": step.get("status"),
        "sequence_order": int(payload.get("sequence_order") or 0),
        "owner_approval_required": bool(payload.get("owner_approval_required", False)),
        "retry_count": int(step.get("attempt_count") or payload.get("retry_count") or 0),
        "max_retries": int(payload.get("max_retries") or 3),
        "payload": deepcopy(payload.get("task_payload") or {}),
        "result": deepcopy(payload.get("task_result") or {}),
        "error": deepcopy(payload.get("task_error") or {}),
    }


def _context_events(orchestration_id: str) -> List[Dict[str, Any]]:
    context = get_orchestration_context(orchestration_id, limit=300)
    if not context.get("success"):
        return []
    return [
        {
            "task_id": event.get("step_id"),
            "event_type": event.get("event_type"),
            "event_status": (event.get("payload") or {}).get("status") or event.get("event_type"),
            "created_at": event.get("created_at"),
            "details": event.get("payload") or {},
        }
        for event in context.get("events", [])
    ]


def create_cross_agent_orchestration(
    orchestration_id: str,
    workflow_id: str,
    objective: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    tenant_id: Optional[str] = None,
    head_agent_id: str = "head_agent",
    active_agent_count: int = 2,
) -> Dict[str, Any]:
    store = init_cross_agent_orchestration_store()
    if not store.get("success"):
        return store

    if not can_head_agent_orchestrate(head_agent_id, active_agent_count):
        return {
            "success": False,
            "status": "head_agent_orchestration_not_allowed",
            "orchestration_id": orchestration_id,
            "head_agent_id": head_agent_id,
            "active_agent_count": active_agent_count,
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "credential_values_exposed": False,
        }

    workflow_type = str(objective.get("workflow_type") or "cross_agent_orchestration").strip().lower()
    workflow = create_workflow(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        payload={
            "objective": objective,
            "task_count": len(tasks),
            "head_agent_id": head_agent_id,
        },
        tenant_id=tenant_id,
        actor_role=head_agent_id,
        max_retries=int(objective.get("max_retries", 3)),
    )
    if not workflow.get("success"):
        return workflow

    orchestration_status = "blocked_pending_owner_approval" if workflow.get("owner_approval_required") else "pending"
    created = create_orchestration_plan(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id or "unknown",
        project_id=workflow_id,
        root_agent_id=head_agent_id,
        status=orchestration_status,
        plan_type="cross_agent_orchestration",
        payload={
            "workflow_id": workflow_id,
            "objective": deepcopy(objective),
            "head_agent_id": head_agent_id,
            "task_count": len(tasks),
            "compatibility_wrapper": "cross_agent_workflow_orchestration",
        },
    )
    if not created.get("success"):
        return created

    for index, task in enumerate(tasks, start=1):
        agent_id = _normalise_agent(task.get("assigned_agent_id"))
        task_type = str(task.get("task_type") or "specialist_task").strip().lower()
        approval_required = action_requires_owner_approval(task_type)
        allowed_agent = agent_id in SPECIALIST_AGENT_ALLOWLIST
        status = "blocked_agent_not_allowed"
        if allowed_agent:
            status = "blocked_pending_owner_approval" if approval_required else "pending"

        task_id = str(task.get("task_id") or f"{orchestration_id}_task_{index:03d}")
        create_orchestration_step(
            step_id=task_id,
            orchestration_id=orchestration_id,
            tenant_id=tenant_id or "unknown",
            agent_id=agent_id,
            action_type=task_type,
            status=status,
            dependency_step_ids=list(task.get("dependency_step_ids") or []),
        )
        record_orchestration_event(
            orchestration_id=orchestration_id,
            step_id=task_id,
            tenant_id=tenant_id or "unknown",
            event_type="cross_agent_task_created",
            payload={
                "status": status,
                "sequence_order": index,
                "owner_approval_required": approval_required,
                "task_payload": deepcopy(task.get("payload") or {}),
                "max_retries": int(task.get("max_retries", 3)),
            },
        )

    record_orchestration_event(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id or "unknown",
        event_type="orchestration_created",
        payload={
            "workflow_id": workflow_id,
            "tenant_id": tenant_id,
            "head_agent_id": head_agent_id,
            "task_count": len(tasks),
            "workflow_status": workflow.get("status"),
            "status": orchestration_status,
        },
    )
    create_recovery_checkpoint(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id or "unknown",
        checkpoint_type="cross_agent_orchestration_created",
        recoverable_status=orchestration_status,
        payload={"workflow_id": workflow_id, "task_count": len(tasks)},
    )

    return get_cross_agent_orchestration(orchestration_id)


def get_cross_agent_orchestration(orchestration_id: str) -> Dict[str, Any]:
    plan_result = get_orchestration_plan(orchestration_id)
    if not plan_result.get("success"):
        if plan_result.get("status") == "orchestration_not_found":
            return {
                "success": False,
                "status": "orchestration_not_found",
                "orchestration_id": orchestration_id,
                "credential_values_exposed": False,
            }
        return plan_result

    plan = plan_result.get("plan") or {}
    payload = plan.get("payload") or {}
    workflow_id = str(payload.get("workflow_id") or plan.get("project_id") or "")
    workflow = get_workflow(workflow_id) if workflow_id else {}
    events = _context_events(orchestration_id)
    task_event_payloads: Dict[str, Dict[str, Any]] = {}
    for event in events:
        if event.get("event_type") == "cross_agent_task_created" and event.get("task_id"):
            task_event_payloads[str(event.get("task_id"))] = deepcopy(event.get("details") or {})
    tasks = [
        _task_from_step(step, task_event_payloads.get(str(step.get("step_id") or "")))
        for step in plan_result.get("steps", [])
    ]
    tasks.sort(key=lambda task: int(task.get("sequence_order") or 0))

    return {
        "success": True,
        "status": plan.get("status"),
        "orchestration_id": plan.get("orchestration_id"),
        "workflow_id": workflow_id,
        "workflow_status": workflow.get("status"),
        "tenant_id": plan.get("tenant_id"),
        "head_agent_id": plan.get("root_agent_id"),
        "objective": deepcopy(payload.get("objective") or {}),
        "final_result": deepcopy(payload.get("final_result") or {}),
        "tasks": tasks,
        "events": events,
        "canonical_storage_mode": plan_result.get("storage_mode"),
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "credential_values_exposed": False,
    }


def complete_cross_agent_task(
    orchestration_id: str,
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_cross_agent_orchestration(orchestration_id)
    if not current.get("success"):
        return current

    matched = next((task for task in current["tasks"] if task["task_id"] == task_id), None)
    if not matched:
        return {
            "success": False,
            "status": "task_not_found",
            "orchestration_id": orchestration_id,
            "task_id": task_id,
            "governance_preserved": True,
            "credential_values_exposed": False,
        }

    if matched["owner_approval_required"]:
        return {
            "success": False,
            "status": "blocked_pending_owner_approval",
            "orchestration_id": orchestration_id,
            "task_id": task_id,
            "execution_status": "task_not_completed",
            "governance_preserved": True,
            "owner_approval_controls_preserved": True,
            "credential_values_exposed": False,
        }

    update_orchestration_step_status(
        step_id=task_id,
        orchestration_id=orchestration_id,
        tenant_id=current.get("tenant_id") or "unknown",
        status="completed",
    )
    record_orchestration_result_memory(
        orchestration_id=orchestration_id,
        step_id=task_id,
        tenant_id=current.get("tenant_id") or "unknown",
        agent_id=matched.get("assigned_agent_id") or "",
        result_type="cross_agent_task_result",
        result_summary=str(result or "")[:500],
        payload=result or {},
    )
    record_orchestration_event(
        orchestration_id=orchestration_id,
        step_id=task_id,
        tenant_id=current.get("tenant_id") or "unknown",
        event_type="task_completed",
        payload={**(result or {}), "status": "completed"},
    )

    updated = get_cross_agent_orchestration(orchestration_id)
    executable_tasks = [
        task for task in updated["tasks"]
        if task["status"] not in {"blocked_pending_owner_approval", "blocked_agent_not_allowed"}
    ]
    all_done = bool(executable_tasks) and all(task["status"] == "completed" for task in executable_tasks)

    if all_done:
        plan_payload = {
            **((get_orchestration_plan(orchestration_id).get("plan") or {}).get("payload") or {}),
            "final_result": {"all_executable_tasks_completed": True},
        }
        update_orchestration_plan_status(
            orchestration_id=orchestration_id,
            status="completed",
            payload=plan_payload,
            completed=True,
        )
        record_orchestration_event(
            orchestration_id=orchestration_id,
            tenant_id=current.get("tenant_id") or "unknown",
            event_type="orchestration_completed",
            payload={"all_executable_tasks_completed": True, "status": "completed"},
        )

    return get_cross_agent_orchestration(orchestration_id)


def fail_cross_agent_task(
    orchestration_id: str,
    task_id: str,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current = get_cross_agent_orchestration(orchestration_id)
    if not current.get("success"):
        return current

    matched = next((task for task in current["tasks"] if task["task_id"] == task_id), None)
    if not matched:
        return {
            "success": False,
            "status": "task_not_found",
            "orchestration_id": orchestration_id,
            "task_id": task_id,
            "governance_preserved": True,
            "credential_values_exposed": False,
        }

    retry_count = int(matched["retry_count"]) + 1
    max_retries = int(matched["max_retries"])
    status = "retry_ready" if retry_count <= max_retries else "failed_manual_review_required"

    update_orchestration_step_status(
        step_id=task_id,
        orchestration_id=orchestration_id,
        tenant_id=current.get("tenant_id") or "unknown",
        status=status,
        last_error=str(error or {}),
        increment_attempt=True,
    )
    update_orchestration_plan_status(
        orchestration_id=orchestration_id,
        status="requires_recovery" if status == "retry_ready" else "manual_review_required",
        failed=status != "retry_ready",
    )
    record_orchestration_event(
        orchestration_id=orchestration_id,
        step_id=task_id,
        tenant_id=current.get("tenant_id") or "unknown",
        event_type="task_failed",
        payload={"retry_count": retry_count, "max_retries": max_retries, "error": error or {}, "status": status},
    )
    create_recovery_checkpoint(
        orchestration_id=orchestration_id,
        tenant_id=current.get("tenant_id") or "unknown",
        checkpoint_type="cross_agent_task_failure",
        recoverable_status=status,
        payload={"task_id": task_id, "retry_count": retry_count, "max_retries": max_retries, "error": error or {}},
    )

    return get_cross_agent_orchestration(orchestration_id)


def readiness() -> Dict[str, Any]:
    store = init_cross_agent_orchestration_store()
    return {
        "success": store.get("success", False),
        "status": "cross_agent_workflow_orchestration_ready" if store.get("success") else store.get("status"),
        "store_status": store["status"],
        "db_path": store["db_path"],
        "storage_mode": store.get("storage_mode"),
        "head_agent_ids": sorted(HEAD_AGENT_IDS),
        "specialist_agent_count": len(SPECIALIST_AGENT_ALLOWLIST),
        "supports_head_agent_delegation": True,
        "supports_durable_workflow_link": True,
        "supports_task_retry_foundation": True,
        "spend_scaling_contracts_owner_gated": True,
        "governance_preserved": True,
        "owner_approval_controls_preserved": True,
        "credential_values_exposed": False,
    }
