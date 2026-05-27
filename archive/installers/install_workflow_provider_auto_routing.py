from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

ROUTER = RUNTIME_DIR / "workflow_provider_auto_routing.py"
TEST_FILE = ROOT / "test_workflow_provider_auto_routing.py"
IMPORT_TEST = ROOT / "test_workflow_provider_auto_routing_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if not MAIN.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_workflow_provider_auto_routing_{ts}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

ROUTER.write_text(r'''
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
    "video": ["heygen", "runway", "higgsfield"],
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
    if any(k in raw for k in ["video", "ugc", "avatar", "heygen", "runway", "higgsfield"]):
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
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.workflow_provider_auto_routing import list_workflow_provider_routes, route_workflow_to_provider_bridge, workflow_provider_routing_readiness\n"
if import_line not in main_text:
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    insert_at = import_matches[-1].end() + 1 if import_matches else 0
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/workflow-provider-routing/readiness")
def admin_workflow_provider_routing_readiness():
    return workflow_provider_routing_readiness()


@app.post("/admin/workflow-provider-routing/route")
def admin_route_workflow_to_provider(payload: dict):
    return route_workflow_to_provider_bridge(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        workflow_id=str(payload.get("workflow_id", "workflow_unknown")),
        agent_id=str(payload.get("agent_id", "unknown_agent")),
        action_type=str(payload.get("action_type", "unknown_action")),
        workflow_payload=dict(payload.get("workflow_payload", {})),
        available_providers=list(payload.get("available_providers", [])) if payload.get("available_providers") is not None else None,
        entitlement_active=bool(payload.get("entitlement_active", True)),
    )


@app.get("/admin/workflow-provider-routing/list")
def admin_list_workflow_provider_routes(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_workflow_provider_routes(tenant_id=tenant_id, status=status, limit=limit)
'''

if "/admin/workflow-provider-routing/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.workflow_provider_auto_routing import (
    classify_workflow_provider_category,
    list_workflow_provider_routes,
    route_workflow_to_provider_bridge,
    workflow_provider_routing_readiness,
)


def main():
    readiness = workflow_provider_routing_readiness()
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True
    assert readiness["owner_approval_required_for_spend_scaling_contracts"] is True

    assert classify_workflow_provider_category("send_email", {"provider": "gmail"}) == "email"
    assert classify_workflow_provider_category("create_shopify_product", {"task": "product draft"}) == "ecommerce"
    assert classify_workflow_provider_category("generate_ugc_video", {"task": "ugc avatar"}) == "video"

    routed = route_workflow_to_provider_bridge(
        tenant_id="tenant_test",
        workflow_id="workflow_email_test",
        agent_id="email_reply_agent",
        action_type="send_email_draft",
        workflow_payload={"channel": "email", "task": "reply"},
        available_providers=["gmail"],
        entitlement_active=True,
    )
    assert routed["status"] == "routed"
    assert routed["provider_execution_packet"]["execution_allowed"] is True
    assert routed["provider_execution_packet"]["provider"] == "gmail"

    gated = route_workflow_to_provider_bridge(
        tenant_id="tenant_test",
        workflow_id="workflow_ads_test",
        agent_id="marketing_specialist_agent",
        action_type="scale_campaign",
        workflow_payload={"provider": "meta_ads", "change_budget": True},
        available_providers=["meta_ads"],
        entitlement_active=True,
    )
    assert gated["status"] == "pending_owner_approval"
    assert gated["provider_execution_packet"]["execution_allowed"] is False
    assert gated["provider_execution_packet"]["owner_approval_required"] is True

    blocked = route_workflow_to_provider_bridge(
        tenant_id="tenant_test",
        workflow_id="workflow_blocked_test",
        agent_id="crm_agent",
        action_type="create_crm_note",
        workflow_payload={"provider": "ghl"},
        available_providers=["ghl"],
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"
    assert blocked["provider_execution_packet"]["execution_allowed"] is False

    listed = list_workflow_provider_routes(tenant_id="tenant_test")
    assert listed["count"] >= 3

    print("WORKFLOW_PROVIDER_AUTO_ROUTING_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/workflow-provider-routing/readiness",
        "/admin/workflow-provider-routing/route",
        "/admin/workflow-provider-routing/list",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("WORKFLOW_PROVIDER_AUTO_ROUTING_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("WORKFLOW_PROVIDER_AUTO_ROUTING_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {ROUTER}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/workflow-provider-routing/readiness")
print("/admin/workflow-provider-routing/route")
print("/admin/workflow-provider-routing/list")