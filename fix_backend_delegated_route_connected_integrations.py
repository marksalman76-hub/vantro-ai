from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"backend_delegated_route_connected_integrations_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old = '''        client_owned_agents=payload.get("client_owned_agents", []),
        package_tier=payload.get("package_tier", "starter"),
    )
'''

new = '''        client_owned_agents=payload.get("client_owned_agents", []),
        package_tier=payload.get("package_tier", "starter"),
        connected_integrations=payload.get("connected_integrations", []),
    )
'''

if old not in text:
    raise SystemExit("DELEGATED_ROUTE_CALL_BLOCK_NOT_FOUND")

text = text.replace(old, new, 1)
target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_backend_delegated_route_connected_integrations.py"
test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

response = client.post(
    "/delegated-workforce-execution",
    json={
        "implementation_plan": {
            "action_packets": [
                {
                    "packet_id": "route_connected_001",
                    "recommended_agent": "marketing_specialist_agent",
                    "title": "Commission targeted healthcare technology market research and client interviews",
                    "risk_level": "medium",
                    "approval_required": False,
                }
            ]
        },
        "owner_approved": False,
        "client_owned_agents": ["marketing_specialist_agent"],
        "package_tier": "enterprise",
        "connected_integrations": ["email", "crm", "calendar"],
    },
)

body = response.json()
assert body["success"] is True
assert body["connected_integrations"] == ["email", "crm", "calendar"]
assert body["external_integration_count"] == 3
assert body["completed_count"] == 1

completed = body["completed_results"][0]
assert completed["external_action_performed"] is True
assert completed["live_external_call_executed"] is True

print("BACKEND_DELEGATED_ROUTE_CONNECTED_INTEGRATIONS_TEST_PASSED")
''', encoding="utf-8")

print("BACKEND_DELEGATED_ROUTE_CONNECTED_INTEGRATIONS_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")