import json
import urllib.request

BASE = "http://127.0.0.1:8000"

checks = {}

def get_json(path):
    req = urllib.request.Request(
        BASE + path,
        headers={"x-actor-role": "owner", "x-tenant-id": "owner"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))

health = get_json("/health")
checks["health_running"] = health.get("success") is True and health.get("status") == "running"

policy = get_json("/admin/billing/subscription-policy-summary")
checks["billing_policy_available"] = policy.get("success") is True
checks["month_to_month"] = policy.get("policy", {}).get("contract_type") == "month_to_month"
checks["retry_48_hours"] = policy.get("policy", {}).get("failed_payment_retry_interval_hours") == 48
checks["owner_admin_credit_bypass"] = policy.get("policy", {}).get("owner_admin_credit_bypass") is True

billing_state = get_json("/admin/billing/durable-runtime-state?tenant_id=client_step203_001")
state = billing_state.get("state") or {}
checks["durable_billing_state_available"] = billing_state.get("success") is True
checks["billing_state_past_due"] = state.get("subscription_status") == "past_due"
checks["billing_client_execution_blocked"] = state.get("client_execution_allowed") is False

provider_readiness = get_json("/admin/provider-readiness")
provider_text = json.dumps(provider_readiness).lower()

checks["provider_readiness_route_available"] = provider_readiness.get("success") is True
checks["provider_values_not_exposed"] = all(secret not in provider_text for secret in [
    "sk-",
    "ecomagentsecure",
    "postgresql://",
    "supabase.com:5432",
])

print("STEP_216_PROVIDER_BILLING_READINESS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_216_PROVIDER_BILLING_READINESS_LOCK_OK")