from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
API = BACKEND / "api"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

bridge_file = CORE / "stripe_billing_runtime_bridge.py"
routes_file = API / "subscription_policy_routes.py"

for file in [bridge_file, routes_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step202_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

bridge_file.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


EVENT_MEMORY: list[Dict[str, Any]] = []


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_tenant_from_stripe_event(event: Dict[str, Any]) -> str:
    """
    Temporary safe resolver until real Stripe customer/subscription mapping
    is connected to the durable tenant billing table.

    Keeps the bridge deterministic and non-destructive.
    """
    customer_id = event.get("stripe_customer_id")
    subscription_id = event.get("stripe_subscription_id")

    if customer_id:
        return f"stripe_customer::{customer_id}"

    if subscription_id:
        return f"stripe_subscription::{subscription_id}"

    return "stripe_unmapped_tenant"


def apply_stripe_classification_to_billing_runtime(
    event: Dict[str, Any],
    classification: Dict[str, Any],
) -> Dict[str, Any]:
    tenant_reference = resolve_tenant_from_stripe_event(event)
    action = classification.get("action")

    runtime_update = {
        "success": True,
        "tenant_reference": tenant_reference,
        "stripe_customer_id": event.get("stripe_customer_id"),
        "stripe_subscription_id": event.get("stripe_subscription_id"),
        "event_type": event.get("event_type"),
        "classification_action": action,
        "processed_at": utc_now_iso(),
        "durable_runtime_update_mode": "safe_bridge_ready",
        "runtime_mutation_committed": False,
        "reason": "durable_tenant_stripe_mapping_pending",
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

if "from backend.app.core.stripe_billing_runtime_bridge import (" not in routes_text:
    routes_text = routes_text.replace(
        "from backend.app.core.stripe_webhook_hardening import (\n",
        "from backend.app.core.stripe_billing_runtime_bridge import (\n"
        "    apply_stripe_classification_to_billing_runtime,\n"
        "    latest_billing_bridge_events,\n"
        ")\n\n"
        "from backend.app.core.stripe_webhook_hardening import (\n",
    )

old_return = '''    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature_result,
        "event": event,
        "classification": classification,
        "policy": {
            "month_to_month": True,
            "lock_in_contract": False,
            "retry_interval_hours": 48,
            "preserve_original_billing_cycle_on_late_payment": True,
        },
        "processed_at": utc_now_iso(),
    }
'''

new_return = '''    billing_runtime_update = apply_stripe_classification_to_billing_runtime(event, classification)

    return {
        "success": True,
        "route": "/webhooks/stripe/hardened",
        "signature": signature_result,
        "event": event,
        "classification": classification,
        "billing_runtime_update": billing_runtime_update,
        "policy": {
            "month_to_month": True,
            "lock_in_contract": False,
            "retry_interval_hours": 48,
            "preserve_original_billing_cycle_on_late_payment": True,
        },
        "processed_at": utc_now_iso(),
    }
'''

if old_return not in routes_text:
    raise RuntimeError("Expected webhook return block not found. Refusing unsafe partial edit.")

routes_text = routes_text.replace(old_return, new_return)

if "@router.get(\"/admin/billing/webhook-runtime-bridge-events\")" not in routes_text:
    routes_text += r'''


@router.get("/admin/billing/webhook-runtime-bridge-events")
def webhook_runtime_bridge_events(
    x_actor_role: Optional[str] = Header(default=None),
    limit: int = 20,
) -> Dict[str, Any]:
    require_owner(x_actor_role)
    return latest_billing_bridge_events(limit=limit)
'''

routes_file.write_text(routes_text, encoding="utf-8")

print("STEP_202_WEBHOOK_TO_BILLING_RUNTIME_BRIDGE_INSTALLED")
print(f"Created/updated: {bridge_file}")
print(f"Updated: {routes_file}")
print("STEP_202_OK")