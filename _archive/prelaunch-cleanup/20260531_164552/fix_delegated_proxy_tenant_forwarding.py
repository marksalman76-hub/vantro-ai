from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"

backup_dir = ROOT / "backups" / f"delegated_proxy_tenant_forwarding_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

text = text.replace(
    '"x-tenant-id": "owner_admin",',
    '"x-tenant-id": body.tenant_id || "owner_admin",'
)

text = text.replace(
    'connected_integrations: body.connected_integrations || [],',
    'connected_integrations: body.connected_integrations || [],\n      tenant_id: body.tenant_id || "owner_admin",'
)

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_delegated_proxy_tenant_forwarding.py"
test_file.write_text(r'''
from pathlib import Path

text = Path("frontend/src/app/api/delegated-workforce-execution/route.ts").read_text(encoding="utf-8")

assert '"x-tenant-id": body.tenant_id || "owner_admin"' in text
assert 'tenant_id: body.tenant_id || "owner_admin"' in text
assert 'connected_integrations: body.connected_integrations || []' in text

print("DELEGATED_PROXY_TENANT_FORWARDING_TEST_PASSED")
''', encoding="utf-8")

print("DELEGATED_PROXY_TENANT_FORWARDING_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")