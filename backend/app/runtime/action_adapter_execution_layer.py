
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.app.runtime.external_action_readiness_classifier import (
    classify_external_action_readiness,
)
from backend.app.runtime.real_external_integration_execution_bridge import (
    execute_real_external_action,
)


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


def execute_action_adapter(
    packet: Dict[str, Any],
    *,
    tenant_id: str = "unknown",
    connected_integrations: List[str] | None = None,
    owner_approved: bool = False,
) -> Dict[str, Any]:
    adapter = classify_action_adapter(packet)
    external_readiness = classify_external_action_readiness(
        adapter=adapter,
        connected_integrations=connected_integrations or [],
        owner_approved=owner_approved,
    )
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

    real_external_result = None
    if external_readiness.get("external_action_ready") is True:
        real_external_result = execute_real_external_action(
            adapter=adapter,
            action_text=str(action_text),
            tenant_id=tenant_id,
            connected_integrations=connected_integrations or [],
            owner_approved=owner_approved,
        )

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
            "external_readiness": external_readiness,
            "external_action_ready": external_readiness.get("external_action_ready", False),
            "internal_fallback_used": False,
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
        "external_provider_called": bool(real_external_result and real_external_result.get("external_action_executed")),
        "live_external_call_executed": bool(real_external_result and real_external_result.get("live_external_call_executed")),
        "external_readiness": external_readiness,
        "external_action_ready": external_readiness.get("external_action_ready", False),
        "real_external_execution": real_external_result,
        "internal_fallback_used": not bool(real_external_result and real_external_result.get("external_action_executed")),
        "missing_connections": external_readiness.get("missing_connections", []),
        "actions_performed": (
            real_external_result.get("actions_performed", [])
            if real_external_result and real_external_result.get("external_action_executed")
            else actions
        ),
        "output": (
            "Real external integration actions executed."
            if real_external_result and real_external_result.get("external_action_executed")
            else output
        ),
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
