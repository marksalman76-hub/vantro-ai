import json
import urllib.request

BASE = "http://127.0.0.1:8000"
TENANT_ID = "client_step203_001"
CUSTOMER_ID = "cus_step203_001"
SUBSCRIPTION_ID = "sub_step203_001"


def request_json(path, method="GET", payload=None):
    data = None
    headers = {
        "Content-Type": "application/json",
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
    }

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers=headers,
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


def stripe_event(event_type, status):
    return {
        "type": event_type,
        "data": {
            "object": {
                "customer": CUSTOMER_ID,
                "subscription": SUBSCRIPTION_ID,
                "billing_reason": "subscription_cycle",
                "status": status,
                "current_period_start": 1767225600,
                "current_period_end": 1769904000,
            }
        },
    }


print("STEP_217_STRIPE_WEBHOOK_LIFECYCLE_LOCK_RESULTS")

failed = []

failed_event = request_json(
    "/webhooks/stripe/hardened",
    method="POST",
    payload=stripe_event("invoice.payment_failed", "open"),
)

failed_state = request_json(f"/admin/billing/durable-runtime-state?tenant_id={TENANT_ID}")
failed_tenant_state = failed_state.get("state") or {}

checks_failed = {
    "failed_event_success": failed_event.get("success") is True,
    "failed_event_committed": failed_event.get("billing_runtime_update", {}).get("runtime_mutation_committed") is True,
    "failed_subscription_past_due": failed_tenant_state.get("subscription_status") == "past_due",
    "failed_execution_blocked": failed_tenant_state.get("client_execution_allowed") is False,
    "failed_credit_blocked": failed_tenant_state.get("credit_state") == "blocked",
    "failed_retry_48": failed_tenant_state.get("retry_interval_hours") == 48,
}

success_event = request_json(
    "/webhooks/stripe/hardened",
    method="POST",
    payload=stripe_event("invoice.payment_succeeded", "paid"),
)

success_state = request_json(f"/admin/billing/durable-runtime-state?tenant_id={TENANT_ID}")
success_tenant_state = success_state.get("state") or {}

checks_success = {
    "success_event_success": success_event.get("success") is True,
    "success_event_committed": success_event.get("billing_runtime_update", {}).get("runtime_mutation_committed") is True,
    "success_subscription_active": success_tenant_state.get("subscription_status") == "active",
    "success_execution_allowed": success_tenant_state.get("client_execution_allowed") is True,
    "success_credit_reset_required": success_tenant_state.get("credit_state") == "monthly_credits_reset_required",
}

# Restore state back to past_due so customer-block regression remains valid.
restore_event = request_json(
    "/webhooks/stripe/hardened",
    method="POST",
    payload=stripe_event("invoice.payment_failed", "open"),
)

restore_state = request_json(f"/admin/billing/durable-runtime-state?tenant_id={TENANT_ID}")
restore_tenant_state = restore_state.get("state") or {}

checks_restore = {
    "restore_event_success": restore_event.get("success") is True,
    "restore_subscription_past_due": restore_tenant_state.get("subscription_status") == "past_due",
    "restore_execution_blocked": restore_tenant_state.get("client_execution_allowed") is False,
}

all_checks = {}
all_checks.update(checks_failed)
all_checks.update(checks_success)
all_checks.update(checks_restore)

for name, passed in all_checks.items():
    print(name, passed)
    if not passed:
        failed.append(name)

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_217_STRIPE_WEBHOOK_LIFECYCLE_LOCK_OK")