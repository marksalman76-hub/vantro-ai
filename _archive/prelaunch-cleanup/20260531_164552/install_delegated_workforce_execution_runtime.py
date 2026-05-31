from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

runtime = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"
main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_delegated_workforce_execution_runtime.py"

backup = ROOT / "backups" / f"delegated_workforce_execution_runtime_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)

if main_file.exists():
    shutil.copy2(main_file, backup / "main.py")

runtime.parent.mkdir(parents=True, exist_ok=True)

runtime.write_text(r'''
from __future__ import annotations

import time
import uuid
from typing import Dict, Any, List


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

        packet_result.update({
            "execution_status": "completed",
            "delegate_execution": "executed",
            "completed_output": specialist["completed_output"],
            "external_action_performed": False,
            "live_external_call_executed": False,
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
'''.lstrip(), encoding="utf-8")

main_text = main_file.read_text(encoding="utf-8")

import_block = '''
from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)
'''

if "execute_delegated_workforce_plan" not in main_text:
    marker = "from backend.app.runtime.outcome_action_execution_runtime import"
    idx = main_text.find(marker)

    if idx != -1:
        insert_at = main_text.find("\n", idx)
        main_text = (
            main_text[:insert_at + 1]
            + import_block
            + main_text[insert_at + 1:]
        )

route_block = r'''

@app.post("/delegated-workforce-execution")
async def delegated_workforce_execution(payload: dict):

    implementation_plan = payload.get("implementation_plan") or {}

    result = execute_delegated_workforce_plan(
        implementation_plan=implementation_plan,
        owner_approved=payload.get("owner_approved", False),
        client_owned_agents=payload.get("client_owned_agents", []),
        package_tier=payload.get("package_tier", "starter"),
    )

    return result
'''

if '/delegated-workforce-execution' not in main_text:
    main_text += route_block

main_file.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import (
    execute_delegated_workforce_plan,
)

sample_plan = {
    "action_packets": [
        {
            "packet_id": "packet_1",
            "recommended_agent": "security_compliance_agent",
            "approval_required": True,
            "risk_level": "high",
        },
        {
            "packet_id": "packet_2",
            "recommended_agent": "analytics_optimisation_agent",
            "approval_required": False,
            "risk_level": "medium",
        },
        {
            "packet_id": "packet_3",
            "recommended_agent": "lead_generator_appointment_setter_agent",
            "approval_required": False,
            "risk_level": "medium",
        },
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=sample_plan,
    owner_approved=True,
    client_owned_agents=[
        "analytics_optimisation_agent",
    ],
    package_tier="starter",
)

assert result["success"] is True
assert result["completed_count"] == 1
assert result["blocked_count"] == 2

blocked = result["blocked_results"][0]

assert blocked["delegate_execution"] == "blocked"
assert blocked["recommendation_visibility"] is True
assert blocked["upsell_visibility"] is True
assert blocked["execution_preview"] == "allowed"

completed = result["completed_results"][0]

assert completed["assigned_agent"] == "analytics_optimisation_agent"
assert completed["execution_status"] == "completed"

print("DELEGATED_WORKFORCE_EXECUTION_RUNTIME_TEST_PASSED")
print({
    "completed_count": result["completed_count"],
    "blocked_count": result["blocked_count"],
})
'''.lstrip(), encoding="utf-8")

print("DELEGATED_WORKFORCE_EXECUTION_RUNTIME_INSTALLED")
print(f"Backup: {backup}")
print(f"Created: {runtime}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")