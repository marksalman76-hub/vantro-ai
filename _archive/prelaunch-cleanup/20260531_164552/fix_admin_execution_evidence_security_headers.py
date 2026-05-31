from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "frontend" / "src" / "app" / "api" / "admin-execution-evidence" / "route.ts"

backup_dir = ROOT / "backups" / f"admin_execution_evidence_security_headers_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old_headers = '''    headers: {
      "x-admin-token": ADMIN_TOKEN,
      "x-actor-role": "owner_admin",
      "x-tenant-id": tenantId || "owner_admin",
    },
'''

new_headers = '''    headers: {
      "Content-Type": "application/json",
      "x-admin-token": ADMIN_TOKEN,
      "Authorization": `Bearer ${ADMIN_TOKEN}`,
      "x-actor-role": "owner_admin",
      "x-tenant-id": tenantId || "owner_admin",
      "x-csrf-token": "admin-execution-evidence",
      "origin": process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
    },
'''

if old_headers not in text:
    raise SystemExit("ADMIN_EVIDENCE_HEADER_BLOCK_NOT_FOUND")

text = text.replace(old_headers, new_headers, 1)

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_admin_execution_evidence_security_headers.py"
test_file.write_text(r'''
from pathlib import Path

text = Path("frontend/src/app/api/admin-execution-evidence/route.ts").read_text(encoding="utf-8")

assert '"Authorization": `Bearer ${ADMIN_TOKEN}`' in text
assert '"x-csrf-token": "admin-execution-evidence"' in text
assert '"origin": process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au"' in text
assert '"x-actor-role": "owner_admin"' in text
assert '"x-tenant-id": tenantId || "owner_admin"' in text

print("ADMIN_EXECUTION_EVIDENCE_SECURITY_HEADERS_TEST_PASSED")
''', encoding="utf-8")

print("ADMIN_EXECUTION_EVIDENCE_SECURITY_HEADERS_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")