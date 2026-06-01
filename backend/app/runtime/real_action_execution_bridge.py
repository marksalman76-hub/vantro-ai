
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.app.runtime.action_adapter_execution_layer import execute_action_adapter


HIGH_RISK_ACTION_KEYWORDS = {
    "spend",
    "budget",
    "scale",
    "launch_paid_campaign",
    "payment",
    "purchase",
    "contract",
    "hire",
    "fire",
    "delete",
    "publish_live",
    "send_bulk",
}


SAFE_ACTION_ADAPTERS = {
    "create_marketing_asset": "marketing_asset_adapter",
    "create_sales_asset": "sales_asset_adapter",
    "create_email_draft": "email_draft_adapter",
    "create_content_calendar": "content_calendar_adapter",
    "create_research_summary": "research_summary_adapter",
    "create_strategy_document": "strategy_document_adapter",
    "create_client_deliverable": "client_deliverable_adapter",
    "prepare_outreach_draft": "outreach_draft_adapter",
    "prepare_implementation_checklist": "implementation_checklist_adapter",
    "website_draft_page": "website_draft_page_adapter",
    "ads_campaign_draft": "ads_campaign_draft_adapter",
    "seo_content_plan": "seo_deliverable_adapter",
    "store_draft_update": "store_draft_update_adapter",
    "product_copywriting": "product_copywriting_adapter",
    "ugc_creative_deliverable": "ugc_creative_deliverable_adapter",
}



def _extract_primary_creative_deliverable(packet: dict, result: dict) -> str:
    """
    Prefer the actual agent deliverable over generic operational proof text.
    This is for text/creative agents where the client/admin needs the finished work,
    not only an execution receipt.
    """
    candidates = [
        result.get("completed_output"),
        result.get("generated_output"),
        result.get("output"),
        result.get("deliverable"),
        result.get("content"),
        result.get("body"),
        packet.get("completed_output"),
        packet.get("generated_output"),
        packet.get("output"),
        packet.get("deliverable"),
        packet.get("content"),
        packet.get("body"),
        packet.get("user_requested_task"),
    ]

    for value in candidates:
        if isinstance(value, dict):
            for key in ("body", "content", "summary", "text", "output"):
                nested = value.get(key)
                if isinstance(nested, str) and nested.strip():
                    return nested.strip()

        if isinstance(value, str) and value.strip():
            text = value.strip()
            if text.lower() not in {
                "created operational execution task.",
                "operational task created",
                "autonomous execution processed.",
            }:
                return text

    return ""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _contains_high_risk_action(packet: Dict[str, Any]) -> bool:
    text = " ".join(
        str(packet.get(k, ""))
        for k in [
            "action",
            "implementation_action",
            "title",
            "description",
            "task",
            "agent",
            "assigned_agent",
        ]
    ).lower()
    return any(keyword in text for keyword in HIGH_RISK_ACTION_KEYWORDS)


def _normalise_action_type(packet: Dict[str, Any]) -> str:
    raw = " ".join(
        str(packet.get(k, ""))
        for k in [
            "action_type",
            "implementation_action",
            "action",
            "title",
            "description",
            "user_requested_task",
            "recommended_agent",
            "assigned_agent",
        ]
    ).lower().replace("_", " ")

    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip().lower()

    if "website draft page" in raw or "landing page" in raw or assigned_agent == "website_landing_apps_agent":
        return "website_draft_page"

    if "ads campaign draft" in raw or "meta ads" in raw or "google ads" in raw or assigned_agent == "paid_ads_agent":
        return "ads_campaign_draft"

    if "seo content plan" in raw or "seo title" in raw or "meta description" in raw or assigned_agent == "seo_agent":
        return "seo_content_plan"

    if "store draft update" in raw or "shopify" in raw or assigned_agent in {"store_builder_agent", "ecommerce_agent"}:
        return "store_draft_update"

    if (
        assigned_agent == "ugc_creative_agent"
        or "ugc" in raw
        or "creator" in raw
        or "shot-by-shot" in raw
        or "video concept" in raw
        or "media generation" in raw
        or "ugc script" in raw
    ):
        return "ugc_creative_deliverable"

    if "product description" in raw or "product copy" in raw or assigned_agent == "product_copywriting_agent":
        return "product_copywriting"

    if "email" in raw:
        return "create_email_draft"
    if "calendar" in raw or "content" in raw:
        return "create_content_calendar"
    if "sales" in raw or "pitch" in raw or "proposal" in raw:
        return "create_sales_asset"
    if "outreach" in raw or "influencer" in raw:
        return "prepare_outreach_draft"
    if "checklist" in raw or "execution plan" in raw or "concrete steps" in raw:
        return "prepare_implementation_checklist"
    if "research" in raw or "market" in raw or "competitor" in raw:
        return "create_research_summary"
    if "strategy" in raw or "positioning" in raw:
        return "create_strategy_document"

    return "create_client_deliverable"


def execute_real_action_packet(
    packet: Dict[str, Any],
    actor_role: str = "owner_admin",
    owner_approved: bool = False,
    tenant_id: str = "owner-admin",
    connected_integrations: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Converts an approved implementation packet into a real executable action result.

    This bridge performs safe internal actions immediately.
    High-risk actions are blocked until owner approval.
    External live provider/API calls remain adapter-gated.
    """

    action_type = _normalise_action_type(packet)
    high_risk = _contains_high_risk_action(packet)

    execution_id = f"real_action_{uuid4().hex[:12]}"
    assigned_agent = packet.get("assigned_agent") or packet.get("agent") or "specialist_agent"
    source_packet_id = packet.get("packet_id") or packet.get("id") or packet.get("action_packet_id")

    if high_risk and not owner_approved:
        return {
            "success": False,
            "execution_id": execution_id,
            "tenant_id": tenant_id,
            "source_packet_id": source_packet_id,
            "assigned_agent": assigned_agent,
            "action_type": action_type,
            "execution_status": "blocked_owner_approval_required",
            "performed_actual_action": False,
            "owner_approval_required": True,
            "customer_safe_message": "This action requires owner approval before execution.",
            "created_at": _now(),
        }

    adapter = SAFE_ACTION_ADAPTERS.get(action_type, "client_deliverable_adapter")

    implementation_action = (
        packet.get("user_requested_task")
        or packet.get("implementation_action")
        or packet.get("action")
        or packet.get("description")
        or packet.get("title")
        or "Approved implementation task"
    )

    adapter_execution = execute_action_adapter(
        {
            **packet,
            "assigned_agent": assigned_agent,
            "implementation_action": implementation_action,
            "action_type": action_type,
            "execution_adapter_target": adapter,
        },
        tenant_id=tenant_id,
        connected_integrations=connected_integrations or [],
        owner_approved=owner_approved,
    )

    if adapter_execution.get("owner_approval_required") and not owner_approved:
        return {
            "success": True,
            "execution_id": execution_id,
            "tenant_id": tenant_id,
            "source_packet_id": source_packet_id,
            "assigned_agent": assigned_agent,
            "action_type": action_type,
            "adapter": adapter_execution.get("adapter", adapter),
            "execution_status": "blocked_owner_approval_required",
            "performed_actual_action": False,
            "owner_approval_required": True,
            "external_provider_called": False,
            "credential_values_exposed": False,
            "customer_safe_message": adapter_execution.get("output"),
            "actions_performed": adapter_execution.get("actions_performed", []),
            "created_at": _now(),
        }

    adapter_asset = adapter_execution.get("asset") or {}
    preview_url = adapter_execution.get("preview_url") or adapter_execution.get("asset_url") or adapter_execution.get("media_url") or adapter_asset.get("preview_url") or adapter_asset.get("asset_url") or ""
    asset_url = adapter_execution.get("asset_url") or adapter_execution.get("media_url") or adapter_asset.get("asset_url") or preview_url
    media_url = adapter_execution.get("media_url") or asset_url
    generated_files = adapter_execution.get("generated_files") or adapter_asset.get("generated_files") or []

    deliverable = {
        "deliverable_id": f"deliverable_{uuid4().hex[:12]}",
        "type": action_type,
        "title": f"Executed: {str(implementation_action)[:90]}",
        "summary": adapter_execution.get("output") or str(implementation_action),
        "created_by_agent": assigned_agent,
        "customer_safe": True,
        "asset_status": adapter_asset.get("status", "created"),
        "download_ready": adapter_asset.get("download_ready", False),
        "preview_ready": adapter_asset.get("preview_ready", True),
        "preview_url": preview_url,
        "asset_url": asset_url,
        "media_url": media_url,
        "generated_files": generated_files,
        "actions_performed": adapter_execution.get("actions_performed", []),
        "adapter": adapter_execution.get("adapter"),
        "asset": {
            **adapter_asset,
            "preview_url": preview_url,
            "asset_url": asset_url,
            "media_url": media_url,
            "generated_files": generated_files,
        },
        "content": {
            "headline": f"{assigned_agent} executed an operational adapter.",
            "body": adapter_execution.get("output") or str(implementation_action),
            "next_step": "Review the created operational actions, then approve client delivery or request amendment.",
        },
    }

    return {
        "success": True,
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "source_packet_id": source_packet_id,
        "assigned_agent": assigned_agent,
        "action_type": action_type,
        "adapter": adapter_execution.get("adapter", adapter),
        "execution_status": adapter_execution.get("execution_status", "adapter_action_executed"),
        "performed_actual_action": adapter_execution.get("performed_actual_action", True),
        "owner_approval_required": adapter_execution.get("owner_approval_required", False),
        "external_provider_called": adapter_execution.get("external_provider_called", False),
        "credential_values_exposed": False,
        "customer_safe_message": adapter_execution.get("output"),
        "preview_url": preview_url,
        "asset_url": asset_url,
        "media_url": media_url,
        "generated_files": generated_files,
        "actions_performed": adapter_execution.get("actions_performed", []),
        "deliverable": deliverable,
        "created_at": _now(),
    }


def execute_real_action_packets(
    packets: List[Dict[str, Any]],
    actor_role: str = "owner_admin",
    owner_approved: bool = False,
    tenant_id: str = "owner-admin",
) -> Dict[str, Any]:
    results = [
        execute_real_action_packet(
            packet=p,
            actor_role=actor_role,
            owner_approved=owner_approved,
            tenant_id=tenant_id,
        )
        for p in packets
    ]

    return {
        "success": True,
        "tenant_id": tenant_id,
        "total_packets": len(packets),
        "executed_count": sum(1 for r in results if r.get("performed_actual_action")),
        "blocked_count": sum(1 for r in results if r.get("execution_status") == "blocked_owner_approval_required"),
        "results": results,
        "created_at": _now(),
    }
