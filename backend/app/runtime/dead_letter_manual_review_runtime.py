from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.runtime.durable_manual_review_recovery_runtime import (
    create_dead_letter_record as durable_create_dead_letter_record,
    create_manual_review_item,
    ensure_manual_review_recovery_tables,
    list_dead_letter_records,
    list_manual_review_items,
    record_manual_review_decision as durable_record_manual_review_decision,
)


def create_dead_letter_record(
    *,
    tenant_id: str,
    agent_id: str,
    action_type: str,
    failure_reason: str,
    payload: Optional[Dict[str, Any]] = None,
    workflow_id: Optional[str] = None,
    retry_count: int = 0,
    severity: str = "medium",
) -> Dict[str, Any]:
    result = durable_create_dead_letter_record(
        tenant_id=tenant_id,
        project_id=str((payload or {}).get("project_id") or workflow_id or "default_project"),
        source_type="legacy_dead_letter",
        source_id=str((payload or {}).get("source_id") or workflow_id or ""),
        orchestration_id=str(workflow_id or (payload or {}).get("orchestration_id") or ""),
        orchestration_step_id=str((payload or {}).get("step_id") or (payload or {}).get("orchestration_step_id") or ""),
        queue_job_id=str((payload or {}).get("queue_job_id") or ""),
        provider_job_id=str((payload or {}).get("provider_job_id") or ""),
        reason=failure_reason,
        error_summary=failure_reason,
        payload={
            **(payload or {}),
            "agent_id": agent_id,
            "action_type": action_type,
            "retry_count": retry_count,
            "severity": severity,
            "legacy_runtime": "dead_letter_manual_review_runtime",
        },
    )
    dead_letter = dict(result.get("dead_letter") or {})
    dead_letter.setdefault("agent_id", agent_id)
    dead_letter.setdefault("action_type", action_type)
    dead_letter.setdefault("failure_reason", failure_reason)
    dead_letter.setdefault("severity", severity)
    dead_letter.setdefault("owner_review_required", True)
    dead_letter.setdefault("governance_preserved", True)
    dead_letter.setdefault("no_autonomous_spend_or_scaling", True)
    return dead_letter if dead_letter else result


def enqueue_manual_review(dead_letter_record: Dict[str, Any]) -> Dict[str, Any]:
    result = create_manual_review_item(
        tenant_id=str(dead_letter_record.get("tenant_id") or "unknown"),
        project_id=str(dead_letter_record.get("project_id") or "default_project"),
        source_type="dead_letter",
        source_id=str(dead_letter_record.get("dead_letter_id") or dead_letter_record.get("source_id") or ""),
        provider_job_id=str(dead_letter_record.get("provider_job_id") or ""),
        orchestration_id=str(dead_letter_record.get("orchestration_id") or dead_letter_record.get("workflow_id") or ""),
        orchestration_step_id=str(dead_letter_record.get("orchestration_step_id") or dead_letter_record.get("step_id") or ""),
        queue_job_id=str(dead_letter_record.get("queue_job_id") or ""),
        review_type="dead_letter_review",
        status="pending_owner_review",
        priority=str(dead_letter_record.get("severity") or "medium"),
        reason=str(dead_letter_record.get("failure_reason") or dead_letter_record.get("reason") or "manual_review_required"),
        summary=str(dead_letter_record.get("failure_reason") or dead_letter_record.get("error_summary") or "Owner/admin review required."),
        payload=dead_letter_record,
    )
    item = dict(result.get("item") or {})
    item.setdefault("dead_letter_id", dead_letter_record.get("dead_letter_id"))
    item.setdefault("failure_reason", dead_letter_record.get("failure_reason") or dead_letter_record.get("reason"))
    item.setdefault("severity", dead_letter_record.get("severity", "medium"))
    item.setdefault("owner_review_required", True)
    item.setdefault("allowed_decisions", ["retry", "mark_resolved", "reject", "escalate"])
    item.setdefault("blocked_decisions", ["increase_spend", "scale_campaign", "approve_contract"])
    item.setdefault("customer_safe_status", "Needs review")
    return item if item else result


def list_dead_letters(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    result = list_dead_letter_records(tenant_id=tenant_id or "", status=status or "", limit=limit)
    return {
        **result,
        "status": "ok" if result.get("success", True) else result.get("status"),
        "count": result.get("count", 0),
        "dead_letters": result.get("dead_letters", []),
        "governance_preserved": True,
        "owner_review_required": True,
    }


def list_manual_review_queue(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    result = list_manual_review_items(tenant_id=tenant_id or "", status=status or "", limit=limit)
    return {
        **result,
        "status": "ok" if result.get("success", True) else result.get("status"),
        "count": result.get("count", 0),
        "manual_review_items": result.get("manual_review_items", result.get("items", [])),
        "governance_preserved": True,
        "customer_safe_ui_required": True,
    }


def record_manual_review_decision(
    *,
    review_id: str,
    decision: str,
    actor_role: str,
    notes: str = "",
) -> Dict[str, Any]:
    result = durable_record_manual_review_decision(
        review_id=review_id,
        decision=decision,
        actor_role=actor_role,
        reason=notes,
        payload={"notes": notes, "legacy_runtime": "dead_letter_manual_review_runtime"},
    )
    if not result.get("success"):
        return {
            **result,
            "status": result.get("status", "blocked"),
            "governance_preserved": True,
            "no_autonomous_spend_or_scaling": True,
        }
    return {
        "status": "ok",
        "decision": result.get("decision"),
        "item": result.get("item"),
        "recovery_action": result.get("recovery_action"),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def dead_letter_readiness() -> Dict[str, Any]:
    readiness = ensure_manual_review_recovery_tables()
    return {
        **readiness,
        "status": "ready" if readiness.get("success") else readiness.get("status"),
        "runtime": "dead_letter_manual_review_runtime",
        "compatibility_wrapper_only": True,
        "canonical_runtime": "durable_manual_review_recovery_runtime",
        "owner_review_required": True,
        "governance_preserved": True,
        "entitlement_isolation_preserved": True,
        "customer_safe_ui_required": True,
        "no_autonomous_spend_or_scaling": True,
    }
