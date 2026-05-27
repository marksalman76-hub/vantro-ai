from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"main_before_provider_adapter_alias_collision_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(MAIN, backup)

s = MAIN.read_text(encoding="utf-8")

alias_import = (
    "from backend.app.runtime.real_provider_adapter_layer import "
    "get_provider_adapter_status as get_unified_provider_adapter_status\n"
)

if alias_import not in s:
    s = alias_import + s

route = '''
@app.get("/provider-adapter-runtime-status/{provider_key}")
def provider_adapter_runtime_status(provider_key: str):
    return get_unified_provider_adapter_status(provider_key)
'''

if '"/provider-adapter-runtime-status/{provider_key}"' not in s:
    s += "\n" + route

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_provider_adapter_runtime_status_route.py"
test.write_text(r'''from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = "/provider-adapter-runtime-status/{provider_key}"
assert required in routes, f"Missing route: {required}"

print("PROVIDER_ADAPTER_RUNTIME_STATUS_ROUTE_TEST_PASSED")
print(required)
''', encoding="utf-8")

print("PROVIDER_ADAPTER_ALIAS_COLLISION_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test}")