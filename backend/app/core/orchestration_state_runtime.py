from __future__ import annotations

from typing import Any, Dict

from backend.app.runtime.durable_orchestration_state_runtime import (
    DURABLE_ORCHESTRATION_PROFILE,
    create_orchestration_plan,
    create_recovery_checkpoint,
    get_orchestration_context as get_durable_orchestration_context,
    get_orchestration_plan,
    get_orchestration_recovery_packet,
    list_orchestration_events,
    record_orchestration_event,
    record_orchestration_result_memory,
)
from backend.app.runtime.durable_orchestration_state_runtime import (
    ensure_orchestration_tables as ensure_durable_orchestration_tables,
)


ORCHESTRATION_STATE_PROFILE = "priority6_orchestration_state_runtime_v1"


def record_orchestration_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan_id = str(payload.get("plan_id") or payload.get("orchestration_id") or payload.get("project_id") or "state_only_orchestration")
    tenant_id = str(payload.get("tenant_id") or "unknown")
    event_type = str(payload.get("event_type") or "orchestration_state_recorded")
    event_payload = {
        "profile": ORCHESTRATION_STATE_PROFILE,
        "status": str(payload.get("status") or "recorded"),
        "step_id": payload.get("step_id"),
        "agent_id": payload.get("agent_id"),
        "dependency_status": payload.get("dependency_status") or {},
        "parallel_group": payload.get("parallel_group"),
        "head_agent_review_required": bool(payload.get("head_agent_review_required", False)),
        "recovery_marker": payload.get("recovery_marker") or f"recover_{plan_id}",
        "data": payload.get("data") or {},
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    existing = get_orchestration_plan(plan_id)
    if not existing.get("success") and existing.get("status") == "orchestration_not_found":
        created = create_orchestration_plan(
            orchestration_id=plan_id,
            tenant_id=tenant_id,
            project_id=str(payload.get("project_id") or plan_id),
            root_agent_id=str(payload.get("agent_id") or "orchestration_agent"),
            status=str(payload.get("status") or "recorded"),
            plan_type="state_only_orchestration",
            payload={"created_by": ORCHESTRATION_STATE_PROFILE},
        )
        if not created.get("success"):
            return created
    elif not existing.get("success"):
        return existing

    result = record_orchestration_event(
        orchestration_id=plan_id,
        step_id=payload.get("step_id"),
        tenant_id=tenant_id,
        event_type=event_type,
        payload=event_payload,
    )

    if result.get("success"):
        create_recovery_checkpoint(
            orchestration_id=plan_id,
            tenant_id=tenant_id,
            checkpoint_type="state_event",
            recoverable_status=str(payload.get("status") or "recorded"),
            payload=event_payload,
        )

    return {
        **result,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "canonical_orchestration_profile": DURABLE_ORCHESTRATION_PROFILE,
        "event": result.get("event"),
        "state_persisted": bool(result.get("success")),
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def record_orchestration_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan_id = str(payload.get("plan_id") or payload.get("orchestration_id") or "result_only_orchestration")
    tenant_id = str(payload.get("tenant_id") or "unknown")
    step_id = str(payload.get("step_id") or "")
    agent_id = str(payload.get("agent_id") or "")

    existing = get_orchestration_plan(plan_id)
    if not existing.get("success") and existing.get("status") == "orchestration_not_found":
        created = create_orchestration_plan(
            orchestration_id=plan_id,
            tenant_id=tenant_id,
            project_id=plan_id,
            root_agent_id=agent_id or "orchestration_agent",
            status="recorded",
            plan_type="result_only_orchestration",
            payload={"created_by": ORCHESTRATION_STATE_PROFILE},
        )
        if not created.get("success"):
            return created
    elif not existing.get("success"):
        return existing

    result = record_orchestration_result_memory(
        orchestration_id=plan_id,
        step_id=step_id or None,
        tenant_id=tenant_id,
        agent_id=agent_id,
        result_type=str(payload.get("result_type") or "agent_output"),
        result_summary=str(payload.get("result_summary") or "")[:2000],
        payload=payload.get("result_payload") or {},
    )

    if result.get("success"):
        record_orchestration_event(
            orchestration_id=plan_id,
            step_id=step_id or None,
            tenant_id=tenant_id,
            event_type="orchestration_result_recorded",
            payload={
                "agent_id": agent_id,
                "result_type": str(payload.get("result_type") or "agent_output"),
                "head_agent_review_required": bool(payload.get("head_agent_review_required", False)),
                "governance_bypass": False,
                "entitlement_bypass": False,
            },
        )

    return {
        **result,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "canonical_orchestration_profile": DURABLE_ORCHESTRATION_PROFILE,
        "memory": result.get("memory"),
        "result_memory_persisted": bool(result.get("success")),
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def get_orchestration_context(plan_id: str, limit: int = 50) -> Dict[str, Any]:
    result = get_durable_orchestration_context(str(plan_id or ""), limit=limit)
    return {
        **result,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "canonical_orchestration_profile": DURABLE_ORCHESTRATION_PROFILE,
        "plan_id": str(plan_id or ""),
        "cross_agent_context_available": bool(result.get("result_memory")),
        "recovery_context_available": bool(result.get("state_events") or result.get("recovery_checkpoints")),
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def orchestration_recovery_packet(plan_id: str) -> Dict[str, Any]:
    result = get_orchestration_recovery_packet(str(plan_id or ""))
    return {
        **result,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "canonical_orchestration_profile": DURABLE_ORCHESTRATION_PROFILE,
        "plan_id": str(plan_id or ""),
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def orchestration_state_readiness() -> Dict[str, Any]:
    readiness = ensure_durable_orchestration_tables()
    event_count = 0
    if readiness.get("success"):
        event_count = list_orchestration_events(limit=1000).get("count", 0)

    return {
        **readiness,
        "success": readiness.get("success", False),
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "canonical_orchestration_profile": DURABLE_ORCHESTRATION_PROFILE,
        "orchestration_state_persistence_enabled": readiness.get("success", False),
        "orchestration_result_memory_enabled": readiness.get("success", False),
        "cross_agent_output_passing_enabled": True,
        "orchestration_recovery_continuation_enabled": True,
        "parallel_execution_scheduling_foundation": True,
        "head_agent_review_runtime_foundation": True,
        "orchestration_telemetry_enabled": True,
        "orchestration_replay_recovery_tooling_enabled": True,
        "state_event_count": event_count,
        "customer_safe_response_mode": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }
