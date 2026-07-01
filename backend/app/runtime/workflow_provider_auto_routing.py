from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid

DATA_DIR = Path("data") / "workflow_provider_routing"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ROUTING_EVENTS = DATA_DIR / "workflow_provider_routing_events.jsonl"
ROUTING_DECISIONS = DATA_DIR / "workflow_provider_routing_decisions.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({
                "record_type": "corrupt_jsonl_line",
                "raw": line,
                "loaded_at": _now(),
            })
    return rows


HIGH_RISK_ACTIONS = {
    "increase_ad_spend",
    "scale_campaign",
    "change_budget",
    "approve_contract",
    "sign_contract",
    "financial_commitment",
    "publish_paid_campaign",
}


PROVIDER_MAP = {
    "email": ["gmail", "sendgrid", "mailgun"],
    "crm": ["ghl", "hubspot", "salesforce"],
    "ecommerce": ["shopify", "woocommerce"],
    "calendar": ["google_calendar"],
    "analytics": ["google_analytics", "meta_ads"],
    "ads": ["meta_ads", "google_ads"],
    "content": ["openai", "anthropic"],
    "image": ["openai_image", "replicate"],
    "video": ["heygen", "runway", "kling"],
    "workflow": ["make", "zapier"],
}


def workflow_provider_routing_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "workflow_provider_auto_routing",
        "routing_events_path": str(ROUTING_EVENTS),
        "routing_decisions_path": str(ROUTING_DECISIONS),
        "provider_map_count": len(PROVIDER_MAP),
        "high_risk_action_gate_enabled": True,
        "owner_approval_required_for_spend_scaling_contracts": True,
        "governance_preserved": True,
        "entitlement_isolation_preserved": True,
        "customer_safe_ui_required": True,
        "white_label_ready": True,
    }


def classify_workflow_provider_category(action_type: str, workflow_payload: Optional[Dict[str, Any]] = None) -> str:
    payload = workflow_payload or {}
    raw = " ".join([
        str(action_type or ""),
        str(payload.get("provider_category", "")),
        str(payload.get("provider", "")),
        str(payload.get("channel", "")),
        str(payload.get("task", "")),
    ]).lower()

    if any(k in raw for k in ["email", "reply", "inbox", "sendgrid", "gmail"]):
        return "email"
    if any(k in raw for k in ["crm", "lead", "opportunity", "contact", "ghl", "hubspot"]):
        return "crm"
    if any(k in raw for k in ["shopify", "woocommerce", "product", "order", "store"]):
        return "ecommerce"
    if any(k in raw for k in ["calendar", "appointment", "booking", "meeting"]):
        return "calendar"
    if any(k in raw for k in ["analytics", "report", "ga4", "google_analytics"]):
        return "analytics"
    if any(k in raw for k in ["ad", "campaign", "meta", "google_ads", "budget", "spend"]):
        return "ads"
    if any(k in raw for k in ["image", "photo", "product picture"]):
        return "image"
    if any(k in raw for k in ["video", "ugc", "avatar", "heygen", "runway", "kling"]):
        return "video"
    if any(k in raw for k in ["make", "zapier", "webhook", "automation"]):
        return "workflow"
    return "content"


def requires_owner_approval(action_type: str, workflow_payload: Optional[Dict[str, Any]] = None) -> bool:
    payload = workflow_payload or {}
    raw = " ".join([
        str(action_type or ""),
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
    ]).lower()
    return any(risk in raw for risk in HIGH_RISK_ACTIONS)


def select_provider_for_workflow(
    *,
    tenant_id: str,
    workflow_id: str,
    agent_id: str,
    action_type: str,
    workflow_payload: Optional[Dict[str, Any]] = None,
    available_providers: Optional[List[str]] = None,
    entitlement_active: bool = True,
) -> Dict[str, Any]:
    workflow_payload = workflow_payload or {}
    category = classify_workflow_provider_category(action_type, workflow_payload)
    candidates = PROVIDER_MAP.get(category, PROVIDER_MAP["content"])
    available = available_providers or candidates
    selected = next((p for p in candidates if p in available), available[0] if available else None)
    owner_approval_required = requires_owner_approval(action_type, workflow_payload)

    if not entitlement_active:
        status = "blocked"
        route_state = "entitlement_inactive"
        selected = None
    elif owner_approval_required:
        status = "pending_owner_approval"
        route_state = "approval_required_before_provider_execution"
    elif selected:
        status = "routed"
        route_state = "ready_for_provider_execution"
    else:
        status = "manual_review_required"
        route_state = "no_available_provider"

    decision = {
        "routing_id": f"route_{uuid.uuid4().hex[:16]}",
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "agent_id": agent_id,
        "action_type": action_type,
        "provider_category": category,
        "candidate_providers": candidates,
        "available_providers": available,
        "selected_provider": selected,
        "status": status,
        "route_state": route_state,
        "owner_approval_required": owner_approval_required,
        "entitlement_active": entitlement_active,
        "created_at": _now(),
        "governance_preserved": True,
        "customer_safe_status": "Prepared route" if status == "routed" else "Needs review",
        "no_autonomous_spend_or_scaling": True,
    }

    _append_jsonl(ROUTING_DECISIONS, decision)
    _append_jsonl(ROUTING_EVENTS, {
        "event_id": f"routing_event_{uuid.uuid4().hex[:16]}",
        "event_type": "workflow_provider_route_decided",
        "routing_id": decision["routing_id"],
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "agent_id": agent_id,
        "status": status,
        "selected_provider": selected,
        "created_at": _now(),
        "governance_preserved": True,
    })

    return decision


def route_workflow_to_provider_bridge(
    *,
    tenant_id: str,
    workflow_id: str,
    agent_id: str,
    action_type: str,
    workflow_payload: Optional[Dict[str, Any]] = None,
    available_providers: Optional[List[str]] = None,
    entitlement_active: bool = True,
) -> Dict[str, Any]:
    decision = select_provider_for_workflow(
        tenant_id=tenant_id,
        workflow_id=workflow_id,
        agent_id=agent_id,
        action_type=action_type,
        workflow_payload=workflow_payload,
        available_providers=available_providers,
        entitlement_active=entitlement_active,
    )

    provider_execution_packet = {
        "routing_id": decision["routing_id"],
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "agent_id": agent_id,
        "action_type": action_type,
        "provider": decision["selected_provider"],
        "provider_category": decision["provider_category"],
        "payload": workflow_payload or {},
        "execution_allowed": decision["status"] == "routed",
        "owner_approval_required": decision["owner_approval_required"],
        "governance_preserved": True,
        "entitlement_active": entitlement_active,
        "no_autonomous_spend_or_scaling": True,
    }

    return {
        "status": decision["status"],
        "route_state": decision["route_state"],
        "routing_decision": decision,
        "provider_execution_packet": provider_execution_packet,
        "customer_safe_status": decision["customer_safe_status"],
        "governance_preserved": True,
    }


def list_workflow_provider_routes(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(ROUTING_DECISIONS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "routes": rows,
        "governance_preserved": True,
    }
