from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_provider_bridge_admin_endpoints_import.py"

if not main_file.exists():
    raise FileNotFoundError(f"Missing backend main file: {main_file}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"main_before_provider_bridge_admin_endpoints_{timestamp}.py"
source = main_file.read_text(encoding="utf-8")
backup.write_text(source, encoding="utf-8")

block_marker = "# --- Provider bridge admin diagnostic endpoints ---"

endpoint_block = r'''

# --- Provider bridge admin diagnostic endpoints ---
# Admin/runtime diagnostics only. No secrets are exposed.

@app.get("/admin/provider-connectors/readiness")
async def admin_provider_connectors_readiness():
    from backend.app.runtime.provider_connector_registry import readiness

    return readiness()


@app.get("/admin/provider-bridge/readiness")
async def admin_provider_bridge_readiness():
    from backend.app.runtime.execution_stack import runtime_provider_bridge_readiness

    return runtime_provider_bridge_readiness()


@app.post("/admin/provider-bridge/test-safe-generation")
async def admin_provider_bridge_test_safe_generation(payload: dict | None = None):
    from backend.app.runtime.execution_stack import execute_safe_generation_via_provider_bridge

    payload = payload or {}
    return execute_safe_generation_via_provider_bridge(
        action_type=payload.get("action_type", "marketing_campaign_execution"),
        payload=payload.get("payload", {"test": "provider bridge admin safe-generation test"}),
        tenant_id=payload.get("tenant_id", "owner_admin_test"),
        actor_role=payload.get("actor_role", "owner_admin"),
        preferred_provider=payload.get("preferred_provider", "openai"),
        capability=payload.get("capability"),
    )
'''

if block_marker not in source:
    source = source.rstrip() + endpoint_block + "\n"
    main_file.write_text(source, encoding="utf-8")
    changed = True
else:
    changed = False

test_file.write_text(r'''
from backend.app.main import app


def main():
    routes = sorted([getattr(route, "path", "") for route in app.routes])

    required = [
        "/admin/provider-connectors/readiness",
        "/admin/provider-bridge/readiness",
        "/admin/provider-bridge/test-safe-generation",
    ]

    print("PROVIDER_BRIDGE_ADMIN_ENDPOINT_IMPORT_TEST")
    for route in required:
        print(route, route in routes)
        assert route in routes

    print("PROVIDER_BRIDGE_ADMIN_ENDPOINT_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("PROVIDER_BRIDGE_ADMIN_ENDPOINTS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")
print(f"Changed: {changed}")
print("No secrets exposed. Admin/runtime diagnostics only.")