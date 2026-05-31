import json
import os
import urllib.error
import urllib.request

BASE_URL = "https://app.trance-formation.com.au"
TOKEN = os.getenv("ADMIN_PLATFORM_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError("Set ADMIN_PLATFORM_TOKEN first.")

FAILED_AGENTS = [
    "custom_websites_landing_pages_apps_agent",
    "analytics_intelligence_agent",
    "qa_testing_agent",
    "billing_optimisation_agent",
    "training_learning_agent",
]

for agent_id in FAILED_AGENTS:
    payload = {
        "tenant_id": "client_demo_001",
        "project_id": "default_project",
        "requested_agent": agent_id,
        "workflow_stage": "content_generation",
        "task": f"Create a premium, client-safe execution output for {agent_id}.",
        "region": "Australia",
        "language": "English",
        "currency": "AUD",
        "action_type": "general_ecommerce_agent_output",
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

    print(f"\n===== {agent_id} =====")

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            raw = response.read().decode("utf-8", errors="replace")
            print("HTTP", response.status)
            print(raw[:5000])
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print("HTTP_ERROR", exc.code)
        print(raw[:5000])
    except Exception as exc:
        print("ERROR", repr(exc))