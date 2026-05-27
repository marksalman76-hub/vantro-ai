import json
import urllib.request
import urllib.error

API = "http://127.0.0.1:8000/run-agent"

payload = {
    "tenant_id": "client_step203_001",
    "requested_agent": "product_copywriting_agent",
    "workflow_stage": "store_creation",
    "action_type": "product_copy_generation",
    "actor_role": "customer",
    "owner_approved": False,
    "task": "Step 214 verify customer remains blocked while billing state is past_due.",
}

req = urllib.request.Request(
    API,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-tenant-id": "client_step203_001",
        "x-actor-role": "customer",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=30) as res:
        status_code = res.status
        data = json.loads(res.read().decode("utf-8"))
except urllib.error.HTTPError as err:
    status_code = err.code
    data = json.loads(err.read().decode("utf-8"))

checks = {
    "http_402_or_blocked_response": status_code == 402 or data.get("workflow_status") == "billing_blocked",
    "success_false": data.get("success") is False,
    "execution_blocked": data.get("execution_status") == "blocked",
    "workflow_billing_blocked": data.get("workflow_status") == "billing_blocked",
    "reason_past_due": data.get("reason") == "past_due",
    "guard_applied": data.get("billing_guard", {}).get("billing_guard_applied") is True,
    "client_execution_false": data.get("billing_guard", {}).get("client_execution_allowed") is False,
    "credit_state_blocked": data.get("billing_guard", {}).get("credit_state") == "blocked",
}

failed = [name for name, passed in checks.items() if not passed]

print("STEP_214_CUSTOMER_BILLING_BLOCK_LOCK_RESULTS")
print("http_status", status_code)
for name, passed in checks.items():
    print(name, passed)

if failed:
    print("FAILED", failed)
    print(json.dumps(data, indent=2))
    raise SystemExit(1)

print("STEP_214_CUSTOMER_BILLING_BLOCK_LOCK_OK")