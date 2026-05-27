import json
import urllib.request

API = "http://127.0.0.1:8000/run-agent"

payload = {
    "tenant_id": "client_step203_001",
    "requested_agent": "product_copywriting_agent",
    "workflow_stage": "store_creation",
    "action_type": "product_copy_generation",
    "actor_role": "owner",
    "owner_approved": True,
    "task": "Create premium skincare serum product copy with luxury positioning, emotional hooks, objection handling, conversion bullets, SEO title, meta description and high-converting CTA.",
}

req = urllib.request.Request(
    API,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-tenant-id": "client_step203_001",
        "x-actor-role": "owner",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=30) as res:
    data = json.loads(res.read().decode("utf-8"))

checks = {
    "success_true": data.get("success") is True,
    "completed": data.get("status") == "agent_execution_completed",
    "approval_passed": data.get("approval", {}).get("approved") is True,
    "quality_passed": data.get("quality", {}).get("passed") is True,
    "execution_prepared": data.get("execution", {}).get("execution_status") == "adapter_prepared",
    "shopify_adapter": data.get("execution", {}).get("adapter") == "shopify_adapter",
    "memory_saved": data.get("memory", {}).get("memory_saved") is True,
    "sqlite_saved": data.get("sqlite", {}).get("sqlite_saved") is True,
    "client_safe": data.get("output", {}).get("client_safe") is True,
    "provider_blocked_safely": data.get("output", {}).get("provider_execution", {}).get("metadata", {}).get("live_execution_allowed") is False,
}

failed = [name for name, passed in checks.items() if not passed]

print("STEP_213_OWNER_SUCCESSFUL_EXECUTION_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_213_OWNER_SUCCESSFUL_EXECUTION_LOCK_OK")