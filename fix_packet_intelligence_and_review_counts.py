from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
runtime = ROOT / "backend" / "app" / "runtime" / "outcome_action_execution_runtime.py"
admin = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
test = ROOT / "test_outcome_action_execution_runtime.py"

backup = ROOT / "backups" / f"packet_intelligence_review_counts_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(runtime, backup / "outcome_action_execution_runtime.py")
shutil.copy2(admin, backup / "admin_page.tsx")

runtime.write_text(r'''
from __future__ import annotations

import re
import time
import uuid
from typing import Any, Dict, List


def _now_ms() -> int:
    return int(time.time() * 1000)


SECTION_JUNK = {
    "executive summary",
    "business/industry context assumptions",
    "business context assumptions",
    "specific opportunity or problem diagnosis",
    "execution plan with concrete steps",
    "execution plan",
    "deliverables/assets/actions to create",
    "deliverables",
    "assets/actions to create",
    "kpis or measurable success criteria",
    "risks, constraints, and mitigations",
    "owner/admin review points",
    "immediate next actions",
}


ROUTING_RULES = [
    (["compliance", "regulatory", "risk", "hipaa", "gdpr", "security", "privacy", "audit"], "security_compliance_agent"),
    (["analytics", "data", "kpi", "metric", "interoperability", "dashboard", "reporting", "ai enablement"], "analytics_optimisation_agent"),
    (["lead", "outreach", "pilot client", "sales", "pipeline", "buyer persona", "cio", "prospect"], "lead_generator_appointment_setter_agent"),
    (["crm", "nurture", "follow up", "qualification", "pipeline management"], "crm_ai_agent"),
    (["webinar", "whitepaper", "thought leadership", "blog", "content calendar", "case study"], "social_media_manager_content_creator_agent"),
    (["brochure", "messaging", "go-to-market", "campaign", "marketing collateral"], "marketing_specialist_agent"),
    (["partnership", "vendor", "association", "alliance", "mou"], "business_growth_partnerships_agent"),
    (["website", "landing page", "portal", "app", "digital experience"], "website_landing_apps_agent"),
    (["seo", "search", "organic"], "seo_agent"),
]


def _clean_line(line: str) -> str:
    line = re.sub(r"^\s*[-•]+\s*", "", line.strip())
    line = re.sub(r"^\s*\d+\.\s*", "", line)
    line = line.replace("**", "").strip()
    return line


def _is_junk(line: str) -> bool:
    clean = _clean_line(line).lower().strip(":")
    if not clean:
        return True
    if clean in SECTION_JUNK:
        return True
    if len(clean) < 28:
        return True
    if re.match(r"^(step\s+\d+|opportunity\s+\d+)\s*:?\s*$", clean):
        return True
    if clean.endswith(":") and len(clean.split()) <= 7:
        return True
    return False


def _route_agent(text: str) -> str:
    lower = text.lower()
    for keywords, agent in ROUTING_RULES:
        if any(k in lower for k in keywords):
            return agent
    return "orchestration_agent"


def _risk_level(text: str) -> str:
    lower = text.lower()
    if any(term in lower for term in ["spend", "budget", "contract", "legal", "compliance", "security", "privacy", "payment", "regulatory", "risk"]):
        return "high"
    if any(term in lower for term in ["campaign", "outreach", "publish", "send", "crm", "lead", "sales", "partnership"]):
        return "medium"
    return "low"


def _extract_action_candidates(outcome_text: str) -> List[str]:
    lines = [_clean_line(line) for line in outcome_text.splitlines()]
    candidates: List[str] = []

    action_verbs = [
        "create", "develop", "launch", "build", "prepare", "identify", "review",
        "generate", "draft", "plan", "initiate", "assign", "schedule", "assemble",
        "conduct", "monitor", "evaluate", "establish", "train", "recruit", "design",
        "secure", "form", "select", "approach"
    ]

    for line in lines:
        if _is_junk(line):
            continue

        lower = line.lower()
        has_action = any(v in lower for v in action_verbs)
        has_domain = any(k in lower for k in [
            "compliance", "analytics", "lead", "crm", "webinar", "whitepaper",
            "campaign", "partnership", "sales", "pilot", "brochure", "training",
            "service", "market", "messaging", "data", "healthcare"
        ])

        if has_action or has_domain:
            candidates.append(line)

    deduped: List[str] = []
    seen = set()
    for item in candidates:
        key = item[:90].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[:12]


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

    if not candidates:
        candidates = [
            "Convert the approved outcome into a practical implementation checklist.",
            "Assign specialist agents to prepare the required deliverables.",
            "Prepare a client-safe implementation package for review.",
        ]

    action_packets = []
    for index, action in enumerate(candidates, start=1):
        recommended_agent = _route_agent(action)
        risk = _risk_level(action)
        approval_required = risk in {"medium", "high"}
        action_packets.append({
            "packet_id": f"action_packet_{uuid.uuid4().hex[:14]}",
            "sequence": index,
            "title": action[:180],
            "action": action,
            "recommended_agent": recommended_agent,
            "source_agent": source_agent,
            "risk_level": risk,
            "approval_required": approval_required,
            "owner_approved": bool(owner_approved) if approval_required else True,
            "execution_status": "ready_for_approval" if approval_required and not owner_approved else "ready_for_implementation_review",
            "external_action_performed": False,
            "live_external_call_executed": False,
            "customer_safe": True,
        })

    return {
        "success": True,
        "profile": "outcome_action_execution_plan_v2",
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
            "safe_auto_ready_count": sum(1 for p in action_packets if p["execution_status"] == "ready_for_implementation_review" and not p["approval_required"]),
        },
        "recommended_agent_summary": sorted(set(p["recommended_agent"] for p in action_packets)),
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

test.write_text(r'''
from backend.app.runtime.outcome_action_execution_runtime import create_outcome_action_plan

sample = """
4. Execution Plan with Concrete Steps
- Develop tailored value propositions and marketing materials for hospital CIOs.
- Create compliance framework outlines for HIPAA and GDPR.
- Launch targeted lead generation campaigns including webinars and whitepapers.
- Establish partnerships with healthcare technology vendors.
- Build KPI dashboard for sales pipeline and pilot engagement tracking.
5. Deliverables/Assets/Actions to Create
"""

plan = create_outcome_action_plan(
    outcome_text=sample,
    source_agent="marketing_specialist_agent",
    owner_approved=True,
)

agents = {p["recommended_agent"] for p in plan["action_packets"]}
titles = [p["title"] for p in plan["action_packets"]]

assert plan["success"] is True
assert plan["profile"] == "outcome_action_execution_plan_v2"
assert "security_compliance_agent" in agents
assert "lead_generator_appointment_setter_agent" in agents or "social_media_manager_content_creator_agent" in agents
assert "business_growth_partnerships_agent" in agents
assert "analytics_optimisation_agent" in agents
assert all("Execution Plan with Concrete Steps" not in t for t in titles)
assert all("Deliverables/Assets/Actions" not in t for t in titles)

print("OUTCOME_ACTION_EXECUTION_RUNTIME_V2_TEST_PASSED")
print({
    "action_count": plan["action_count"],
    "recommended_agents": sorted(agents),
})
'''.lstrip(), encoding="utf-8")

s = admin.read_text(encoding="utf-8")

# Fix metric cards by replacing the review centre display block patterns.
s = s.replace(
    '''<div><small>Live provider outputs</small><strong>0</strong></div>
                  <div><small>Dead-letter items</small><strong>0</strong></div>
                  <div><small>Manual review items</small><strong>0</strong></div>''',
    '''<div><small>Live provider outputs</small><strong>{runResult?.items?.length || 0}</strong></div>
                  <div><small>Implementation packets</small><strong>{latestImplementationPlan?.action_count || 0}</strong></div>
                  <div><small>Queued packets</small><strong>{queuedImplementationPackets.length}</strong></div>
                  <div><small>Completed runs</small><strong>{completedImplementationRuns.length}</strong></div>
                  <div><small>Manual review items</small><strong>{latestImplementationPlan?.approval_summary?.approval_required_count || 0}</strong></div>'''
)

# Broader fallback if exact block not found.
s = s.replace(
    '''<strong>0</strong></div>
                  <div><small>Dead-letter items</small><strong>0</strong></div>
                  <div><small>Manual review items</small><strong>0</strong>''',
    '''<strong>{runResult?.items?.length || 0}</strong></div>
                  <div><small>Implementation packets</small><strong>{latestImplementationPlan?.action_count || 0}</strong></div>
                  <div><small>Queued packets</small><strong>{queuedImplementationPackets.length}</strong></div>
                  <div><small>Completed runs</small><strong>{completedImplementationRuns.length}</strong></div>
                  <div><small>Manual review items</small><strong>{latestImplementationPlan?.approval_summary?.approval_required_count || 0}</strong>'''
)

admin.write_text(s, encoding="utf-8")

print("PACKET_INTELLIGENCE_AND_REVIEW_COUNTS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {runtime}")
print(f"Updated: {admin}")
print(f"Updated: {test}")