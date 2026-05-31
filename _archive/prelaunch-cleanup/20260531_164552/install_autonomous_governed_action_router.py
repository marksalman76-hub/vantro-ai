from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / f"autonomous_governed_action_router_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

router_file = runtime_dir / "autonomous_governed_action_router.py"
if router_file.exists():
    shutil.copy2(router_file, BACKUP / router_file.name)

router_file.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.app.runtime.real_action_execution_bridge import execute_real_action_packet


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
) -> Dict[str, Any]:
    governance = classify_autonomous_governance(
        packet,
        package_tier=package_tier,
        client_owned_agents=client_owned_agents,
        actor_role=actor_role,
    )

    routing_id = f"auto_route_{uuid4().hex[:12]}"

    if governance["route"] == "recommendation_only_not_owned":
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
        execution = execute_real_action_packet(
            packet={
                **packet,
                "assigned_agent": governance["assigned_agent"],
            },
            actor_role=actor_role,
            owner_approved=owner_approved,
            tenant_id=tenant_id,
        )

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
''', encoding="utf-8")

test_file = ROOT / "test_autonomous_governed_action_router.py"
test_file.write_text(r'''
from backend.app.runtime.autonomous_governed_action_router import (
    classify_autonomous_governance,
    route_autonomous_governed_packet,
    route_autonomous_governed_packets,
)

safe_packet = {
    "packet_id": "safe_001",
    "recommended_agent": "marketing_specialist_agent",
    "implementation_action": "Create a healthcare positioning strategy document draft",
    "risk_level": "medium",
}

risky_packet = {
    "packet_id": "risk_001",
    "recommended_agent": "marketing_specialist_agent",
    "implementation_action": "Launch paid campaign and increase budget",
    "risk_level": "high",
}

not_owned_packet = {
    "packet_id": "not_owned_001",
    "recommended_agent": "seo_agent",
    "implementation_action": "Create SEO topic cluster draft",
    "risk_level": "medium",
}

safe_classification = classify_autonomous_governance(
    safe_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
)
assert safe_classification["route"] == "autonomous_safe_execution"
assert safe_classification["autonomous_allowed"] is True

safe_result = route_autonomous_governed_packet(
    safe_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert safe_result["routing_status"] == "autonomously_executed"
assert safe_result["performed_actual_action"] is True
assert safe_result["deliverable"]["asset_status"] == "created"

risky_result = route_autonomous_governed_packet(
    risky_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert risky_result["routing_status"] == "queued_for_owner_approval"
assert risky_result["performed_actual_action"] is False

not_owned_result = route_autonomous_governed_packet(
    not_owned_packet,
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert not_owned_result["routing_status"] == "recommendation_only"
assert not_owned_result["performed_actual_action"] is False

batch = route_autonomous_governed_packets(
    [safe_packet, risky_packet, not_owned_packet],
    package_tier="business",
    client_owned_agents=["marketing_specialist_agent"],
    tenant_id="tenant_test",
)
assert batch["total_packets"] == 3
assert batch["autonomously_executed_count"] == 1
assert batch["owner_approval_queue_count"] == 1
assert batch["recommendation_only_count"] == 1
assert batch["performed_actual_action_count"] == 1

print("AUTONOMOUS_GOVERNED_ACTION_ROUTER_TEST_PASSED")
''', encoding="utf-8")

print("AUTONOMOUS_GOVERNED_ACTION_ROUTER_INSTALLED")
print(f"Backup: {BACKUP}")
print(f"Created/updated: {router_file}")
print(f"Created/updated: {test_file}")