from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"main_before_non_conflicting_provider_adapter_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(MAIN, backup)

s = MAIN.read_text(encoding="utf-8")

route = '''
@app.get("/admin/unified-provider-adapter-status/{provider_key}")
def admin_unified_provider_adapter_status(provider_key: str):
    return get_provider_adapter_status(provider_key)
'''

if '"/admin/unified-provider-adapter-status/{provider_key}"' not in s:
    s += "\n" + route

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_non_conflicting_provider_adapter_status_route.py"
test.write_text(r'''from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = "/admin/unified-provider-adapter-status/{provider_key}"
assert required in routes, f"Missing route: {required}"

print("NON_CONFLICTING_PROVIDER_ADAPTER_STATUS_ROUTE_TEST_PASSED")
print(required)
''', encoding="utf-8")

print("NON_CONFLICTING_PROVIDER_ADAPTER_STATUS_ROUTE_ADDED")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test}")