from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
API = BACKEND / "api"
DATA = BACKEND / "data"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

billing_state_file = CORE / "durable_billing_state_store.py"
bridge_file = CORE / "stripe_billing_runtime_bridge.py"
routes_file = API / "subscription_policy_routes.py"

for file in [billing_state_file, bridge_file, routes_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step204_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

billing_state_file.write_text(r'''
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BILLING_STATE_FILE = DATA_DIR / "durable_billing_state.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> Dict[str, Any]:
    if not BILLING_STATE_FILE.exists():
        return {
            "version": "step204_durable_billing_state_v1",
            "tenants": {},
            "events": [],
            "updated_at": utc_now_iso(),
        }

    try:
        return json.loads(BILLING_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "step204_durable_billing_state_v1",
            "tenants": {},
            "events": [],
            "updated_at": utc_now_iso(),
            "recovered_from_invalid_json": True,
        }


def _save(data: Dict[str, Any]) -> None:
    data["updated_at"] = utc_now_iso()
    BILLING_STATE_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def apply_billing_runtime_mutation(
    tenant_id: str,
    stripe_customer_id: Optional[str],
    stripe_subscription_id: Optional[str],
    event_type: str,
    target_subscription_status: str,
    target_client_execution_allowed: Any,
    target_credit_action: str,
    preserve_cycle_anchor: bool = True,
    retry_interval_hours: Optional[int] = None,
    cancel_at_period_end: Optional[bool] = None,
) -> Dict[str, Any]:
    if not tenant_id:
        return {
            "success": False,
            "mutation_committed": False,
            "reason": "tenant_id_required",
        }

    data = _load()
    tenants = data.setdefault("tenants", {})
    events = data.setdefault("events", [])

    tenant_state = tenants.setdefault(tenant_id, {
        "tenant_id": tenant_id,
        "created_at": utc_now_iso(),
        "client_execution_allowed": True,
        "subscription_status": "unknown",
        "credit_state": "unknown",
    })

    previous_state = dict(tenant_state)

    tenant_state["tenant_id"] = tenant_id
    tenant_state["stripe_customer_id"] = stripe_customer_id
    tenant_state["stripe_subscription_id"] = stripe_subscription_id
    tenant_state["subscription_status"] = target_subscription_status
    tenant_state["last_event_type"] = event_type
    tenant_state["last_webhook_processed_at"] = utc_now_iso()
    tenant_state["preserve_cycle_anchor"] = preserve_cycle_anchor

    if isinstance(target_client_execution_allowed, bool):
        tenant_state["client_execution_allowed"] = target_client_execution_allowed

    tenant_state["credit_action"] = target_credit_action

    if target_credit_action == "reset_monthly_credits":
        tenant_state["credit_state"] = "monthly_credits_reset_required"
        tenant_state["execution_block_reason"] = None

    elif target_credit_action in {"block_credit_consuming_execution", "block_client_execution"}:
        tenant_state["credit_state"] = "blocked"
        tenant_state["execution_block_reason"] = target_subscription_status

    elif target_credit_action == "sync_only":
        tenant_state["credit_state"] = "sync_only"

    if retry_interval_hours is not None:
        tenant_state["retry_interval_hours"] = retry_interval_hours

    if cancel_at_period_end is not None:
        tenant_state["cancel_at_period_end"] = cancel_at_period_end

    tenant_state["updated_at"] = utc_now_iso()

    event_record = {
        "tenant_id": tenant_id,
        "event_type": event_type,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "target_subscription_status": target_subscription_status,
        "target_client_execution_allowed": target_client_execution_allowed,
        "target_credit_action": target_credit_action,
        "processed_at": utc_now_iso(),
    }

    events.append(event_record)
    data["events"] = events[-200:]

    _save(data)

    return {
        "success": True,
        "mutation_committed": True,
        "tenant_id": tenant_id,
        "previous_state": previous_state,
        "updated_state": tenant_state,
        "event_record": event_record,
        "billing_state_file": str(BILLING_STATE_FILE),
    }


def get_billing_runtime_state(tenant_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    data = _load()

    if tenant_id:
        return {
            "success": True,
            "tenant_id": tenant_id,
            "state": data.get("tenants", {}).get(tenant_id),
            "checked_at": utc_now_iso(),
        }

    return {
        "success": True,
        "tenant_count": len(data.get("tenants", {})),
        "tenants": data.get("tenants", {}),
        "event_count": len(data.get("events", [])[-limit:]),
        "events": data.get("events", [])[-limit:],
        "billing_state_file": str(BILLING_STATE_FILE),
        "checked_at": utc_now_iso(),
    }
'''.lstrip(), encoding="utf-8")

bridge_file.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.core.durable_billing_state_store import apply_billing_runtime_mutation
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
        "durable_runtime_update_mode": "durable_state_mutation",
        "runtime_mutation_committed": False,
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
            "preserve_cycle_anchor": True,
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
            "preserve_cycle_anchor": True,
        })

    if tenant_id:
        mutation = apply_billing_runtime_mutation(
            tenant_id=tenant_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            event_type=event.get("event_type"),
            target_subscription_status=runtime_update.get("target_subscription_status"),
            target_client_execution_allowed=runtime_update.get("target_client_execution_allowed"),
            target_credit_action=runtime_update.get("target_credit_action"),
            preserve_cycle_anchor=runtime_update.get("preserve_cycle_anchor", True),
            retry_interval_hours=runtime_update.get("retry_interval_hours"),
            cancel_at_period_end=runtime_update.get("cancel_at_period_end"),
        )
        runtime_update["runtime_mutation_committed"] = bool(mutation.get("mutation_committed"))
        runtime_update["durable_billing_mutation"] = mutation
    else:
        runtime_update["durable_billing_mutation"] = {
            "success": False,
            "mutation_committed": False,
            "reason": "tenant_not_resolved",
        }

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

if "from backend.app.core.durable_billing_state_store import get_billing_runtime_state" not in routes_text:
    routes_text = routes_text.replace(
        "from backend.app.core.stripe_tenant_mapping_store import (\n",
        "from backend.app.core.durable_billing_state_store import get_billing_runtime_state\n\n"
        "from backend.app.core.stripe_tenant_mapping_store import (\n",
    )

if "@router.get(\"/admin/billing/durable-runtime-state\")" not in routes_text:
    routes_text += r'''


@router.get("/admin/billing/durable-runtime-state")
def admin_billing_durable_runtime_state(
    x_actor_role: Optional[str] = Header(default=None),
    tenant_id: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return get_billing_runtime_state(tenant_id=tenant_id, limit=limit)
'''

routes_file.write_text(routes_text, encoding="utf-8")

print("STEP_204_DURABLE_WEBHOOK_BILLING_MUTATION_INSTALLED")
print(f"Created/updated: {billing_state_file}")
print(f"Updated: {bridge_file}")
print(f"Updated: {routes_file}")
print("STEP_204_OK")