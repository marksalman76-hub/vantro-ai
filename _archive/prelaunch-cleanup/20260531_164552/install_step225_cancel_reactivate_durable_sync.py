from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ROUTES = ROOT / "backend" / "app" / "api" / "subscription_policy_routes.py"
TEST = ROOT / "test_step225_cancel_reactivate_durable_sync_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"subscription_policy_routes_before_step225_{timestamp}.py"
backup.write_text(ROUTES.read_text(encoding="utf-8"), encoding="utf-8")

text = ROUTES.read_text(encoding="utf-8")

if "apply_billing_runtime_mutation" not in text:
    text = text.replace(
        "from backend.app.core.durable_billing_state_store import get_billing_runtime_state",
        "from backend.app.core.durable_billing_state_store import get_billing_runtime_state, apply_billing_runtime_mutation",
    )

old_cancel = '''    return {
        "success": True,
        "route": "/admin/billing/cancel-subscription",
        "tenant_id": payload.tenant_id,
        "subscription_id": payload.subscription_id,
        "requested_action": "cancel_at_period_end" if payload.cancel_at_period_end else "cancel_immediately",
        "month_to_month": True,
        "lock_in_contract": False,
        "client_execution_after_period_end": "blocked_unless_reactivated_or_new_subscription_active",
        "owner_admin_access": "unaffected",
        "reason": payload.reason,
        "recorded_at": utc_now_iso(),
    }
'''

new_cancel = '''    recorded_at = utc_now_iso()
    requested_action = "cancel_at_period_end" if payload.cancel_at_period_end else "cancel_immediately"

    durable_billing_mutation = apply_billing_runtime_mutation(
        tenant_id=payload.tenant_id,
        event_type="customer.subscription.cancel_requested",
        stripe_customer_id=None,
        stripe_subscription_id=payload.subscription_id,
        target_subscription_status="cancel_at_period_end" if payload.cancel_at_period_end else "cancelled",
        target_client_execution_allowed=True if payload.cancel_at_period_end else False,
        target_credit_action="allow_until_period_end" if payload.cancel_at_period_end else "block_credit_consuming_execution",
        processed_at=recorded_at,
        preserve_cycle_anchor=True,
        retry_interval_hours=48,
    )

    return {
        "success": True,
        "route": "/admin/billing/cancel-subscription",
        "tenant_id": payload.tenant_id,
        "subscription_id": payload.subscription_id,
        "requested_action": requested_action,
        "month_to_month": True,
        "lock_in_contract": False,
        "client_execution_after_period_end": "blocked_unless_reactivated_or_new_subscription_active",
        "owner_admin_access": "unaffected",
        "reason": payload.reason,
        "durable_billing_mutation": durable_billing_mutation,
        "recorded_at": recorded_at,
    }
'''

old_reactivate = '''    return {
        "success": True,
        "route": "/admin/billing/reactivate-subscription",
        "tenant_id": payload.tenant_id,
        "subscription_id": payload.subscription_id,
        "requested_action": "reactivate_subscription",
        "billing_cycle_rule": "preserve_original_cycle_anchor_where_available",
        "client_execution": "allowed_after_active_subscription_and_credit_state_verified",
        "owner_admin_access": "unaffected",
        "reason": payload.reason,
        "recorded_at": utc_now_iso(),
    }
'''

new_reactivate = '''    recorded_at = utc_now_iso()

    durable_billing_mutation = apply_billing_runtime_mutation(
        tenant_id=payload.tenant_id,
        event_type="customer.subscription.reactivate_requested",
        stripe_customer_id=None,
        stripe_subscription_id=payload.subscription_id,
        target_subscription_status="active",
        target_client_execution_allowed=True,
        target_credit_action="preserve_or_restore_credit_access",
        processed_at=recorded_at,
        preserve_cycle_anchor=True,
        retry_interval_hours=48,
    )

    return {
        "success": True,
        "route": "/admin/billing/reactivate-subscription",
        "tenant_id": payload.tenant_id,
        "subscription_id": payload.subscription_id,
        "requested_action": "reactivate_subscription",
        "billing_cycle_rule": "preserve_original_cycle_anchor_where_available",
        "client_execution": "allowed_after_active_subscription_and_credit_state_verified",
        "owner_admin_access": "unaffected",
        "reason": payload.reason,
        "durable_billing_mutation": durable_billing_mutation,
        "recorded_at": recorded_at,
    }
'''

if old_cancel not in text:
    raise RuntimeError("Expected cancel route return block not found.")

if old_reactivate not in text:
    raise RuntimeError("Expected reactivate route return block not found.")

text = text.replace(old_cancel, new_cancel)
text = text.replace(old_reactivate, new_reactivate)

ROUTES.write_text(text, encoding="utf-8")

TEST.write_text(r'''
import json
import urllib.request

BASE = "http://127.0.0.1:8000"
TENANT_ID = "client_step225_001"
SUB_ID = "sub_step225_001"


def request_json(path, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


cancel = request_json(
    "/admin/billing/cancel-subscription",
    method="POST",
    payload={
        "tenant_id": TENANT_ID,
        "subscription_id": SUB_ID,
        "cancel_at_period_end": True,
        "reason": "Step 225 cancel at period end regression",
    },
)

cancel_state = request_json(f"/admin/billing/durable-runtime-state?tenant_id={TENANT_ID}")
cancel_state_data = cancel_state.get("state") or {}

reactivate = request_json(
    "/admin/billing/reactivate-subscription",
    method="POST",
    payload={
        "tenant_id": TENANT_ID,
        "subscription_id": SUB_ID,
        "reason": "Step 225 reactivate regression",
    },
)

reactivate_state = request_json(f"/admin/billing/durable-runtime-state?tenant_id={TENANT_ID}")
reactivate_state_data = reactivate_state.get("state") or {}

checks = {
    "cancel_success": cancel.get("success") is True,
    "cancel_mutation_committed": cancel.get("durable_billing_mutation", {}).get("mutation_committed") is True,
    "cancel_status_period_end": cancel_state_data.get("subscription_status") == "cancel_at_period_end",
    "cancel_preserves_client_access_until_period_end": cancel_state_data.get("client_execution_allowed") is True,
    "cancel_credit_action": cancel_state_data.get("credit_action") == "allow_until_period_end",
    "reactivate_success": reactivate.get("success") is True,
    "reactivate_mutation_committed": reactivate.get("durable_billing_mutation", {}).get("mutation_committed") is True,
    "reactivate_status_active": reactivate_state_data.get("subscription_status") == "active",
    "reactivate_client_execution_allowed": reactivate_state_data.get("client_execution_allowed") is True,
    "reactivate_preserve_cycle_anchor": reactivate_state_data.get("preserve_cycle_anchor") is True,
}

print("STEP_225_CANCEL_REACTIVATE_DURABLE_SYNC_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "cancel": cancel,
        "cancel_state": cancel_state,
        "reactivate": reactivate,
        "reactivate_state": reactivate_state,
    }, indent=2))
    raise SystemExit(1)

print("STEP_225_CANCEL_REACTIVATE_DURABLE_SYNC_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(ROUTES), doraise=True)
py_compile.compile(str(TEST), doraise=True)

print("STEP_225_CANCEL_REACTIVATE_DURABLE_SYNC_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {ROUTES}")
print(f"Created/updated: {TEST}")
print("STEP_225_OK")