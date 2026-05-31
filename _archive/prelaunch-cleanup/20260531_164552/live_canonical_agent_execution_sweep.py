import json
import os
import time
import urllib.request
from pathlib import Path

from backend.app.agents.agent_registry import ALL_AGENT_IDS, get_agent, normalize_agent_id

BASE_URL = "https://api.trance-formation.com.au"
ORIGIN = "https://trance-formation.com.au"
OUT_DIR = Path("reports/live_agent_execution_sweep")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOKEN = os.environ.get("ADMIN_PLATFORM_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError("Set ADMIN_PLATFORM_TOKEN first.")

def request_run_agent(agent_id: str):
    agent = get_agent(agent_id)
    role = agent.get("role", "")
    name = agent.get("name", agent_id)

    payload = {
        "tenant_id": "owner_admin",
        "requested_agent": agent_id,
        "workflow_stage": "canonical_all_agent_live_execution_sweep",
        "task": (
            f"You are {name}. Role: {role}. "
            "Produce a real commercial-quality execution result for a premium ecommerce brand. "
            "Make the output specific to your specialist role. Include concrete recommendations, "
            "execution steps, risks, measurable next actions, and what should be reviewed by the owner. "
            "Do not mention testing. Do not return generic filler."
        ),
        "action_type": "governed_live_provider_generation",
        "region": "Global",
        "language": "English",
        "currency": "USD",
        "owner_approved": True,
        "execute_real_world_action": True,
        "project_id": "canonical_all_agent_live_execution_sweep",
        "actor_role": "owner_admin",
        "requested_credits": 1,
    }

    req = urllib.request.Request(
        BASE_URL + "/run-agent",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-admin-token": TOKEN,
            "x-actor-role": "owner_admin",
            "x-tenant-id": "owner_admin",
            "x-csrf-token": "canonical-all-agent-live-execution-sweep",
            "Origin": ORIGIN,
            "x-request-id": f"canonical-all-agent-live-sweep-{agent_id}",
            "x-idempotency-key": f"canonical-all-agent-live-sweep-{agent_id}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        return response.status, json.loads(response.read().decode("utf-8"))

summary = []
full_results = {}
canonical_agents = [normalize_agent_id(agent) for agent in ALL_AGENT_IDS]
canonical_agents = list(dict.fromkeys(canonical_agents))

for i, agent_id in enumerate(canonical_agents, start=1):
    print(f"\n[{i}/{len(canonical_agents)}] Running {agent_id}...")
    started = time.time()

    try:
        status, result = request_run_agent(agent_id)
        elapsed_ms = int((time.time() - started) * 1000)

        execution = result.get("execution") or {}
        adapter_result = execution.get("adapter_result") or {}
        normalised = adapter_result.get("normalised_response") or {}
        safe_output = normalised.get("safe_output") or {}

        row = {
            "agent_id": agent_id,
            "agent_name": get_agent(agent_id).get("name"),
            "visibility": get_agent(agent_id).get("visibility"),
            "http_status": status,
            "success": result.get("success"),
            "run_agent_status": result.get("status"),
            "execution_status": execution.get("execution_status"),
            "adapter": execution.get("adapter"),
            "provider_key": adapter_result.get("provider_key"),
            "provider_status": adapter_result.get("status"),
            "live_external_call_executed": adapter_result.get("live_external_call_executed"),
            "credential_values_exposed": adapter_result.get("credential_values_exposed"),
            "customer_safe": adapter_result.get("customer_safe"),
            "latency_ms": adapter_result.get("latency_ms") or elapsed_ms,
            "memory_saved": (result.get("memory") or {}).get("memory_saved"),
            "sqlite_saved": (result.get("sqlite") or {}).get("sqlite_saved"),
            "output_preview": str(safe_output.get("text") or result.get("output") or "")[:800],
        }

        print(json.dumps(row, indent=2))
        summary.append(row)
        full_results[agent_id] = result

    except Exception as exc:
        row = {
            "agent_id": agent_id,
            "success": False,
            "error": str(exc),
        }
        print(json.dumps(row, indent=2))
        summary.append(row)
        full_results[agent_id] = row

    time.sleep(1)

timestamp = time.strftime("%Y%m%d_%H%M%S")
summary_file = OUT_DIR / f"canonical_agent_live_sweep_summary_{timestamp}.json"
full_file = OUT_DIR / f"canonical_agent_live_sweep_full_{timestamp}.json"

summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
full_file.write_text(json.dumps(full_results, indent=2), encoding="utf-8")

passed = [r for r in summary if r.get("success") is True and r.get("live_external_call_executed") is True]
failed = [r for r in summary if not (r.get("success") is True and r.get("live_external_call_executed") is True)]

print("\nCANONICAL_AGENT_LIVE_EXECUTION_SWEEP_COMPLETE")
print(json.dumps({
    "total_agents": len(canonical_agents),
    "passed_live_execution": len(passed),
    "failed_or_blocked": len(failed),
    "summary_file": str(summary_file),
    "full_file": str(full_file),
    "failed_agents": [r.get("agent_id") for r in failed],
}, indent=2))