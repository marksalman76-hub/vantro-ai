from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"

backup_dir = ROOT / "backups" / f"delegated_proxy_connected_integrations_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old = '''      package_tier: body.package_tier || "enterprise",
'''

new = '''      package_tier: body.package_tier || "enterprise",
      connected_integrations: body.connected_integrations || [],
'''

if old not in text:
    raise SystemExit("PACKAGE_TIER_PROXY_BLOCK_NOT_FOUND")

text = text.replace(old, new)

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_delegated_proxy_connected_integrations.py"
test_file.write_text(r'''
from pathlib import Path

p = Path("frontend/src/app/api/delegated-workforce-execution/route.ts")
text = p.read_text(encoding="utf-8")

assert "connected_integrations: body.connected_integrations || []" in text
assert "package_tier: body.package_tier ||" in text

print("DELEGATED_PROXY_CONNECTED_INTEGRATIONS_TEST_PASSED")
''', encoding="utf-8")

print("DELEGATED_PROXY_CONNECTED_INTEGRATIONS_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")