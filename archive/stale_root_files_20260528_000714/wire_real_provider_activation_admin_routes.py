from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"main_before_real_provider_activation_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(MAIN, backup)

s = MAIN.read_text(encoding="utf-8")

import_block = "from backend.app.runtime.real_provider_activation_registry import get_all_provider_activation_statuses, get_provider_activation_status, select_ready_provider_for_capability\n"
if import_block not in s:
    insert_after = "from fastapi import"
    idx = s.find(insert_after)
    line_end = s.find("\n", idx)
    s = s[:line_end+1] + import_block + s[line_end+1:]

route_block = r'''

@app.get("/admin/provider-activation/status")
def admin_provider_activation_status():
    return get_all_provider_activation_statuses()


@app.get("/admin/provider-activation/status/{provider_key}")
def admin_provider_activation_single_status(provider_key: str):
    return get_provider_activation_status(provider_key)


@app.get("/admin/provider-activation/select/{capability}")
def admin_provider_activation_select(capability: str):
    return select_ready_provider_for_capability(capability)
'''

if '"/admin/provider-activation/status"' not in s:
    s += route_block

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_real_provider_activation_admin_routes.py"
test.write_text(r'''from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = [
    "/admin/provider-activation/status",
    "/admin/provider-activation/status/{provider_key}",
    "/admin/provider-activation/select/{capability}",
]

missing = [route for route in required if route not in routes]
assert not missing, f"Missing routes: {missing}"

print("REAL_PROVIDER_ACTIVATION_ADMIN_ROUTES_TEST_PASSED")
for route in required:
    print(route)
''', encoding="utf-8")

print("REAL_PROVIDER_ACTIVATION_ADMIN_ROUTES_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test}")