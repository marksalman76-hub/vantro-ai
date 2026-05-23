from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME = ROOT / "backend" / "app" / "core" / "saas_provisioning_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for path in [MAIN, RUNTIME]:
    if not path.exists():
        raise FileNotFoundError(path)

main_backup = BACKUP_DIR / f"main_before_priority8_tenant_bootstrap_route_fix_{timestamp}.py"
runtime_backup = BACKUP_DIR / f"saas_runtime_before_priority8_tenant_bootstrap_route_fix_{timestamp}.py"

main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")
runtime_backup.write_text(RUNTIME.read_text(encoding="utf-8"), encoding="utf-8")

runtime_text = RUNTIME.read_text(encoding="utf-8")

bad_block = '''@router.post("/tenant-bootstrap")
def tenant_bootstrap_endpoint(payload: Dict[str, Any]):
    return retrieve_tenant_bootstrap(payload)
'''

runtime_text = runtime_text.replace(bad_block, "")
RUNTIME.write_text(runtime_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

old_import = "from backend.app.core.saas_provisioning_runtime import provisioning_readiness, provision_tenant, validate_one_time_link"
new_import = "from backend.app.core.saas_provisioning_runtime import provisioning_readiness, provision_tenant, validate_one_time_link, retrieve_tenant_bootstrap"

if old_import in main_text:
    main_text = main_text.replace(old_import, new_import)
elif "retrieve_tenant_bootstrap" not in main_text:
    raise RuntimeError("Could not safely update saas_provisioning_runtime import in main.py")

route_block = '''

@app.post("/admin/saas-provisioning/tenant-bootstrap")
def admin_saas_provisioning_tenant_bootstrap(payload: dict):
    return retrieve_tenant_bootstrap(payload)
'''

if "/admin/saas-provisioning/tenant-bootstrap" not in main_text:
    main_text = main_text.rstrip() + "\n" + route_block + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("PRIORITY8_TENANT_BOOTSTRAP_ROUTE_WIRED")
print(f"Main backup: {main_backup}")
print(f"Runtime backup: {runtime_backup}")
print("Route: /admin/saas-provisioning/tenant-bootstrap")