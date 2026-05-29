from __future__ import annotations

import time
import uuid
from typing import Dict, Any, List

from backend.app.runtime.real_action_execution_bridge import (
    execute_real_action_packet,
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
) -> Dict[str, Any]:

    client_owned_agents = client_owned_agents or []

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

        real_execution_result = execute_real_action_packet(
            {
                "packet_id": packet.get("packet_id"),
                "assigned_agent": assigned_agent,
                "implementation_action": (
                    packet.get("implementation_action")
                    or packet.get("title")
                    or specialist["completed_output"]
                ),
                "risk_level": packet.get("risk_level", "medium"),
            },
            actor_role="owner_admin",
            owner_approved=owner_approved,
            tenant_id="owner_admin",
        )

        packet_result.update({
            "execution_status": real_execution_result.get("execution_status"),
            "delegate_execution": (
                "executed"
                if real_execution_result.get("performed_actual_action")
                else "blocked"
            ),
            "performed_actual_action": real_execution_result.get("performed_actual_action", False),
            "real_execution": True,
            "deliverable": real_execution_result.get("deliverable"),
            "completed_output": (
                real_execution_result.get("deliverable", {})
                .get("content", {})
                .get("body")
            ),
            "external_action_performed": real_execution_result.get("external_provider_called", False),
            "live_external_call_executed": real_execution_result.get("external_provider_called", False),
        })

        execution_results.append(packet_result)

    return {
        "success": True,
        "profile": "delegated_workforce_execution_runtime_v1",
        "execution_id": f"delegated_exec_{uuid.uuid4().hex[:12]}",
        "completed_count": len(execution_results),
        "queued_count": len(queued_results),
        "blocked_count": len(blocked_results),
        "completed_results": execution_results,
        "queued_results": queued_results,
        "blocked_results": blocked_results,
        "enterprise_access": enterprise_access,
        "customer_safe": True,
        "credential_values_exposed": False,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "created_at_ms": _now_ms(),
    }
