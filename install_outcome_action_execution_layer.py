from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime = ROOT / "backend" / "app" / "runtime" / "outcome_action_execution_runtime.py"
main = ROOT / "backend" / "app" / "main.py"
test = ROOT / "test_outcome_action_execution_runtime.py"

backup = ROOT / "backups" / f"outcome_action_execution_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(main, backup / "main.py")

runtime.write_text(r'''
from __future__ import annotations

import re
import time
import uuid
from typing import Any, Dict, List


def _now_ms() -> int:
    return int(time.time() * 1000)


AGENT_ROUTING = {
    "marketing": "marketing_specialist_agent",
    "campaign": "marketing_specialist_agent",
    "content": "social_media_manager_content_creator_agent",
    "seo": "seo_agent",
    "email": "email_reply_agent",
    "crm": "crm_ai_agent",
    "landing": "website_landing_apps_agent",
    "website": "website_landing_apps_agent",
    "analytics": "analytics_optimisation_agent",
    "compliance": "security_compliance_agent",
    "cyber": "security_compliance_agent",
    "partnership": "business_growth_partnerships_agent",
    "sales": "lead_generator_appointment_setter_agent",
    "lead": "lead_generator_appointment_setter_agent",
    "asset": "product_image_agent",
    "image": "product_image_agent",
    "creative": "ad_creative_agent",
}


def _route_agent(text: str) -> str:
    lower = text.lower()
    for keyword, agent in AGENT_ROUTING.items():
        if keyword in lower:
            return agent
    return "orchestration_agent"


def _risk_level(text: str) -> str:
    lower = text.lower()
    high_terms = ["spend", "budget", "contract", "legal", "compliance", "security", "client data", "payment", "stripe"]
    medium_terms = ["campaign", "outreach", "publish", "send", "crm", "lead", "sales"]
    if any(term in lower for term in high_terms):
        return "high"
    if any(term in lower for term in medium_terms):
        return "medium"
    return "low"


def _extract_action_candidates(outcome_text: str) -> List[str]:
    lines = [line.strip(" -•\t") for line in outcome_text.splitlines()]
    candidates = []
    capture = False

    for line in lines:
        if not line:
            continue
        lower = line.lower()

        if any(key in lower for key in [
            "immediate next actions",
            "execution plan",
            "deliverables",
            "assets",
            "actions to create",
            "next steps",
        ]):
            capture = True
            continue

        if capture and (
            re.match(r"^[a-z]\.", lower) or
            re.match(r"^\d+\.", lower) or
            line.startswith("-") or
            len(line) > 35
        ):
            candidates.append(line)

    if not candidates:
        for line in lines:
            if len(line) > 45 and any(v in line.lower() for v in ["create", "develop", "launch", "build", "prepare", "identify", "review", "generate"]):
                candidates.append(line)

    return candidates[:12]


def create_outcome_action_plan(
    *,
    outcome_text: str,
    source_agent: str,
    tenant_id: str = "owner_admin",
    project_id: str = "outcome_action_execution",
    owner_approved: bool = False,
) -> Dict[str, Any]:
    plan_id = f"outcome_plan_{uuid.uuid4().hex[:14]}"
    candidates = _extract_action_candidates(outcome_text)

    action_packets = []
    for index, action in enumerate(candidates, start=1):
        risk = _risk_level(action)
        approval_required = risk in {"medium", "high"}
        packet = {
            "packet_id": f"action_packet_{uuid.uuid4().hex[:14]}",
            "sequence": index,
            "title": action[:120],
            "action": action,
            "recommended_agent": _route_agent(action),
            "risk_level": risk,
            "approval_required": approval_required,
            "owner_approved": bool(owner_approved) if approval_required else True,
            "execution_status": "ready_for_approval" if approval_required and not owner_approved else "ready_for_safe_execution",
            "external_action_performed": False,
            "live_external_call_executed": False,
            "customer_safe": True,
        }
        action_packets.append(packet)

    return {
        "success": True,
        "profile": "outcome_action_execution_plan_v1",
        "plan_id": plan_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "source_agent": source_agent,
        "action_count": len(action_packets),
        "action_packets": action_packets,
        "execution_graph": [
            {
                "from": source_agent,
                "to": packet["recommended_agent"],
                "action_packet_id": packet["packet_id"],
                "status": packet["execution_status"],
            }
            for packet in action_packets
        ],
        "approval_summary": {
            "requires_owner_approval": any(p["approval_required"] and not p["owner_approved"] for p in action_packets),
            "approval_required_count": sum(1 for p in action_packets if p["approval_required"]),
            "safe_auto_ready_count": sum(1 for p in action_packets if p["execution_status"] == "ready_for_safe_execution"),
        },
        "customer_safe": True,
        "credential_values_exposed": False,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "created_at_ms": _now_ms(),
    }


def mark_outcome_plan_decision(plan: Dict[str, Any], decision: str, amendment_note: str = "") -> Dict[str, Any]:
    decision = decision.lower().strip()
    if decision not in {"approved", "rejected", "amendment_requested"}:
        decision = "amendment_requested"

    return {
        "success": True,
        "profile": "outcome_plan_decision_v1",
        "plan_id": plan.get("plan_id"),
        "decision": decision,
        "amendment_note": amendment_note,
        "next_stage": {
            "approved": "implementation_queue_ready",
            "rejected": "workflow_closed_rejected",
            "amendment_requested": "revision_required",
        }[decision],
        "customer_safe": True,
        "external_action_performed": False,
        "live_external_call_executed": False,
        "credential_values_exposed": False,
        "decided_at_ms": _now_ms(),
    }
'''.lstrip(), encoding="utf-8")

