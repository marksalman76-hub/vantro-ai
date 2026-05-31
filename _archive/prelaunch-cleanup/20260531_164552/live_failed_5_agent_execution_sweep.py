import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

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

results = []

for index, agent_id in enumerate(FAILED_AGENTS, start=1):
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
        },
        method="POST",
    )

    print(f"\n[{index}/5] Running {agent_id}...")

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
            data = body.get("data") if isinstance(body.get("data"), dict) else body

            execution = data.get("execution") or {}
            result = {
                "agent_id": agent_id,
                "http_status": response.status,
                "success": data.get("success"),
                "run_agent_status": data.get("status"),
                "execution_status": execution.get("execution_status"),
                "adapter": execution.get("adapter"),
                "provider_key": execution.get("provider_key"),
                "provider_status": execution.get("provider_status"),
                "live_external_call_executed": execution.get("live_external_call_executed"),
                "credential_values_exposed": execution.get("credential_values_exposed"),
                "customer_safe": execution.get("customer_safe"),
                "memory_saved": bool(data.get("memory", {}).get("memory_saved")),
                "sqlite_saved": bool(data.get("sqlite", {}).get("sqlite_saved")),
                "output_preview": str(
                    data.get("output", {}).get("generated_output")
                    or data.get("output", {}).get("content")
                    or data.get("output", "")
                )[:500],
            }
    except Exception as exc:
        result = {
            "agent_id": agent_id,
            "success": False,
            "error": str(exc),
        }

    print(json.dumps(result, indent=2))
    results.append(result)

passed = [
    r for r in results
    if r.get("success") is True
    and r.get("execution_status") == "governed_live_provider_execution_completed"
    and r.get("live_external_call_executed") is True
]

failed = [r for r in results if r not in passed]

report_dir = Path("reports/live_agent_execution_sweep")
report_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_file = report_dir / f"failed_5_agent_live_sweep_{stamp}.json"
report_file.write_text(json.dumps({"passed": passed, "failed": failed, "results": results}, indent=2), encoding="utf-8")

print("\nFAILED_5_AGENT_LIVE_EXECUTION_SWEEP_COMPLETE")
print(json.dumps({
    "total_agents": len(FAILED_AGENTS),
    "passed_live_execution": len(passed),
    "failed_or_blocked": len(failed),
    "report_file": str(report_file),
}, indent=2))