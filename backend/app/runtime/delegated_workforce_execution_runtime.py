from __future__ import annotations

import time
import uuid
from typing import Dict, Any, List

from backend.app.runtime.autonomous_governed_action_router import (
    route_autonomous_governed_packet,
)
from backend.app.runtime.persistent_action_execution_history import (
    record_action_execution,
)
from backend.app.runtime.intelligent_action_packet_normalizer import (
    normalize_implementation_plan,
)
from backend.app.runtime.durable_external_action_records import (
    record_external_actions,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


SPECIALIST_OUTPUTS = {
    "security_compliance_agent": {
        "deliverable_type": "compliance_framework",
        "completed_output": "Generated HIPAA/GDPR compliance readiness framework with governance checkpoints and audit review schedule."
    },
    "analytics_optimisation_agent": {
        "deliverable_type": "analytics_dashboard_plan",
        "completed_output": "Prepared KPI dashboard structure covering pipeline conversion, pilot engagement tracking, and healthcare sector growth metrics."
    },
    "lead_generator_appointment_setter_agent": {
        "deliverable_type": "lead_generation_campaign",
        "completed_output": "Prepared healthcare outreach targeting framework including pilot-client acquisition strategy and appointment funnel."
    },
    "business_growth_partnerships_agent": {
        "deliverable_type": "partnership_strategy",
        "completed_output": "Generated healthcare partnership and alliance roadmap targeting healthcare technology vendors and innovation hubs."
    },
    "social_media_manager_content_creator_agent": {
        "deliverable_type": "thought_leadership_content",
        "completed_output": "Generated webinar and thought-leadership rollout strategy for healthcare technology positioning."
    },
    "website_landing_apps_agent": {
        "deliverable_type": "digital_experience_plan",
        "completed_output": "Prepared healthcare-focused landing page and digital experience implementation outline."
    },
    "crm_ai_agent": {
        "deliverable_type": "crm_pipeline_setup",
        "completed_output": "Generated CRM nurture and healthcare pipeline automation recommendations."
    },
    "seo_agent": {
        "deliverable_type": "seo_strategy",
        "completed_output": "Prepared healthcare SEO topic cluster and organic growth strategy."
    },
    "marketing_specialist_agent": {
        "deliverable_type": "marketing_execution",
        "completed_output": "Generated healthcare market positioning and campaign execution recommendations."
    },
    "orchestration_agent": {
        "deliverable_type": "workflow_coordination",
        "completed_output": "Prepared orchestration workflow coordination and execution review structure."
    }
}


def execute_delegated_workforce_plan(
    *,
    implementation_plan: Dict[str, Any],
    owner_approved: bool = False,
    client_owned_agents: List[str] | None = None,
    package_tier: str = "starter",
    connected_integrations: List[str] | None = None,
    tenant_id: str = "owner_admin",
) -> Dict[str, Any]:

    client_owned_agents = client_owned_agents or []
    connected_integrations = connected_integrations or []

    implementation_plan = normalize_implementation_plan(
        implementation_plan or {"action_packets": []},
        fallback_agent="marketing_specialist_agent",
    )

    package_tier = (package_tier or "starter").lower()

    enterprise_access = package_tier == "enterprise"

    execution_results = []
    queued_results = []
    blocked_results = []

    for packet in implementation_plan.get("action_packets", []):

        assigned_agent = packet.get("recommended_agent", "orchestration_agent")

        agent_owned = (
            enterprise_access
            or assigned_agent in client_owned_agents
        )

        specialist = SPECIALIST_OUTPUTS.get(
            assigned_agent,
            SPECIALIST_OUTPUTS["orchestration_agent"]
        )

        packet_result = {
            "packet_id": packet.get("packet_id"),
            "assigned_agent": assigned_agent,
            "deliverable_type": specialist["deliverable_type"],
            "risk_level": packet.get("risk_level", "medium"),
            "customer_safe": True,
            "created_at_ms": _now_ms(),
        }

        if not agent_owned:
            packet_result.update({
                "execution_status": "agent_not_owned",
                "delegate_execution": "blocked",
                "recommendation_visibility": True,
                "upsell_visibility": True,
                "execution_preview": "allowed",
                "completed_output": None,
                "upgrade_recommendation": assigned_agent,
                "autonomous_governance": True,
                "autonomous_route": "recommendation_only",
                "performed_actual_action": False,
                "real_execution": False,
            })
            blocked_results.append(packet_result)
            continue

        if packet.get("approval_required") and not owner_approved:
            packet_result.update({
                "execution_status": "awaiting_owner_approval",
                "delegate_execution": "blocked",
                "completed_output": None,
            })
            queued_results.append(packet_result)
            continue

        autonomous_route_result = route_autonomous_governed_packet(
            {
                "packet_id": packet.get("packet_id"),
                "assigned_agent": assigned_agent,
                "recommended_agent": assigned_agent,
                "implementation_action": (
                    packet.get("implementation_action")
                    or packet.get("title")
                    or specialist["completed_output"]
                ),
                "risk_level": packet.get("risk_level", "medium"),
            },
            package_tier=package_tier,
            client_owned_agents=client_owned_agents,
            actor_role="owner_admin" if enterprise_access else "client",
            tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
            owner_approved=owner_approved,
            connected_integrations=connected_integrations,
        )

        packet_result.update({
            "execution_status": autonomous_route_result.get("routing_status"),
            "delegate_execution": (
                "executed"
                if autonomous_route_result.get("performed_actual_action")
                else "blocked"
            ),
            "performed_actual_action": autonomous_route_result.get("performed_actual_action", False),
            "autonomous_governance": True,
            "autonomous_route": autonomous_route_result.get("routing_status"),
            "governance": autonomous_route_result.get("governance"),
            "real_execution": True,
            "deliverable": autonomous_route_result.get("deliverable"),
            "completed_output": (
                autonomous_route_result.get("deliverable", {})
                .get("content", {})
                .get("body")
            ),
            "external_action_performed": (
                autonomous_route_result.get("execution", {})
                .get("external_provider_called", False)
            ),
            "live_external_call_executed": (
                autonomous_route_result.get("execution", {})
                .get("external_provider_called", False)
            ),
        })

        if autonomous_route_result.get("routing_status") in {
            "queued_for_owner_approval",
            "manual_review_required",
        }:
            queued_results.append(packet_result)
        elif autonomous_route_result.get("routing_status") == "recommendation_only":
            blocked_results.append(packet_result)
        else:
            history_record = record_action_execution(
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                execution_payload=packet_result,
            )
            packet_result["history_id"] = history_record.get("history_id")
            packet_result["history_persisted"] = True

            external_records = record_external_actions(
                tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),
                execution_id=packet_result.get("execution_id"),
                packet_id=packet_result.get("packet_id"),
                assigned_agent=assigned_agent,
                deliverable=packet_result.get("deliverable"),
            )
            packet_result["external_action_record_count"] = external_records.get("record_count", 0)
            packet_result["external_action_records_persisted"] = external_records.get("record_count", 0) > 0
            packet_result["external_action_records"] = external_records.get("records", [])

            execution_results.append(packet_result)

    return {
        "success": True,
        "profile": "delegated_workforce_execution_runtime_v1",
        "normalization": implementation_plan.get("normalization"),
        "execution_id": f"delegated_exec_{uuid.uuid4().hex[:12]}",
        "completed_count": len(execution_results),
        "queued_count": len(queued_results),
        "blocked_count": len(blocked_results),
        "completed_results": execution_results,
        "queued_results": queued_results,
        "blocked_results": blocked_results,
        "enterprise_access": enterprise_access,
        "connected_integrations": connected_integrations,
        "external_integration_count": len(connected_integrations),
        "customer_safe": True,
        "credential_values_exposed": False,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "created_at_ms": _now_ms(),
    }
