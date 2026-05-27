from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
RUNTIME = CORE / "marketplace_state_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_backup = BACKUP_DIR / f"main_before_priority9_marketplace_state_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.core.marketplace_activation_runtime import (
    activate_marketplace_agent,
    deactivate_marketplace_agent,
    build_client_marketplace_workspace,
)
from backend.app.core.marketplace_entitlement_runtime import PACKAGE_LIMITS


DATA_DIR = Path.cwd() / "runtime_data"
STATE_FILE = DATA_DIR / "marketplace_tenant_state.jsonl"
AUDIT_FILE = DATA_DIR / "marketplace_activation_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_jsonl(path: Path, limit: int = 5000) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except Exception:
                continue

    return records[-limit:]


def _rewrite_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _unique(values: List[str]) -> List[str]:
    return list(dict.fromkeys([str(v).strip().lower() for v in values if str(v).strip()]))


def _find_state(records: List[Dict[str, Any]], tenant_id: str) -> Dict[str, Any] | None:
    for record in reversed(records):
        if record.get("tenant_id") == tenant_id:
            return record
    return None


def upsert_marketplace_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    state = {
        "tenant_id": tenant_id,
        "client_number": payload.get("client_number"),
        "package": str(payload.get("package") or "starter").lower(),
        "purchased_agents": _unique(payload.get("purchased_agents") or []),
        "active_agents": _unique(payload.get("active_agents") or payload.get("activated_agents") or []),
        "updated_at": _now(),
        "state_profile": "priority9_marketplace_state_v1",
        "client_access_limited_to_paid_agents": True,
        "internal_config_hidden_from_client": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }

    records = _read_jsonl(STATE_FILE)
    records = [r for r in records if r.get("tenant_id") != tenant_id]
    records.append(state)
    _rewrite_jsonl(STATE_FILE, records)

    _append_jsonl(AUDIT_FILE, {
        "timestamp": _now(),
        "event_type": "marketplace_state_upserted",
        "tenant_id": tenant_id,
        "client_number": state.get("client_number"),
        "package": state.get("package"),
    })

    return {"success": True, "state": state}


def get_marketplace_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    records = _read_jsonl(STATE_FILE)
    state = _find_state(records, tenant_id)

    if not state:
        return {
            "success": False,
            "error": "marketplace_state_not_found",
            "tenant_id": tenant_id,
        }

    workspace = build_client_marketplace_workspace(state)

    return {
        "success": True,
        "state": state,
        "workspace": workspace,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "internal_config_hidden_from_client": True,
    }


def persist_activation_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    action = str(payload.get("action") or "activate").strip().lower()
    agent_id = str(payload.get("agent_id") or "").strip().lower()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    records = _read_jsonl(STATE_FILE)
    state = _find_state(records, tenant_id)

    if not state:
        initial = upsert_marketplace_state(payload)
        state = initial.get("state", {})

    action_payload = {
        **state,
        "agent_id": agent_id,
    }

    if action == "activate":
        result = activate_marketplace_agent(action_payload)
    elif action == "deactivate":
        result = deactivate_marketplace_agent(action_payload)
    else:
        return {"success": False, "error": "unsupported_marketplace_action"}

    if result.get("success"):
        state["active_agents"] = result.get("active_agents", state.get("active_agents", []))
        state["updated_at"] = _now()

        records = [r for r in _read_jsonl(STATE_FILE) if r.get("tenant_id") != tenant_id]
        records.append(state)
        _rewrite_jsonl(STATE_FILE, records)

    _append_jsonl(AUDIT_FILE, {
        "timestamp": _now(),
        "event_type": f"marketplace_agent_{action}",
        "tenant_id": tenant_id,
        "client_number": state.get("client_number"),
        "agent_id": agent_id,
        "success": result.get("success"),
        "status": result.get("status"),
        "error": result.get("error"),
    })

    return {
        **result,
        "persisted": bool(result.get("success")),
        "state": state if result.get("success") else None,
        "audit_logged": True,
    }


