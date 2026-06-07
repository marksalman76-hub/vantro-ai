
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.app.runtime.real_action_execution_bridge import execute_real_action_packet
from backend.app.runtime.durable_orchestration_state_runtime import (
    create_recovery_checkpoint,
    record_orchestration_event,
    record_orchestration_result_memory,
)


OWNER_APPROVAL_KEYWORDS = {
    "budget", "spend", "scale", "increase ad", "paid campaign", "payment",
    "purchase", "contract", "hire", "fire", "legal", "delete", "remove",
    "publish live", "go live", "send bulk", "bulk send", "mass email",
    "change subscription", "entitlement", "package override", "price change",
    "supplier agreement", "paid collaboration", "commission agreement",
}

AUTONOMOUS_SAFE_KEYWORDS = {
    "draft", "prepare", "create", "generate", "summarise", "summarize",
    "analyse", "analyze", "research", "outline", "checklist", "plan",
    "recommend", "preview", "framework", "document", "calendar",
    "strategy document", "email draft", "landing page draft",

    # safe operational execution verbs
    "conduct stakeholder interviews",
    "stakeholder interviews",
    "schedule interview",
    "book interview",
    "create outreach",
    "prepare outreach",
    "draft outreach",
    "analyze competitor",
    "analyse competitor",
    "identify white space",
    "develop messaging",
    "develop core messaging",
    "generate thought leadership",
    "create thought leadership",
    "develop content",
    "create content",
    "build content calendar",
    "create crm task",
    "create calendar placeholder",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _packet_text(packet: Dict[str, Any]) -> str:
    return " ".join(
        str(packet.get(k, ""))
        for k in [
            "packet_id",
            "assigned_agent",
            "recommended_agent",
            "implementation_action",
            "action",
            "title",
            "description",
            "risk",
            "risk_level",
        ]
    ).lower()


def classify_autonomous_governance(
    packet: Dict[str, Any],
    *,
    package_tier: str = "starter",
    client_owned_agents: List[str] | None = None,
    actor_role: str = "client",
) -> Dict[str, Any]:
    client_owned_agents = client_owned_agents or []

    assigned_agent = (
        packet.get("assigned_agent")
        or packet.get("recommended_agent")
        or "orchestration_agent"
    )

    package_tier_normalised = (package_tier or "starter").lower()
    enterprise_or_admin = package_tier_normalised == "enterprise" or actor_role == "owner_admin"

    entitlement_allowed = enterprise_or_admin or assigned_agent in client_owned_agents

    text = _packet_text(packet)
    risk_level = str(packet.get("risk_level") or packet.get("risk") or "medium").lower()

    owner_approval_triggered = any(k in text for k in OWNER_APPROVAL_KEYWORDS)
    safe_intent_detected = any(k in text for k in AUTONOMOUS_SAFE_KEYWORDS)

    high_risk = risk_level in {"high", "critical"} or owner_approval_triggered

    if not entitlement_allowed:
        route = "recommendation_only_not_owned"
        autonomous_allowed = False
        owner_approval_required = False
    elif high_risk:
        route = "owner_approval_required"
        autonomous_allowed = False
        owner_approval_required = True
    elif safe_intent_detected:
        route = "autonomous_safe_execution"
        autonomous_allowed = True
        owner_approval_required = False
    else:
        route = "manual_review_required"
        autonomous_allowed = False
        owner_approval_required = True

    return {
        "success": True,
        "governance_profile": "autonomous_governed_action_router_v1",
        "packet_id": packet.get("packet_id") or packet.get("id"),
        "assigned_agent": assigned_agent,
        "package_tier": package_tier_normalised,
        "actor_role": actor_role,
        "entitlement_allowed": entitlement_allowed,
        "risk_level": risk_level,
        "safe_intent_detected": safe_intent_detected,
        "owner_approval_triggered": owner_approval_triggered,
        "autonomous_allowed": autonomous_allowed,
        "owner_approval_required": owner_approval_required,
        "route": route,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }


def route_autonomous_governed_packet(
    packet: Dict[str, Any],
    *,
    package_tier: str = "starter",
    client_owned_agents: List[str] | None = None,
    actor_role: str = "client",
    tenant_id: str = "unknown",
    owner_approved: bool = False,
    connected_integrations: List[str] | None = None,
) -> Dict[str, Any]:
    governance = classify_autonomous_governance(
        packet,
        package_tier=package_tier,
        client_owned_agents=client_owned_agents,
        actor_role=actor_role,
    )

    routing_id = f"auto_route_{uuid4().hex[:12]}"
    orchestration_id = str(packet.get("orchestration_id") or packet.get("plan_id") or "")
    step_id = str(packet.get("step_id") or packet.get("packet_id") or "") or None

    def _record_route_event(status: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not orchestration_id:
            return {"success": True, "status": "not_orchestration_linked"}
        return record_orchestration_event(
            orchestration_id=orchestration_id,
            step_id=step_id,
            tenant_id=tenant_id,
            event_type="autonomous_governed_action_routed",
            payload={"routing_id": routing_id, "routing_status": status, **payload},
        )

    if governance["route"] == "recommendation_only_not_owned":
        persisted = _record_route_event("recommendation_only", {"governance": governance})
        if not persisted.get("success"):
            return persisted
        return {
            "success": True,
            "routing_id": routing_id,
            "routing_status": "recommendation_only",
            "performed_actual_action": False,
            "governance": governance,
            "customer_safe_message": "This agent is not owned by the client. Recommendation visibility only.",
            "created_at": _now(),
        }

    if governance["owner_approval_required"] and not owner_approved:
        persisted = _record_route_event("queued_for_owner_approval", {"governance": governance})
        if not persisted.get("success"):
            return persisted
        if orchestration_id:
            checkpoint = create_recovery_checkpoint(
                orchestration_id=orchestration_id,
                tenant_id=tenant_id,
                checkpoint_type="owner_approval_queue",
                recoverable_status="queued_for_owner_approval",
                payload={"routing_id": routing_id, "packet_id": packet.get("packet_id")},
            )
            if not checkpoint.get("success"):
                return checkpoint
        return {
            "success": True,
            "routing_id": routing_id,
            "routing_status": "queued_for_owner_approval",
            "performed_actual_action": False,
            "governance": governance,
            "customer_safe_message": "Action queued for owner approval under governance policy.",
            "created_at": _now(),
        }

    if governance["autonomous_allowed"] or owner_approved:
        pre_persisted = _record_route_event(
            "execution_started",
            {"governance": governance, "owner_approved": bool(owner_approved)},
        )
        if not pre_persisted.get("success"):
            return pre_persisted
        execution = execute_real_action_packet(
            packet={
                **packet,
                "assigned_agent": governance["assigned_agent"],
            },
            actor_role=actor_role,
            owner_approved=owner_approved,
            tenant_id=tenant_id,
            connected_integrations=connected_integrations or [],
        )
        persisted = _record_route_event(
            "autonomously_executed" if governance["autonomous_allowed"] else "owner_approved_executed",
            {"governance": governance, "performed_actual_action": execution.get("performed_actual_action", False)},
        )
        if not persisted.get("success"):
            return persisted
        if orchestration_id and execution.get("deliverable"):
            memory = record_orchestration_result_memory(
                orchestration_id=orchestration_id,
                step_id=step_id,
                tenant_id=tenant_id,
                agent_id=str(governance["assigned_agent"]),
                result_type="autonomous_governed_action_result",
                result_summary=str(execution.get("customer_safe_message") or execution.get("deliverable") or "")[:500],
                payload={"deliverable": execution.get("deliverable"), "routing_id": routing_id},
            )
            if not memory.get("success"):
                return memory

        return {
            "success": execution.get("success", False),
            "routing_id": routing_id,
            "routing_status": "autonomously_executed" if governance["autonomous_allowed"] else "owner_approved_executed",
            "performed_actual_action": execution.get("performed_actual_action", False),
            "governance": governance,
            "execution": execution,
            "deliverable": execution.get("deliverable"),
            "customer_safe_message": execution.get("customer_safe_message"),
            "created_at": _now(),
        }

    persisted = _record_route_event("manual_review_required", {"governance": governance})
    if not persisted.get("success"):
        return persisted
    if orchestration_id:
        checkpoint = create_recovery_checkpoint(
            orchestration_id=orchestration_id,
            tenant_id=tenant_id,
            checkpoint_type="manual_review_required",
            recoverable_status="manual_review_required",
            payload={"routing_id": routing_id, "packet_id": packet.get("packet_id")},
        )
        if not checkpoint.get("success"):
            return checkpoint
    return {
        "success": True,
        "routing_id": routing_id,
        "routing_status": "manual_review_required",
        "performed_actual_action": False,
        "governance": governance,
        "customer_safe_message": "Action requires manual review before execution.",
        "created_at": _now(),
    }


def route_autonomous_governed_packets(
    packets: List[Dict[str, Any]],
    *,
    package_tier: str = "starter",
    client_owned_agents: List[str] | None = None,
    actor_role: str = "client",
    tenant_id: str = "unknown",
    owner_approved: bool = False,
) -> Dict[str, Any]:
    results = [
        route_autonomous_governed_packet(
            packet,
            package_tier=package_tier,
            client_owned_agents=client_owned_agents,
            actor_role=actor_role,
            tenant_id=tenant_id,
            owner_approved=owner_approved,
        )
        for packet in packets
    ]

    return {
        "success": True,
        "profile": "autonomous_governed_action_router_v1",
        "total_packets": len(results),
        "autonomously_executed_count": sum(1 for r in results if r.get("routing_status") == "autonomously_executed"),
        "owner_approval_queue_count": sum(1 for r in results if r.get("routing_status") == "queued_for_owner_approval"),
        "recommendation_only_count": sum(1 for r in results if r.get("routing_status") == "recommendation_only"),
        "manual_review_count": sum(1 for r in results if r.get("routing_status") == "manual_review_required"),
        "performed_actual_action_count": sum(1 for r in results if r.get("performed_actual_action")),
        "results": results,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": _now(),
    }
