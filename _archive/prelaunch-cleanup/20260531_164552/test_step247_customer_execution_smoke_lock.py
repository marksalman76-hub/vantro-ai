import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://127.0.0.1:8000"
ROOT = Path.cwd()

record_path = ROOT / "backend" / "app" / "data" / "step247_customer_execution_smoke_lock.json"
record = json.loads(record_path.read_text(encoding="utf-8"))


def post_json(path, payload, headers=None):
    req_headers = {
        "Content-Type": "application/json",
        "x-actor-role": "customer",
        "x-tenant-id": payload.get("tenant_id", "client_step245_smoke"),
    }

    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body}
        return exc.code, data



def assign_credits(tenant_id: str):
    payload = {
        "tenant_id": tenant_id,
        "monthly_credits": 25,
        "credits_used": 0,
        "reason": "Step 247 customer execution smoke test credit allocation.",
    }

    req = urllib.request.Request(
        BASE + "/admin/assign-client-credits",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body}
        return exc.code, data


tenant_id = "client_step245_smoke"

credit_status, credit_result = assign_credits(tenant_id)

payload = {
    "tenant_id": tenant_id,
    "requested_agent": "product_copywriting_agent",
    "workflow_stage": "store_creation",
    "task": "Create a premium Shopify product page for a high-converting skincare serum targeting women aged 25 to 40 in Australia. Include conversion-focused benefits, objections, offer angle, product description, and ad-ready product positioning.",
    "action_type": "product_copy_generation",
    "region": "Australia",
    "language": "English",
    "currency": "AUD",
    "owner_approved": False,
    "execute_real_world_action": True,
    "project_id": "step247_customer_execution_smoke",
    "actor_role": "customer",
    "requested_credits": 1,
}

status, result = post_json("/run-agent", payload)

combined = json.dumps({
    "record": record,
    "result": result,
}).lower()

output = result.get("output") or {}
workflow = result.get("workflow") or {}
quality = result.get("quality") or {}
execution = result.get("execution") or {}

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "customer_execution_smoke_requirements_locked",
    "credit_assignment_success": credit_status in {200, 201} and credit_result.get("success") is True,
    "run_agent_status_controlled": status in {200, 402, 403, 422},
    "run_agent_success": result.get("success") is True,
    "workflow_present": isinstance(workflow, dict) and bool(workflow),
    "quality_passed": quality.get("passed") is True,
    "output_present": isinstance(output, dict) and bool(output),
    "client_safe_output": output.get("client_safe") is True,
    "premium_output_type_present": bool(output.get("output_type")),
    "execution_present": isinstance(execution, dict) and bool(execution),
    "provider_safely_governed": "provider_execution" in json.dumps(output),
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_247_CUSTOMER_EXECUTION_SMOKE_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("credit_status", credit_status)
print("credit_assigned", credit_result.get("success") if isinstance(credit_result, dict) else None)
print("http_status", status)
print("workflow_status", result.get("status"))
print("output_type", output.get("output_type"))
print("execution_status", execution.get("execution_status") if isinstance(execution, dict) else None)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(result, indent=2))
    raise SystemExit(1)

print("STEP_247_CUSTOMER_EXECUTION_SMOKE_LOCK_OK")
