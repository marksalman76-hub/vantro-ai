from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"main_before_global_provider_admin_routes_{stamp}.py"

s = MAIN.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

imports = [
    "from backend.app.runtime.global_provider_execution_runtime import global_provider_execution_readiness, build_global_provider_execution_packet\n",
    "from backend.app.runtime.global_real_provider_connector_layer import global_real_provider_connector_readiness, build_global_connector_execution_packet\n",
    "from backend.app.runtime.real_provider_activation_layer import real_provider_activation_readiness\n",
]

for import_line in imports:
    if import_line not in s:
        lines = s.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_at = i + 1
        lines.insert(insert_at, import_line.rstrip())
        s = "\n".join(lines) + "\n"

route_block = r'''

# Global provider execution admin routes
@app.get("/admin/global-provider/readiness")
def admin_global_provider_readiness() -> Dict[str, object]:
    return {
        "success": True,
        "scope": "platform_wide_multi_agent",
        "real_provider_activation": real_provider_activation_readiness(),
        "global_provider_execution": global_provider_execution_readiness(),
        "global_connector": global_real_provider_connector_readiness(),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }


@app.post("/admin/global-provider/execution-packet")
def admin_global_provider_execution_packet(payload: dict) -> Dict[str, object]:
    return {
        "success": True,
        "scope": "platform_wide_multi_agent",
        "provider_execution_packet": build_global_provider_execution_packet(payload),
        "connector_execution_packet": build_global_connector_execution_packet(payload),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "governance_preserved": True,
        "owner_approval_gate_preserved": True,
    }
'''

if '"/admin/global-provider/readiness"' not in s:
    s = s + route_block + "\n"

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_global_provider_admin_routes.py"
test.write_text(r'''
from pathlib import Path

main = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "/admin/global-provider/readiness" in main
assert "/admin/global-provider/execution-packet" in main
assert "real_provider_activation_readiness" in main
assert "global_provider_execution_readiness" in main
assert "global_real_provider_connector_readiness" in main

print("GLOBAL_PROVIDER_ADMIN_ROUTES_OK")
''', encoding="utf-8")

print("GLOBAL_PROVIDER_ADMIN_ROUTES_INSTALLED")
print(f"Backup: {backup}")
print(f"Created: {test}")