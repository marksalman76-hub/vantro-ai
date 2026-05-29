from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"
main_file = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"delegated_runtime_tenant_passthrough_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(runtime_file, backup_dir / runtime_file.name)
shutil.copy2(main_file, backup_dir / main_file.name)

runtime = runtime_file.read_text(encoding="utf-8")
main = main_file.read_text(encoding="utf-8")

old_sig = '''    package_tier: str = "starter",
    connected_integrations: List[str] | None = None,
) -> Dict[str, Any]:
'''

new_sig = '''    package_tier: str = "starter",
    connected_integrations: List[str] | None = None,
    tenant_id: str = "owner_admin",
) -> Dict[str, Any]:
'''

if old_sig not in runtime:
    raise SystemExit("RUNTIME_SIGNATURE_BLOCK_NOT_FOUND")

runtime = runtime.replace(old_sig, new_sig, 1)

runtime = runtime.replace(
    'tenant_id="owner_admin" if enterprise_access else "client",',
    'tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),'
)

runtime = runtime.replace(
    'tenant_id="owner_admin" if enterprise_access else "client",',
    'tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),'
)

runtime = runtime.replace(
    'tenant_id="owner_admin" if enterprise_access else "client",',
    'tenant_id=tenant_id or ("owner_admin" if enterprise_access else "client"),'
)

runtime_file.write_text(runtime, encoding="utf-8")

old_main_call = '''        client_owned_agents=payload.get("client_owned_agents", []),
        package_tier=payload.get("package_tier", "starter"),
        connected_integrations=payload.get("connected_integrations", []),
    )
'''

new_main_call = '''        client_owned_agents=payload.get("client_owned_agents", []),
        package_tier=payload.get("package_tier", "starter"),
        connected_integrations=payload.get("connected_integrations", []),
        tenant_id=payload.get("tenant_id") or "owner_admin",
    )
'''

if old_main_call not in main:
    raise SystemExit("MAIN_DELEGATED_CALL_BLOCK_NOT_FOUND")

main = main.replace(old_main_call, new_main_call, 1)
main_file.write_text(main, encoding="utf-8")

test_file = ROOT / "test_delegated_runtime_tenant_passthrough.py"
test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan

plan = {
    "action_packets": [
        {
            "packet_id": "tenant_passthrough_001",
            "recommended_agent": "email_reply_agent",
            "title": "Send governed live Brevo execution verification email",
            "risk_level": "medium",
            "approval_required": False,
        }
    ]
}

runtime_result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=True,
    client_owned_agents=["email_reply_agent"],
    package_tier="enterprise",
    connected_integrations=["email"],
    tenant_id="client_demo_001",
)

assert runtime_result["success"] is True
completed = runtime_result["completed_results"][0]
assert completed["deliverable"]["actions_performed"][0]["tenant_id"] == "client_demo_001"

client = TestClient(app)
response = client.post(
    "/delegated-workforce-execution",
    json={
        "implementation_plan": plan,
        "owner_approved": True,
        "client_owned_agents": ["email_reply_agent"],
        "package_tier": "enterprise",
        "connected_integrations": ["email"],
        "tenant_id": "client_demo_001",
    },
)

body = response.json()
assert body["success"] is True
completed_route = body["completed_results"][0]
assert completed_route["deliverable"]["actions_performed"][0]["tenant_id"] == "client_demo_001"

print("DELEGATED_RUNTIME_TENANT_PASSTHROUGH_TEST_PASSED")
''', encoding="utf-8")

print("DELEGATED_RUNTIME_TENANT_ID_PASSTHROUGH_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Updated: {main_file}")
print(f"Created: {test_file}")