from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from backend.app.runtime.provider_workforce_runtime_hardening import (
    provider_runtime_health_summary,
    provider_recovery_readiness_summary,
)
from backend.app.runtime.durable_orchestration_state_runtime import (
    create_orchestration_plan,
    create_orchestration_step,
    create_recovery_checkpoint,
    get_orchestration_recovery_packet,
    record_orchestration_event,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def create_agent_to_agent_execution_packet(
    *,
    tenant_id: str,
    project_id: str,
    parent_agent: str,
    target_agent: str,
    task: str,
    orchestration_id: Optional[str] = None,
    priority: int = 5,
    requires_owner_approval: bool = False,
) -> Dict[str, Any]:
    packet_id = f"agent_packet_{uuid.uuid4().hex[:16]}"
    orchestration_id = orchestration_id or f"orch_{uuid.uuid4().hex[:16]}"

    return {
        "success": True,
        "profile": "agent_to_agent_execution_packet_v1",
        "packet_id": packet_id,
        "orchestration_id": orchestration_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "parent_agent": parent_agent,
        "target_agent": target_agent,
        "task": task,
        "priority": int(priority),
        "status": "prepared",
        "requires_owner_approval": bool(requires_owner_approval),
        "owner_approval_required_for_spend_scale_contracts": True,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def create_delegated_subtask_plan(
    *,
    tenant_id: str,
    project_id: str,
    lead_agent: str,
    objective: str,
    requested_agents: Optional[List[str]] = None,
) -> Dict[str, Any]:
    requested_agents = requested_agents or [
        "marketing_specialist_agent",
        "seo_agent",
        "crm_ai_agent",
    ]
    orchestration_id = f"orch_{uuid.uuid4().hex[:16]}"

    packets = [
        create_agent_to_agent_execution_packet(
            tenant_id=tenant_id,
            project_id=project_id,
            parent_agent=lead_agent,
            target_agent=agent,
            task=f"Support objective: {objective}",
            orchestration_id=orchestration_id,
            priority=index + 1,
            requires_owner_approval=False,
        )
        for index, agent in enumerate(requested_agents)
    ]

    persisted = create_orchestration_plan(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id,
        project_id=project_id,
        root_agent_id=lead_agent,
        status="prepared_for_governed_execution",
        plan_type="autonomous_workforce_delegated_subtask_plan",
        payload={
            "objective": objective,
            "requested_agents": requested_agents,
            "execution_mode": "planning_only",
            "governance_enforced": True,
        },
    )
    if not persisted.get("success"):
        return persisted

    previous_step_id = None
    for index, packet in enumerate(packets, start=1):
        step_id = str(packet.get("packet_id") or f"{orchestration_id}_step_{index:03d}")
        create_orchestration_step(
            step_id=step_id,
            orchestration_id=orchestration_id,
            tenant_id=tenant_id,
            agent_id=str(packet.get("target_agent") or ""),
            action_type="agent_to_agent_execution_packet",
            status="prepared",
            dependency_step_ids=[previous_step_id] if previous_step_id else [],
        )
        previous_step_id = step_id

    create_recovery_checkpoint(
        orchestration_id=orchestration_id,
        tenant_id=tenant_id,
        checkpoint_type="delegated_subtask_plan_created",
        recoverable_status="prepared_for_governed_execution",
        payload={"packet_count": len(packets), "objective": objective},
    )

    return {
        "success": True,
        "profile": "delegated_subtask_plan_v1",
        "orchestration_id": orchestration_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "lead_agent": lead_agent,
        "objective": objective,
        "packet_count": len(packets),
        "packets": packets,
        "status": "prepared_for_governed_execution",
        "execution_mode": "planning_only",
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "created_at_ms": _now_ms(),
        "canonical_persistence": {
            "success": True,
            "storage_mode": persisted.get("storage_mode"),
            "durable": persisted.get("durable", False),
            "dev_only": persisted.get("dev_only", False),
        },
    }


def create_orchestration_execution_graph(plan: Dict[str, Any]) -> Dict[str, Any]:
    packets = list(plan.get("packets") or [])
    nodes = []
    edges = []

    lead_agent = str(plan.get("lead_agent") or "head_agent")
    orchestration_id = str(plan.get("orchestration_id") or f"orch_{uuid.uuid4().hex[:16]}")

    nodes.append({
        "node_id": f"agent::{lead_agent}",
        "type": "lead_agent",
        "label": lead_agent,
        "status": "ready",
    })

    for packet in packets:
        target = packet.get("target_agent")
        packet_id = packet.get("packet_id")
        nodes.append({
            "node_id": f"agent::{target}",
            "type": "delegated_agent",
            "label": target,
            "status": "prepared",
            "packet_id": packet_id,
        })
        edges.append({
            "from": f"agent::{lead_agent}",
            "to": f"agent::{target}",
            "type": "delegates_to",
            "packet_id": packet_id,
        })

    return {
        "success": True,
        "profile": "orchestration_execution_graph_v1",
        "orchestration_id": orchestration_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def orchestration_replay_recovery_packet(
    *,
    orchestration_id: str,
    failure_reason: str = "unknown",
    attempt_count: int = 0,
) -> Dict[str, Any]:
    recovery_readiness = provider_recovery_readiness_summary()

    retry_allowed = int(attempt_count) < 3
    next_action = "retry_prepared" if retry_allowed else "owner_review_required"

    checkpoint = create_recovery_checkpoint(
        orchestration_id=orchestration_id,
        tenant_id="unknown",
        checkpoint_type="orchestration_replay_recovery_packet",
        recoverable_status=next_action,
        payload={
            "failure_reason": failure_reason,
            "attempt_count": int(attempt_count),
            "retry_allowed": retry_allowed,
            "owner_review_required": not retry_allowed,
        },
    )
    if not checkpoint.get("success"):
        return checkpoint
    durable_packet = get_orchestration_recovery_packet(orchestration_id)
    record_orchestration_event(
        orchestration_id=orchestration_id,
        tenant_id="unknown",
        event_type="orchestration_replay_recovery_packet_created",
        payload={"failure_reason": failure_reason, "attempt_count": int(attempt_count), "next_action": next_action},
    )

    return {
        "success": True,
        "profile": "orchestration_replay_recovery_packet_v1",
        "orchestration_id": orchestration_id,
        "failure_reason": failure_reason,
        "attempt_count": int(attempt_count),
        "retry_allowed": retry_allowed,
        "next_action": next_action,
        "recovery_readiness": recovery_readiness,
        "owner_review_required": not retry_allowed,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
        "checkpoint": checkpoint.get("checkpoint"),
        "durable_recovery_packet": durable_packet if durable_packet.get("success") else None,
    }


def autonomous_workforce_orchestration_status() -> Dict[str, Any]:
    provider_health = provider_runtime_health_summary()
    recovery = provider_recovery_readiness_summary()

    return {
        "success": True,
        "profile": "autonomous_workforce_orchestration_foundation_v1",
        "visibility_only": True,
        "execution_mode": "governed_foundation_only",
        "autonomous_uncontrolled_actions_enabled": False,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "owner_approval_required_for_spend_scale_contracts": True,
        "foundation_layers": {
            "delegated_subtask_packets": True,
            "agent_to_agent_execution_packets": True,
            "orchestration_execution_graph": True,
            "orchestration_replay_recovery_packet": True,
            "provider_health_linked": True,
            "provider_recovery_linked": True,
            "customer_safe_status_packets": True,
            "uncontrolled_autonomy_blocked": True,
        },
        "provider_health": provider_health,
        "recovery_readiness": recovery,
        "checked_at_ms": _now_ms(),
    }
