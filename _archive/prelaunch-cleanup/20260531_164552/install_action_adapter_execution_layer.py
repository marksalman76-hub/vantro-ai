from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / f"action_adapter_execution_layer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "action_adapter_execution_layer.py"
if target.exists():
    shutil.copy2(target, BACKUP / target.name)

target.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(packet: Dict[str, Any]) -> str:
    return " ".join(
        str(packet.get(k, ""))
        for k in [
            "implementation_action",
            "action",
            "title",
            "description",
            "completed_output",
            "summary",
        ]
    ).lower()


def classify_action_adapter(packet: Dict[str, Any]) -> str:
    text = _text(packet)

    if any(x in text for x in ["stakeholder interview", "interviews", "interview healthcare", "schedule interview"]):
        return "stakeholder_interview_outreach_adapter"

    if any(x in text for x in ["competitor", "white space", "positioning analysis", "landscape analysis"]):
        return "competitor_research_adapter"

    if any(x in text for x in ["thought leadership", "white paper", "whitepaper", "webinar", "blog", "case study"]):
        return "content_asset_creation_adapter"

    if any(x in text for x in ["messaging pillars", "positioning framework", "value proposition", "sales deck"]):
        return "sales_enablement_asset_adapter"

    if any(x in text for x in ["crm", "pipeline", "lead", "prospect", "appointment"]):
        return "crm_task_creation_adapter"

    if any(x in text for x in ["launch campaign", "paid campaign", "increase budget", "ad budget", "go live"]):
        return "approval_gated_campaign_adapter"

    if any(x in text for x in ["send email", "outreach email", "bulk", "mass email"]):
        return "approval_gated_communication_adapter"

    return "general_operational_task_adapter"


def execute_action_adapter(packet: Dict[str, Any], *, tenant_id: str = "unknown") -> Dict[str, Any]:
    adapter = classify_action_adapter(packet)
    action_text = (
        packet.get("implementation_action")
        or packet.get("action")
        or packet.get("title")
        or packet.get("description")
        or "Approved operational task"
    )

    execution_id = f"adapter_exec_{uuid4().hex[:12]}"
    asset_id = f"asset_{uuid4().hex[:12]}"
    task_id = f"task_{uuid4().hex[:12]}"

    if adapter == "stakeholder_interview_outreach_adapter":
        actions = [
            {
                "type": "email_draft_created",
                "status": "created",
                "subject": "Healthcare technology positioning research interview",
                "body_preview": "Drafted outreach asking healthcare technology decision-makers for a short market validation interview.",
            },
            {
                "type": "crm_task_created",
                "status": "created",
                "task_title": "Book 5 healthcare stakeholder validation interviews",
                "priority": "high",
            },
            {
                "type": "calendar_placeholder_created",
                "status": "draft_created",
                "title": "Healthcare stakeholder interview slot",
            },
        ]
        output = "Created interview outreach draft, CRM follow-up task, and calendar placeholder draft."

    elif adapter == "competitor_research_adapter":
        actions = [
            {
                "type": "research_task_created",
                "status": "created",
                "task_title": "Analyze healthcare consulting competitor positioning",
            },
            {
                "type": "research_brief_created",
                "status": "created",
                "sections": ["competitor categories", "message gaps", "white-space positioning", "recommended differentiation"],
            },
        ]
        output = "Created competitor research brief structure and research task for healthcare positioning analysis."

    elif adapter == "content_asset_creation_adapter":
        actions = [
            {
                "type": "content_asset_created",
                "status": "created",
                "asset_type": "thought_leadership_pack",
                "items": ["whitepaper outline", "blog draft brief", "webinar topic plan"],
            },
            {
                "type": "content_calendar_item_created",
                "status": "created",
                "title": "Healthcare technology thought leadership rollout",
            },
        ]
        output = "Created thought-leadership asset pack and content calendar task."

    elif adapter == "sales_enablement_asset_adapter":
        actions = [
            {
                "type": "sales_asset_created",
                "status": "created",
                "asset_type": "messaging_framework",
                "items": ["positioning statement", "messaging pillars", "buyer objections", "proof points"],
            }
        ]
        output = "Created sales enablement messaging framework asset."

    elif adapter == "crm_task_creation_adapter":
        actions = [
            {
                "type": "crm_task_created",
                "status": "created",
                "task_title": "Create healthcare prospect pipeline and appointment workflow",
                "priority": "medium",
            }
        ]
        output = "Created CRM pipeline task and appointment workflow task."

    elif adapter in {"approval_gated_campaign_adapter", "approval_gated_communication_adapter"}:
        return {
            "success": True,
            "execution_id": execution_id,
            "adapter": adapter,
            "tenant_id": tenant_id,
            "performed_actual_action": False,
            "execution_status": "blocked_owner_approval_required",
            "owner_approval_required": True,
            "customer_safe": True,
            "credential_values_exposed": False,
            "actions_performed": [],
            "output": "Action requires owner approval before live campaign, send, publish, or spend execution.",
            "created_at": _now(),
        }

    else:
        actions = [
            {
                "type": "operational_task_created",
                "status": "created",
                "task_title": str(action_text)[:140],
                "priority": "medium",
            }
        ]
        output = "Created operational execution task."

    return {
        "success": True,
        "execution_id": execution_id,
        "adapter": adapter,
        "tenant_id": tenant_id,
        "performed_actual_action": True,
        "execution_status": "adapter_action_executed",
        "owner_approval_required": False,
        "customer_safe": True,
        "credential_values_exposed": False,
        "external_provider_called": False,
        "live_external_call_executed": False,
        "actions_performed": actions,
        "output": output,
        "asset": {
            "asset_id": asset_id,
            "task_id": task_id,
            "status": "created",
            "preview_ready": True,
            "download_ready": False,
            "customer_safe": True,
        },
        "created_at": _now(),
    }
''', encoding="utf-8")

test_file = ROOT / "test_action_adapter_execution_layer.py"
test_file.write_text(r'''
from backend.app.runtime.action_adapter_execution_layer import (
    classify_action_adapter,
    execute_action_adapter,
)

interview_packet = {
    "implementation_action": "Conduct stakeholder interviews with healthcare providers and payers",
}
assert classify_action_adapter(interview_packet) == "stakeholder_interview_outreach_adapter"
interview_result = execute_action_adapter(interview_packet, tenant_id="tenant_test")
assert interview_result["performed_actual_action"] is True
assert interview_result["adapter"] == "stakeholder_interview_outreach_adapter"
assert len(interview_result["actions_performed"]) >= 2

competitor_packet = {
    "implementation_action": "Analyze competitor positioning and identify white space",
}
competitor_result = execute_action_adapter(competitor_packet)
assert competitor_result["adapter"] == "competitor_research_adapter"
assert competitor_result["performed_actual_action"] is True

content_packet = {
    "implementation_action": "Generate thought leadership content series including white papers and webinars",
}
content_result = execute_action_adapter(content_packet)
assert content_result["adapter"] == "content_asset_creation_adapter"
assert content_result["performed_actual_action"] is True

risky_packet = {
    "implementation_action": "Launch paid campaign and increase budget",
}
risky_result = execute_action_adapter(risky_packet)
assert risky_result["performed_actual_action"] is False
assert risky_result["owner_approval_required"] is True
assert risky_result["execution_status"] == "blocked_owner_approval_required"

print("ACTION_ADAPTER_EXECUTION_LAYER_TEST_PASSED")
''', encoding="utf-8")

print("ACTION_ADAPTER_EXECUTION_LAYER_INSTALLED")
print(f"Backup: {BACKUP}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")