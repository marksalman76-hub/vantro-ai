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
