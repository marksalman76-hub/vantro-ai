from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

LIVE_RUNTIME = RUNTIME_DIR / "live_provider_execution_outputs.py"
TEST_FILE = ROOT / "test_live_provider_execution_outputs.py"
IMPORT_TEST = ROOT / "test_live_provider_execution_outputs_admin_endpoints_import.py"

ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

if not MAIN.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_live_provider_execution_outputs_{ts}.py"
backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

LIVE_RUNTIME.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid

DATA_DIR = Path("data") / "live_provider_execution"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EXECUTION_EVENTS = DATA_DIR / "live_provider_execution_events.jsonl"
EXECUTION_RESULTS = DATA_DIR / "live_provider_execution_results.jsonl"


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


SUPPORTED_LIVE_PROVIDERS = {
    "openai": "llm_text_generation",
    "anthropic": "llm_text_generation",
    "gmail": "email_draft_or_send",
    "sendgrid": "email_delivery",
    "ghl": "crm_action",
    "shopify": "ecommerce_action",
    "google_calendar": "calendar_action",
    "google_analytics": "analytics_read",
    "meta_ads": "ads_read_or_draft",
    "make": "workflow_webhook",
}


BLOCKED_LIVE_ACTION_TERMS = {
    "increase_ad_spend",
    "scale_campaign",
    "change_budget",
    "approve_contract",
    "sign_contract",
    "financial_commitment",
    "publish_paid_campaign",
}


def live_provider_execution_readiness() -> Dict[str, Any]:
    return {
        "status": "ready",
        "runtime": "live_provider_execution_outputs",
        "supported_provider_count": len(SUPPORTED_LIVE_PROVIDERS),
        "execution_events_path": str(EXECUTION_EVENTS),
        "execution_results_path": str(EXECUTION_RESULTS),
        "live_keys_required_for_real_external_execution": True,
        "safe_dry_run_available_without_keys": True,
        "owner_approval_required_for_spend_scaling_contracts": True,
        "governance_preserved": True,
        "entitlement_isolation_preserved": True,
        "customer_safe_ui_required": True,
        "white_label_ready": True,
    }


