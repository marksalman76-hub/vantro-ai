import json
import os
import urllib.error
import urllib.request

BASE_URL = "https://app.trance-formation.com.au"
TOKEN = os.getenv("ADMIN_PLATFORM_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError("Set ADMIN_PLATFORM_TOKEN first.")

payload = {
    "tenant_id": "client_demo_001",
    "project_id": "default_project",
    "requested_agent": "qa_testing_agent",
    "workflow_stage": "quality_assurance",
    "task": "Run a premium QA readiness check for the unique multi-agent platform and produce a client-safe test summary.",
    "region": "Australia",
    "language": "English",
    "currency": "AUD",
    "action_type": "qa_testing_generation",
    "execute_real_world_action": True,
    "owner_approved": True,
    "actor_role": "owner_admin",
    "requested_credits": 1,
}

req = urllib.request.Request(
    f"{BASE_URL}/api/run-agent",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "x-admin-token": TOKEN,
        "x-actor-role": "owner_admin",
        "x-tenant-id": "owner_admin",
        "Origin": "https://app.trance-formation.com.au",
        "Referer": "https://app.trance-formation.com.au/admin",
        "User-Agent": "Mozilla/5.0",
    },
    method="POST",
)

print("QA_AGENT_TEST_START")

try:
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read().decode("utf-8", errors="replace")
        print("HTTP", response.status)
        print(raw[:8000])
except urllib.error.HTTPError as exc:
    raw = exc.read().decode("utf-8", errors="replace")
    print("HTTP_ERROR", exc.code)
    print(raw[:8000])
except Exception as exc:
    print("ERROR", repr(exc))