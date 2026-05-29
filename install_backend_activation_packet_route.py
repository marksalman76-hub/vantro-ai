from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"backend_activation_packet_route_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

text = main_file.read_text(encoding="utf-8")

route = r'''

@app.post("/signup-agent-selection/activation-packet")
def signup_agent_selection_activation_packet(payload: dict):
    tenant_id = (
        payload.get("tenant_id")
        or payload.get("tenantId")
        or "client_demo_001"
    )

    plan = str(
        payload.get("plan")
        or payload.get("package_tier")
        or payload.get("package")
        or "starter"
    ).lower()

    if plan not in {"starter", "growth", "business", "enterprise"}:
        plan = "starter"

    package_limits = {
        "starter": 3,
        "growth": 7,
        "business": 10,
        "enterprise": 27,
    }

    raw_agents = (
        payload.get("selected_agents")
        or payload.get("selectedAgents")
        or []
    )

    if not isinstance(raw_agents, list):
        raw_agents = []

    selected_agents = []
    for agent in raw_agents:
        agent_id = str(agent or "").strip()
        if agent_id and agent_id not in selected_agents:
            selected_agents.append(agent_id)

    enterprise_only = {"head_agent", "orchestration_agent"}

    if plan == "enterprise":
        filtered_agents = selected_agents
        enterprise_only_blocked = []
    else:
        filtered_agents = [
            agent for agent in selected_agents
            if agent not in enterprise_only
        ]
        enterprise_only_blocked = [
            agent for agent in selected_agents
            if agent in enterprise_only
        ]

    max_agent_count = package_limits[plan]
    activated_agents = filtered_agents[:max_agent_count]

    return {
        "success": True,
        "profile": "backend_signup_activation_packet_runtime_v1",
        "tenant_id": tenant_id,
        "package_tier": plan,
        "selected_agents": selected_agents,
        "activated_agents": activated_agents,
        "active_agent_count": len(activated_agents),
        "max_agent_count": max_agent_count,
        "enterprise_only_agents_blocked": enterprise_only_blocked,
        "entitlement_status": "activation_packet_ready",
        "activation_status": "ready_for_client_activation",
        "backend_runtime": True,
        "fallback_required": False,
        "customer_safe": True,
        "credential_values_exposed": False,
    }
'''

if '@app.post("/signup-agent-selection/activation-packet")' not in text:
    text = text.rstrip() + "\n" + route + "\n"

main_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_backend_activation_packet_route.py"
test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

response = client.post(
    "/signup-agent-selection/activation-packet",
    json={
        "tenant_id": "client_demo_001",
        "plan": "starter",
        "selected_agents": ["marketing_specialist_agent", "head_agent"],
    },
)

assert response.status_code == 200
body = response.json()

assert body["success"] is True
assert body["profile"] == "backend_signup_activation_packet_runtime_v1"
assert body["tenant_id"] == "client_demo_001"
assert body["package_tier"] == "starter"
assert body["activated_agents"] == ["marketing_specialist_agent"]
assert body["enterprise_only_agents_blocked"] == ["head_agent"]
assert body["fallback_required"] is False
assert body["credential_values_exposed"] is False

print("BACKEND_ACTIVATION_PACKET_ROUTE_TEST_PASSED")
''', encoding="utf-8")

print("BACKEND_ACTIVATION_PACKET_ROUTE_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")