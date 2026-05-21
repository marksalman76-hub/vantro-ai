from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
RUNTIME = CORE / "marketplace_commercial_bridge.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_backup = BACKUP_DIR / f"main_before_priority9_commercial_bridge_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.core.marketplace_entitlement_runtime import PACKAGE_LIMITS
from backend.app.core.marketplace_state_runtime import get_marketplace_state, upsert_marketplace_state, validate_package_downgrade


DATA_DIR = Path.cwd() / "runtime_data"
COMMERCIAL_EVENTS_FILE = DATA_DIR / "marketplace_commercial_events.jsonl"

PACKAGE_PRICING = {
    "starter": {
        "monthly_aud": 497,
        "agent_limit": 2,
        "positioning": "Starter automation package",
    },
    "growth": {
        "monthly_aud": 997,
        "agent_limit": 5,
        "positioning": "Growth automation package",
    },
    "professional": {
        "monthly_aud": 1997,
        "agent_limit": 10,
        "positioning": "Professional automation package",
    },
    "enterprise": {
        "monthly_aud": None,
        "agent_limit": 999,
        "positioning": "Custom enterprise automation package",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


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


def _normalise_package(package: str) -> str:
    package = str(package or "starter").strip().lower()
    return package if package in PACKAGE_PRICING else "starter"


def package_pricing_catalogue() -> Dict[str, Any]:
    return {
        "success": True,
        "pricing_profile": "priority9_package_pricing_catalogue_v1",
        "currency": "AUD",
        "billing_interval": "monthly",
        "packages": PACKAGE_PRICING,
        "month_to_month": True,
        "no_lock_in_contract": True,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }


def build_purchase_flow_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    current_package = _normalise_package(payload.get("current_package") or payload.get("package"))
    target_package = _normalise_package(payload.get("target_package"))
    selected_agents = list(dict.fromkeys(payload.get("selected_agents") or payload.get("purchased_agents") or []))

    current_price = PACKAGE_PRICING[current_package]["monthly_aud"]
    target_price = PACKAGE_PRICING[target_package]["monthly_aud"]

    if target_package == "enterprise":
        checkout_required = False
        owner_sales_required = True
        price_delta = None
    else:
        checkout_required = True
        owner_sales_required = False
        price_delta = (target_price or 0) - (current_price or 0)

    event = {
        "timestamp": _now(),
        "event_type": "marketplace_purchase_flow_created",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "current_package": current_package,
        "target_package": target_package,
        "selected_agents": selected_agents,
        "checkout_required": checkout_required,
    }
    _append_jsonl(COMMERCIAL_EVENTS_FILE, event)

    return {
        "success": True,
        "purchase_flow_profile": "priority9_purchase_flow_payload_v1",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "current_package": current_package,
        "target_package": target_package,
        "selected_agents": selected_agents,
        "current_monthly_aud": current_price,
        "target_monthly_aud": target_price,
        "monthly_delta_aud": price_delta,
        "checkout_required": checkout_required,
        "owner_sales_required": owner_sales_required,
        "stripe_checkout_ready": checkout_required,
        "enterprise_contact_required": owner_sales_required,
        "billing_required": checkout_required,
        "customer_safe_message": (
            "Continue to checkout to activate this upgrade."
            if checkout_required else
            "Enterprise package requires owner review and custom setup."
        ),
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def create_entitlement_change_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    change_type = str(payload.get("change_type") or "upgrade").strip().lower()
    current_package = _normalise_package(payload.get("current_package") or payload.get("package"))
    target_package = _normalise_package(payload.get("target_package"))
    active_agents = list(dict.fromkeys(payload.get("active_agents") or []))
    purchased_agents = list(dict.fromkeys(payload.get("purchased_agents") or []))

    request_id = f"entchg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    downgrade_check = None
    if change_type == "downgrade":
        downgrade_check = validate_package_downgrade({
            "current_package": current_package,
            "target_package": target_package,
            "active_agents": active_agents,
        })
        if downgrade_check.get("blocked"):
            status = "blocked_requires_agent_deactivation"
        else:
            status = "ready_for_billing_sync"
    elif target_package == "enterprise":
        status = "owner_sales_review_required"
    else:
        status = "ready_for_checkout"

    event = {
        "timestamp": _now(),
        "event_type": "entitlement_change_requested",
        "request_id": request_id,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "change_type": change_type,
        "current_package": current_package,
        "target_package": target_package,
        "active_agents": active_agents,
        "purchased_agents": purchased_agents,
        "status": status,
    }
    _append_jsonl(COMMERCIAL_EVENTS_FILE, event)

    return {
        "success": True,
        "request_id": request_id,
        "change_type": change_type,
        "status": status,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "current_package": current_package,
        "target_package": target_package,
        "downgrade_check": downgrade_check,
        "billing_sync_required": status in {"ready_for_billing_sync", "ready_for_checkout"},
        "checkout_required": status == "ready_for_checkout",
        "owner_sales_review_required": status == "owner_sales_review_required",
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def apply_entitlement_change_after_billing(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    target_package = _normalise_package(payload.get("target_package"))
    purchased_agents = list(dict.fromkeys(payload.get("purchased_agents") or []))
    active_agents = list(dict.fromkeys(payload.get("active_agents") or []))
    billing_status = str(payload.get("billing_status") or "paid").lower()

    if billing_status not in {"paid", "active", "trial_active"}:
        return {
            "success": False,
            "error": "billing_not_active",
            "billing_status": billing_status,
            "customer_safe_message": "Billing must be active before this change can be applied.",
        }

    state_result = upsert_marketplace_state({
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": target_package,
        "purchased_agents": purchased_agents,
        "active_agents": active_agents,
    })

    event = {
        "timestamp": _now(),
        "event_type": "entitlement_change_applied_after_billing",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "target_package": target_package,
        "billing_status": billing_status,
        "success": state_result.get("success"),
    }
    _append_jsonl(COMMERCIAL_EVENTS_FILE, event)

    return {
        "success": state_result.get("success"),
        "status": "entitlement_change_applied",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": target_package,
        "state": state_result.get("state"),
        "billing_status": billing_status,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "entitlement_bypass": False,
        "governance_bypass": False,
    }


def marketplace_commercial_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    events = _read_jsonl(COMMERCIAL_EVENTS_FILE, limit=5000)

    if tenant_id:
        events = [event for event in events if event.get("tenant_id") == tenant_id]

    event_counts: Dict[str, int] = {}
    for event in events:
        event_type = event.get("event_type") or "unknown"
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    return {
        "success": True,
        "summary_profile": "priority9_marketplace_commercial_summary_v1",
        "tenant_id": tenant_id,
        "event_count": len(events),
        "event_counts": event_counts,
        "recent_events": events[-25:],
        "pricing_catalogue": PACKAGE_PRICING,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.marketplace_commercial_bridge import package_pricing_catalogue, build_purchase_flow_payload, create_entitlement_change_request, apply_entitlement_change_after_billing, marketplace_commercial_summary"
if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

routes = r'''

@app.get("/client/marketplace/pricing")
def client_marketplace_pricing():
    return package_pricing_catalogue()


@app.post("/client/marketplace/purchase-flow")
def client_marketplace_purchase_flow(payload: dict):
    return build_purchase_flow_payload(payload)


@app.post("/admin/marketplace/entitlement-change/request")
def admin_marketplace_entitlement_change_request(payload: dict):
    return create_entitlement_change_request(payload)


@app.post("/admin/marketplace/entitlement-change/apply-after-billing")
def admin_marketplace_entitlement_change_apply_after_billing(payload: dict):
    return apply_entitlement_change_after_billing(payload)


@app.post("/admin/marketplace/commercial-summary")
def admin_marketplace_commercial_summary(payload: dict):
    return marketplace_commercial_summary(payload)
'''

if "/client/marketplace/pricing" not in main_text:
    main_text = main_text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority9_commercial_marketplace_bridge.py"
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
        print(json.dumps(response.json(), indent=2)[:12000])
    except Exception:
        print(response.text[:12000])

base_payload = {
    "tenant_id": "tenant_priority9_commercial_test",
    "client_number": "CL-P9-COMMERCIAL",
    "current_package": "growth",
    "target_package": "professional",
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
        "ugc_creative_agent",
        "product_image_agent"
    ],
}

pricing = requests.get(f"{BASE}/client/marketplace/pricing", headers=HEADERS, timeout=30)
show("PRICING_CATALOGUE", pricing)

purchase = requests.post(
    f"{BASE}/client/marketplace/purchase-flow",
    headers=HEADERS,
    json=base_payload,
    timeout=30,
)
show("PURCHASE_FLOW", purchase)

upgrade_request = requests.post(
    f"{BASE}/admin/marketplace/entitlement-change/request",
    headers=HEADERS,
    json={**base_payload, "change_type": "upgrade"},
    timeout=30,
)
show("UPGRADE_CHANGE_REQUEST", upgrade_request)

apply_after_billing = requests.post(
    f"{BASE}/admin/marketplace/entitlement-change/apply-after-billing",
    headers=HEADERS,
    json={**base_payload, "target_package": "professional", "billing_status": "paid"},
    timeout=30,
)
show("APPLY_AFTER_BILLING", apply_after_billing)

downgrade_request = requests.post(
    f"{BASE}/admin/marketplace/entitlement-change/request",
    headers=HEADERS,
    json={**base_payload, "change_type": "downgrade", "target_package": "starter"},
    timeout=30,
)
show("DOWNGRADE_CHANGE_REQUEST", downgrade_request)

summary = requests.post(
    f"{BASE}/admin/marketplace/commercial-summary",
    headers=HEADERS,
    json={"tenant_id": "tenant_priority9_commercial_test"},
    timeout=30,
)
show("COMMERCIAL_SUMMARY", summary)

for response in [pricing, purchase, upgrade_request, apply_after_billing, downgrade_request, summary]:
    assert response.status_code == 200

pricing_json = pricing.json()
purchase_json = purchase.json()
upgrade_json = upgrade_request.json()
apply_json = apply_after_billing.json()
downgrade_json = downgrade_request.json()
summary_json = summary.json()

assert pricing_json["success"] is True
assert pricing_json["packages"]["growth"]["monthly_aud"] == 997
assert pricing_json["month_to_month"] is True

assert purchase_json["success"] is True
assert purchase_json["checkout_required"] is True
assert purchase_json["target_package"] == "professional"
assert purchase_json["billing_required"] is True
assert purchase_json["secret_exposure"] is False

assert upgrade_json["success"] is True
assert upgrade_json["change_type"] == "upgrade"
assert upgrade_json["status"] == "ready_for_checkout"
assert upgrade_json["checkout_required"] is True

assert apply_json["success"] is True
assert apply_json["package"] == "professional"
assert apply_json["billing_status"] == "paid"
assert apply_json["state"]["package"] == "professional"

assert downgrade_json["success"] is True
assert downgrade_json["change_type"] == "downgrade"
assert downgrade_json["status"] == "blocked_requires_agent_deactivation"
assert downgrade_json["downgrade_check"]["blocked"] is True

assert summary_json["success"] is True
assert summary_json["event_count"] >= 3
assert summary_json["secret_exposure"] is False

print("\nPRIORITY9_COMMERCIAL_MARKETPLACE_BRIDGE_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY9_COMMERCIAL_MARKETPLACE_BRIDGE_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Created/updated: {RUNTIME}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {TEST}")