from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"main_before_real_provider_adapter_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(MAIN, backup)

s = MAIN.read_text(encoding="utf-8")

import_block = (
    "from backend.app.runtime.real_provider_adapter_layer import "
    "get_provider_adapter_status, normalise_provider_request, route_provider_request, execute_provider_request_scaffold\n"
)

if import_block not in s:
    marker = "from backend.app.runtime.async_provider_job_runtime import"
    idx = s.find(marker)
    if idx != -1:
        line_end = s.find("\n", idx)
        s = s[:line_end+1] + import_block + s[line_end+1:]
    else:
        fastapi_idx = s.find("from fastapi import")
        line_end = s.find("\n", fastapi_idx)
        s = s[:line_end+1] + import_block + s[line_end+1:]

route_block = r'''

@app.get("/admin/provider-adapters/status/{provider_key}")
def admin_provider_adapter_status(provider_key: str):
    return get_provider_adapter_status(provider_key)


@app.post("/admin/provider-adapters/normalise")
def admin_provider_adapter_normalise(payload: dict):
    return normalise_provider_request(payload)


@app.post("/admin/provider-adapters/route")
def admin_provider_adapter_route(payload: dict):
    return route_provider_request(payload)


@app.post("/admin/provider-adapters/execute-scaffold")
def admin_provider_adapter_execute_scaffold(payload: dict):
    return execute_provider_request_scaffold(payload)
'''

if '"/admin/provider-adapters/status/{provider_key}"' not in s:
    s += route_block

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_real_provider_adapter_admin_routes.py"
test.write_text(r'''from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = [
    "/admin/provider-adapters/status/{provider_key}",
    "/admin/provider-adapters/normalise",
    "/admin/provider-adapters/route",
    "/admin/provider-adapters/execute-scaffold",
]

missing = [route for route in required if route not in routes]
assert not missing, f"Missing routes: {missing}"

print("REAL_PROVIDER_ADAPTER_ADMIN_ROUTES_TEST_PASSED")
for route in required:
    print(route)
''', encoding="utf-8")

print("REAL_PROVIDER_ADAPTER_ADMIN_ROUTES_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test}")