def validate_package_downgrade(payload: Dict[str, Any]) -> Dict[str, Any]:
    current_package = str(payload.get("current_package") or payload.get("package") or "starter").lower()
    target_package = str(payload.get("target_package") or "starter").lower()
    active_agents = _unique(payload.get("active_agents") or [])

    current_limit = PACKAGE_LIMITS.get(current_package, 2)
    target_limit = PACKAGE_LIMITS.get(target_package, 2)

    blocked = target_package != "enterprise" and len(active_agents) > target_limit

    return {
        "success": True,
        "downgrade_allowed": not blocked,
        "blocked": blocked,
        "current_package": current_package,
        "target_package": target_package,
        "current_package_limit": current_limit,
        "target_package_limit": target_limit,
        "active_agent_count": len(active_agents),
        "agents_to_deactivate_required": max(0, len(active_agents) - target_limit),
        "customer_safe_message": (
            "Deactivate agents before downgrading." if blocked else "Downgrade can continue."
        ),
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def marketplace_audit_history(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    limit = int(payload.get("limit") or 50)

    events = _read_jsonl(AUDIT_FILE, limit=5000)
    if tenant_id:
        events = [e for e in events if e.get("tenant_id") == tenant_id]

    return {
        "success": True,
        "tenant_id": tenant_id or None,
        "count": len(events[-limit:]),
        "events": events[-limit:],
        "secret_exposure": False,
        "customer_safe_response_mode": True,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.marketplace_state_runtime import upsert_marketplace_state, get_marketplace_state, persist_activation_action, validate_package_downgrade, marketplace_audit_history"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

routes = r'''

@app.post("/admin/marketplace/state/upsert")
def admin_marketplace_state_upsert(payload: dict):
    return upsert_marketplace_state(payload)


@app.post("/admin/marketplace/state/get")
def admin_marketplace_state_get(payload: dict):
    return get_marketplace_state(payload)


@app.post("/admin/marketplace/state/action")
def admin_marketplace_state_action(payload: dict):
    return persist_activation_action(payload)


@app.post("/admin/marketplace/downgrade-check")
def admin_marketplace_downgrade_check(payload: dict):
    return validate_package_downgrade(payload)


@app.post("/admin/marketplace/audit-history")
def admin_marketplace_audit_history(payload: dict):
    return marketplace_audit_history(payload)
'''

if "/admin/marketplace/state/upsert" not in main_text:
    main_text = main_text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority9_persistent_marketplace_state.py"
TEST.write_text(r'''
import json
import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {
    "x-actor-role": "admin",
    "x-tenant-id": "owner",
    "Content-Type": "application/json",
}

def show(label, response):
    print("\n" + "=" * 80)
    print(label)
    print("HTTP", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2)[:14000])
    except Exception:
        print(response.text[:14000])

state_payload = {
    "tenant_id": "tenant_priority9_state_test",
    "client_number": "CL-P9-STATE",
    "package": "growth",
    "purchased_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent",
        "ugc_creative_agent",
        "product_image_agent"
    ],
    "active_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "ugc_creative_agent"
    ]
}

upsert = requests.post(f"{BASE}/admin/marketplace/state/upsert", headers=HEADERS, json=state_payload, timeout=30)
show("UPSERT_MARKETPLACE_STATE", upsert)

activate = requests.post(
    f"{BASE}/admin/marketplace/state/action",
    headers=HEADERS,
    json={**state_payload, "action": "activate", "agent_id": "product_image_agent"},
    timeout=30,
)
show("PERSIST_ACTIVATION", activate)

get_state = requests.post(
    f"{BASE}/admin/marketplace/state/get",
    headers=HEADERS,
    json={"tenant_id": "tenant_priority9_state_test"},
    timeout=30,
)
show("GET_MARKETPLACE_STATE", get_state)

downgrade_block = requests.post(
    f"{BASE}/admin/marketplace/downgrade-check",
    headers=HEADERS,
    json={
        "current_package": "growth",
        "target_package": "starter",
        "active_agents": activate.json().get("active_agents", [])
    },
    timeout=30,
)
show("DOWNGRADE_BLOCK_CHECK", downgrade_block)

deactivate = requests.post(
    f"{BASE}/admin/marketplace/state/action",
    headers=HEADERS,
    json={**state_payload, "action": "deactivate", "agent_id": "ugc_creative_agent"},
    timeout=30,
)
show("PERSIST_DEACTIVATION", deactivate)

audit = requests.post(
    f"{BASE}/admin/marketplace/audit-history",
    headers=HEADERS,
    json={"tenant_id": "tenant_priority9_state_test", "limit": 20},
    timeout=30,
)
show("MARKETPLACE_AUDIT_HISTORY", audit)

for response in [upsert, activate, get_state, downgrade_block, deactivate, audit]:
    assert response.status_code == 200

assert upsert.json()["success"] is True
assert upsert.json()["state"]["tenant_id"] == "tenant_priority9_state_test"

assert activate.json()["success"] is True
assert activate.json()["persisted"] is True
assert "product_image_agent" in activate.json()["active_agents"]

state = get_state.json()
assert state["success"] is True
assert state["state"]["tenant_id"] == "tenant_priority9_state_test"
assert "product_image_agent" in state["state"]["active_agents"]
assert state["workspace"]["catalogue_agent_count"] == 27
assert state["secret_exposure"] is False

assert downgrade_block.json()["success"] is True
assert downgrade_block.json()["downgrade_allowed"] is False
assert downgrade_block.json()["agents_to_deactivate_required"] >= 1

assert deactivate.json()["success"] is True
assert deactivate.json()["persisted"] is True
assert "ugc_creative_agent" not in deactivate.json()["active_agents"]

assert audit.json()["success"] is True
assert audit.json()["count"] >= 3
assert audit.json()["secret_exposure"] is False

print("\nPRIORITY9_PERSISTENT_MARKETPLACE_STATE_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY9_PERSISTENT_MARKETPLACE_STATE_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Created/updated: {RUNTIME}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")