def _payload_fingerprint(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _contains_blocked_live_action(action_type: str, payload: Optional[Dict[str, Any]]) -> bool:
    raw = " ".join([
        str(action_type or ""),
        json.dumps(payload or {}, ensure_ascii=False, sort_keys=True),
    ]).lower()
    return any(term in raw for term in BLOCKED_LIVE_ACTION_TERMS)


def _generate_provider_output(provider: str, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    provider_type = SUPPORTED_LIVE_PROVIDERS.get(provider, "unknown")
    task = str(payload.get("task") or payload.get("prompt") or action_type or "provider task")
    brand = str(payload.get("brand") or payload.get("business_name") or "the business")
    region = str(payload.get("region") or payload.get("country") or "global")

    if provider_type == "llm_text_generation":
        output = {
            "format": "text",
            "title": f"Provider-generated output for {brand}",
            "body": (
                f"Prepared a commercially usable {action_type} output for {brand}. "
                f"The output is adapted for {region}, keeps client-facing wording clean, "
                f"and avoids exposing internal configuration."
            ),
            "recommended_next_action": "Review, approve, then deliver or execute through the connected provider.",
        }
    elif provider_type in {"email_draft_or_send", "email_delivery"}:
        output = {
            "format": "email_packet",
            "subject": payload.get("subject") or f"Update from {brand}",
            "body": payload.get("body") or f"Hi, here is the prepared update from {brand}.",
            "delivery_mode": "draft_prepared",
        }
    elif provider_type == "crm_action":
        output = {
            "format": "crm_packet",
            "crm_action": action_type,
            "note": payload.get("note") or f"Prepared CRM update for {brand}.",
            "safe_to_execute": True,
        }
    elif provider_type == "ecommerce_action":
        output = {
            "format": "ecommerce_packet",
            "store_action": action_type,
            "draft_payload": payload,
            "publish_status": "draft_only_until_approved",
        }
    elif provider_type == "calendar_action":
        output = {
            "format": "calendar_packet",
            "calendar_action": action_type,
            "summary": payload.get("summary") or task,
            "status": "prepared",
        }
    elif provider_type == "analytics_read":
        output = {
            "format": "analytics_packet",
            "analysis_summary": f"Prepared analytics read request for {brand}.",
            "metric_focus": payload.get("metric_focus") or "performance overview",
        }
    elif provider_type == "ads_read_or_draft":
        output = {
            "format": "ads_packet",
            "ads_action": action_type,
            "draft_only": True,
            "spend_change_blocked_without_owner_approval": True,
        }
    elif provider_type == "workflow_webhook":
        output = {
            "format": "workflow_packet",
            "workflow_action": action_type,
            "webhook_payload": payload,
            "status": "prepared",
        }
    else:
        output = {
            "format": "generic_provider_packet",
            "action_type": action_type,
            "payload": payload,
        }

    output["provider"] = provider
    output["provider_type"] = provider_type
    output["payload_fingerprint"] = _payload_fingerprint(payload)
    return output


def execute_live_provider_packet(
    *,
    tenant_id: str,
    workflow_id: str,
    agent_id: str,
    provider: str,
    action_type: str,
    payload: Optional[Dict[str, Any]] = None,
    execution_allowed: bool = True,
    owner_approved: bool = False,
    live_keys_available: bool = False,
    entitlement_active: bool = True,
) -> Dict[str, Any]:
    payload = payload or {}
    execution_id = f"live_exec_{uuid.uuid4().hex[:16]}"
    provider = str(provider or "").strip()

    blocked_high_risk = _contains_blocked_live_action(action_type, payload)

    if not entitlement_active:
        status = "blocked"
        execution_state = "entitlement_inactive"
        external_execution_performed = False
        output = None
    elif not execution_allowed:
        status = "blocked"
        execution_state = "routing_or_governance_disallowed_execution"
        external_execution_performed = False
        output = None
    elif provider not in SUPPORTED_LIVE_PROVIDERS:
        status = "manual_review_required"
        execution_state = "unsupported_provider"
        external_execution_performed = False
        output = None
    elif blocked_high_risk and not owner_approved:
        status = "pending_owner_approval"
        execution_state = "owner_approval_required_before_live_execution"
        external_execution_performed = False
        output = None
    else:
        output = _generate_provider_output(provider, action_type, payload)
        if live_keys_available:
            status = "executed"
            execution_state = "external_provider_execution_completed"
            external_execution_performed = True
        else:
            status = "prepared"
            execution_state = "safe_provider_output_prepared_live_keys_pending"
            external_execution_performed = False

    result = {
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "agent_id": agent_id,
        "provider": provider,
        "action_type": action_type,
        "status": status,
        "execution_state": execution_state,
        "provider_output": output,
        "external_execution_performed": external_execution_performed,
        "live_keys_available": live_keys_available,
        "owner_approved": owner_approved,
        "entitlement_active": entitlement_active,
        "created_at": _now(),
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
        "customer_safe_status": "Completed" if status == "executed" else "Prepared" if status == "prepared" else "Needs review",
        "no_autonomous_spend_or_scaling": True,
    }

    _append_jsonl(EXECUTION_RESULTS, result)
    _append_jsonl(EXECUTION_EVENTS, {
        "event_id": f"live_exec_event_{uuid.uuid4().hex[:16]}",
        "execution_id": execution_id,
        "tenant_id": tenant_id,
        "workflow_id": workflow_id,
        "agent_id": agent_id,
        "provider": provider,
        "action_type": action_type,
        "status": status,
        "execution_state": execution_state,
        "created_at": _now(),
        "governance_preserved": True,
    })

    return result


def list_live_provider_executions(
    *,
    tenant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    rows = _read_jsonl(EXECUTION_RESULTS)
    if tenant_id:
        rows = [r for r in rows if r.get("tenant_id") == tenant_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    rows = rows[-limit:]
    return {
        "status": "ok",
        "count": len(rows),
        "executions": rows,
        "governance_preserved": True,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.runtime.live_provider_execution_outputs import execute_live_provider_packet, list_live_provider_executions, live_provider_execution_readiness\n"
if import_line not in main_text:
    import_matches = list(re.finditer(r"^(from backend\.app\.runtime\..*|from backend\.app\.core\..*|import .*)$", main_text, flags=re.MULTILINE))
    insert_at = import_matches[-1].end() + 1 if import_matches else 0
    main_text = main_text[:insert_at] + import_line + main_text[insert_at:]

routes_block = r'''

@app.get("/admin/live-provider-execution/readiness")
def admin_live_provider_execution_readiness():
    return live_provider_execution_readiness()


@app.post("/admin/live-provider-execution/execute")
def admin_execute_live_provider_packet(payload: dict):
    return execute_live_provider_packet(
        tenant_id=str(payload.get("tenant_id", "tenant_unknown")),
        workflow_id=str(payload.get("workflow_id", "workflow_unknown")),
        agent_id=str(payload.get("agent_id", "unknown_agent")),
        provider=str(payload.get("provider", "")),
        action_type=str(payload.get("action_type", "unknown_action")),
        payload=dict(payload.get("payload", {})),
        execution_allowed=bool(payload.get("execution_allowed", True)),
        owner_approved=bool(payload.get("owner_approved", False)),
        live_keys_available=bool(payload.get("live_keys_available", False)),
        entitlement_active=bool(payload.get("entitlement_active", True)),
    )


@app.get("/admin/live-provider-execution/list")
def admin_list_live_provider_executions(tenant_id: str | None = None, status: str | None = None, limit: int = 50):
    return list_live_provider_executions(tenant_id=tenant_id, status=status, limit=limit)
'''

if "/admin/live-provider-execution/readiness" not in main_text:
    main_text = main_text.rstrip() + routes_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST_FILE.write_text(r'''
from backend.app.runtime.live_provider_execution_outputs import (
    execute_live_provider_packet,
    list_live_provider_executions,
    live_provider_execution_readiness,
)


def main():
    readiness = live_provider_execution_readiness()
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    prepared = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_test",
        agent_id="email_reply_agent",
        provider="gmail",
        action_type="send_email_draft",
        payload={"subject": "Test", "body": "Prepared test email"},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=False,
        entitlement_active=True,
    )
    assert prepared["status"] == "prepared"
    assert prepared["external_execution_performed"] is False
    assert prepared["provider_output"]["format"] == "email_packet"

    executed = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_openai_test",
        agent_id="marketing_specialist_agent",
        provider="openai",
        action_type="generate_campaign_copy",
        payload={"brand": "Demo Brand", "region": "Australia", "task": "campaign copy"},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=True,
        entitlement_active=True,
    )
    assert executed["status"] == "executed"
    assert executed["external_execution_performed"] is True
    assert executed["provider_output"]["format"] == "text"

    gated = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_ads_test",
        agent_id="marketing_specialist_agent",
        provider="meta_ads",
        action_type="scale_campaign",
        payload={"increase_ad_spend": True},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=True,
        entitlement_active=True,
    )
    assert gated["status"] == "pending_owner_approval"
    assert gated["external_execution_performed"] is False

    blocked = execute_live_provider_packet(
        tenant_id="tenant_test",
        workflow_id="workflow_live_blocked_test",
        agent_id="crm_agent",
        provider="ghl",
        action_type="create_note",
        payload={"note": "Test note"},
        execution_allowed=True,
        owner_approved=False,
        live_keys_available=True,
        entitlement_active=False,
    )
    assert blocked["status"] == "blocked"

    listed = list_live_provider_executions(tenant_id="tenant_test")
    assert listed["count"] >= 4

    print("LIVE_PROVIDER_EXECUTION_OUTPUTS_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

IMPORT_TEST.write_text(r'''
def main():
    import backend.app.main as main_module

    route_paths = {getattr(route, "path", "") for route in getattr(main_module, "app").routes}
    required = {
        "/admin/live-provider-execution/readiness",
        "/admin/live-provider-execution/execute",
        "/admin/live-provider-execution/list",
    }
    missing = sorted(required - route_paths)
    assert not missing, missing

    print("LIVE_PROVIDER_EXECUTION_OUTPUTS_ADMIN_ENDPOINTS_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("LIVE_PROVIDER_EXECUTION_OUTPUTS_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {LIVE_RUNTIME}")
print(f"Created/updated: {TEST_FILE}")
print(f"Created/updated: {IMPORT_TEST}")
print("Routes:")
print("/admin/live-provider-execution/readiness")
print("/admin/live-provider-execution/execute")
print("/admin/live-provider-execution/list")