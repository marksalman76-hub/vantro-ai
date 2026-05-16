from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
API = BACKEND / "api"
BACKUPS = ROOT / "backups"
DATA = BACKEND / "data"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

mapping_file = CORE / "stripe_tenant_mapping_store.py"
bridge_file = CORE / "stripe_billing_runtime_bridge.py"
routes_file = API / "subscription_policy_routes.py"

for file in [mapping_file, bridge_file, routes_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step203_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

mapping_file.write_text(r'''
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAPPING_FILE = DATA_DIR / "stripe_tenant_mappings.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> Dict[str, Any]:
    if not MAPPING_FILE.exists():
        return {
            "version": "step203_stripe_tenant_mapping_v1",
            "mappings": [],
            "updated_at": utc_now_iso(),
        }

    try:
        return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "step203_stripe_tenant_mapping_v1",
            "mappings": [],
            "updated_at": utc_now_iso(),
            "recovered_from_invalid_json": True,
        }


def _save(data: Dict[str, Any]) -> None:
    data["updated_at"] = utc_now_iso()
    MAPPING_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def upsert_stripe_tenant_mapping(
    tenant_id: str,
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
    company_name: Optional[str] = None,
    subscription_status: Optional[str] = None,
    package_name: Optional[str] = None,
) -> Dict[str, Any]:
    if not tenant_id:
        raise ValueError("tenant_id_required")

    data = _load()
    mappings = data.setdefault("mappings", [])

    existing = None
    for item in mappings:
        if item.get("tenant_id") == tenant_id:
            existing = item
            break

    if existing is None:
        existing = {
            "tenant_id": tenant_id,
            "created_at": utc_now_iso(),
        }
        mappings.append(existing)

    if stripe_customer_id:
        existing["stripe_customer_id"] = stripe_customer_id

    if stripe_subscription_id:
        existing["stripe_subscription_id"] = stripe_subscription_id

    if company_name:
        existing["company_name"] = company_name

    if subscription_status:
        existing["subscription_status"] = subscription_status

    if package_name:
        existing["package_name"] = package_name

    existing["updated_at"] = utc_now_iso()
    _save(data)

    return {
        "success": True,
        "mapping": existing,
        "mapping_file": str(MAPPING_FILE),
    }


def resolve_tenant_by_stripe_ids(
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
) -> Dict[str, Any]:
    data = _load()

    for item in data.get("mappings", []):
        if stripe_customer_id and item.get("stripe_customer_id") == stripe_customer_id:
            return {
                "success": True,
                "resolved": True,
                "match_type": "stripe_customer_id",
                "mapping": item,
            }

        if stripe_subscription_id and item.get("stripe_subscription_id") == stripe_subscription_id:
            return {
                "success": True,
                "resolved": True,
                "match_type": "stripe_subscription_id",
                "mapping": item,
            }

    return {
        "success": True,
        "resolved": False,
        "match_type": None,
        "mapping": None,
    }


def list_stripe_tenant_mappings(limit: int = 50) -> Dict[str, Any]:
    data = _load()
    mappings = data.get("mappings", [])[-limit:]

    return {
        "success": True,
        "count": len(mappings),
        "mappings": mappings,
        "mapping_file": str(MAPPING_FILE),
        "checked_at": utc_now_iso(),
    }
'''.lstrip(), encoding="utf-8")

bridge_file.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.core.stripe_tenant_mapping_store import resolve_tenant_by_stripe_ids


EVENT_MEMORY: list[Dict[str, Any]] = []


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def apply_stripe_classification_to_billing_runtime(
    event: Dict[str, Any],
    classification: Dict[str, Any],
) -> Dict[str, Any]:
    stripe_customer_id = event.get("stripe_customer_id")
    stripe_subscription_id = event.get("stripe_subscription_id")
    mapping_result = resolve_tenant_by_stripe_ids(
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
    )

    tenant_mapping = mapping_result.get("mapping") if mapping_result.get("resolved") else None
    tenant_id = tenant_mapping.get("tenant_id") if tenant_mapping else None
    action = classification.get("action")

    runtime_update = {
        "success": True,
        "tenant_id": tenant_id,
        "tenant_resolved": bool(tenant_id),
        "tenant_reference": tenant_id or f"unmapped_stripe_customer::{stripe_customer_id or 'unknown'}",
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "event_type": event.get("event_type"),
        "classification_action": action,
        "processed_at": utc_now_iso(),
        "durable_runtime_update_mode": "tenant_mapping_ready",
        "runtime_mutation_committed": bool(tenant_id),
        "reason": "tenant_mapping_resolved" if tenant_id else "durable_tenant_stripe_mapping_pending",
        "mapping_match_type": mapping_result.get("match_type"),
    }

    if action == "mark_subscription_active_and_reset_monthly_credits":
        runtime_update.update({
            "target_subscription_status": "active",
            "target_client_execution_allowed": True,
            "target_credit_action": "reset_monthly_credits",
            "preserve_cycle_anchor": True,
        })

    elif action == "mark_subscription_past_due_and_block_client_credit_consuming_execution":
        runtime_update.update({
            "target_subscription_status": "past_due",
            "target_client_execution_allowed": False,
            "target_credit_action": "block_credit_consuming_execution",
            "retry_interval_hours": classification.get("retry_interval_hours", 48),
            "preserve_cycle_anchor": True,
        })

    elif action == "mark_subscription_cancelled_and_block_client_execution":
        runtime_update.update({
            "target_subscription_status": "cancelled",
            "target_client_execution_allowed": False,
            "target_credit_action": "block_client_execution",
        })

    elif action == "sync_subscription_status_cancel_policy_and_cycle_dates":
        runtime_update.update({
            "target_subscription_status": event.get("status") or "sync_required",
            "target_client_execution_allowed": "depends_on_synced_subscription_status",
            "target_credit_action": "sync_only",
            "cancel_at_period_end": event.get("cancel_at_period_end"),
            "preserve_cycle_anchor": True,
        })

    else:
        runtime_update.update({
            "target_subscription_status": "unchanged",
            "target_client_execution_allowed": "unchanged",
            "target_credit_action": "none",
        })

    EVENT_MEMORY.append(runtime_update)
    return runtime_update


def latest_billing_bridge_events(limit: int = 20) -> Dict[str, Any]:
    return {
        "success": True,
        "count": len(EVENT_MEMORY[-limit:]),
        "events": EVENT_MEMORY[-limit:],
        "checked_at": utc_now_iso(),
    }
'''.lstrip(), encoding="utf-8")

routes_text = routes_file.read_text(encoding="utf-8")

if "from backend.app.core.stripe_tenant_mapping_store import (" not in routes_text:
    routes_text = routes_text.replace(
        "from pydantic import BaseModel\n",
        "from pydantic import BaseModel\n\n"
        "from backend.app.core.stripe_tenant_mapping_store import (\n"
        "    list_stripe_tenant_mappings,\n"
        "    upsert_stripe_tenant_mapping,\n"
        ")\n",
    )

if "class StripeTenantMappingRequest(BaseModel):" not in routes_text:
    routes_text = routes_text.replace(
        "class ReactivationRequest(BaseModel):\n"
        "    tenant_id: str\n"
        "    subscription_id: Optional[str] = None\n"
        "    reason: Optional[str] = None\n",
        "class ReactivationRequest(BaseModel):\n"
        "    tenant_id: str\n"
        "    subscription_id: Optional[str] = None\n"
        "    reason: Optional[str] = None\n\n\n"
        "class StripeTenantMappingRequest(BaseModel):\n"
        "    tenant_id: str\n"
        "    stripe_customer_id: Optional[str] = None\n"
        "    stripe_subscription_id: Optional[str] = None\n"
        "    company_name: Optional[str] = None\n"
        "    subscription_status: Optional[str] = None\n"
        "    package_name: Optional[str] = None\n",
    )

if "@router.post(\"/admin/billing/stripe-tenant-mapping\")" not in routes_text:
    routes_text += r'''


@router.post("/admin/billing/stripe-tenant-mapping")
def create_or_update_stripe_tenant_mapping(
    payload: StripeTenantMappingRequest,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return upsert_stripe_tenant_mapping(
        tenant_id=payload.tenant_id,
        stripe_customer_id=payload.stripe_customer_id,
        stripe_subscription_id=payload.stripe_subscription_id,
        company_name=payload.company_name,
        subscription_status=payload.subscription_status,
        package_name=payload.package_name,
    )


@router.get("/admin/billing/stripe-tenant-mappings")
def get_stripe_tenant_mappings(
    x_actor_role: Optional[str] = Header(default=None),
    limit: int = 50,
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return list_stripe_tenant_mappings(limit=limit)
'''

routes_file.write_text(routes_text, encoding="utf-8")

print("STEP_203_STRIPE_TENANT_MAPPING_INSTALLED")
print(f"Created/updated: {mapping_file}")
print(f"Updated: {bridge_file}")
print(f"Updated: {routes_file}")
print("STEP_203_OK")