m = main.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.outcome_action_execution_runtime import create_outcome_action_plan, mark_outcome_plan_decision\n"
if import_line not in m:
    first_import = m.find("from ")
    if first_import == -1:
        raise SystemExit("Import anchor not found")
    m = m[:first_import] + import_line + m[first_import:]

routes = r'''

@app.post("/admin/outcome-action-plan")
async def admin_outcome_action_plan(payload: dict):
    return create_outcome_action_plan(
        outcome_text=str(payload.get("outcome_text") or ""),
        source_agent=str(payload.get("source_agent") or "unknown_agent"),
        tenant_id=str(payload.get("tenant_id") or "owner_admin"),
        project_id=str(payload.get("project_id") or "outcome_action_execution"),
        owner_approved=bool(payload.get("owner_approved") or False),
    )


@app.post("/admin/outcome-action-decision")
async def admin_outcome_action_decision(payload: dict):
    return mark_outcome_plan_decision(
        plan=dict(payload.get("plan") or {}),
        decision=str(payload.get("decision") or "amendment_requested"),
        amendment_note=str(payload.get("amendment_note") or ""),
    )
'''

if '"/admin/outcome-action-plan"' not in m:
    m = m.rstrip() + "\n" + routes + "\n"

main.write_text(m, encoding="utf-8")

test.write_text(r'''
from backend.app.runtime.outcome_action_execution_runtime import create_outcome_action_plan, mark_outcome_plan_decision

sample = """
Immediate next actions
- Create a healthcare technology market research report.
- Develop a compliance checklist for healthcare client onboarding.
- Launch a lead generation campaign targeting healthcare CIOs.
- Prepare a CRM pipeline for pilot opportunities.
"""

plan = create_outcome_action_plan(
    outcome_text=sample,
    source_agent="marketing_specialist_agent",
    owner_approved=False,
)

assert plan["success"] is True
assert plan["action_count"] >= 3
assert plan["approval_summary"]["approval_required_count"] >= 1
assert plan["customer_safe"] is True
assert plan["credential_values_exposed"] is False
assert plan["external_action_performed"] is False

decision = mark_outcome_plan_decision(plan, "approved")
assert decision["success"] is True
assert decision["next_stage"] == "implementation_queue_ready"

print("OUTCOME_ACTION_EXECUTION_RUNTIME_TEST_PASSED")
print({
    "action_count": plan["action_count"],
    "approval_required_count": plan["approval_summary"]["approval_required_count"],
    "safe_auto_ready_count": plan["approval_summary"]["safe_auto_ready_count"],
    "decision_next_stage": decision["next_stage"],
})
'''.lstrip(), encoding="utf-8")

print("OUTCOME_ACTION_EXECUTION_LAYER_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {runtime}")
print(f"Updated: {main}")
print(f"Created: {test}")