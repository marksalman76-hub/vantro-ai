from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_run_agent_owner_admin_credit_bypass.py"

backup_dir = ROOT / "backups" / f"run_agent_owner_admin_credit_bypass_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

text = text.replace(
    'owner_admin_credit_bypass = actor_role in {"owner", "admin", "system"}',
    'owner_admin_credit_bypass = actor_role in {"owner", "admin", "owner_admin", "system"}',
)

text = text.replace(
    'owner_admin_internal_execution = request.actor_role in {"owner", "admin", "system"}',
    'owner_admin_internal_execution = (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}',
)

target.write_text(text, encoding="utf-8")

test_file.write_text(r'''
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert 'owner_admin_credit_bypass = actor_role in {"owner", "admin", "owner_admin", "system"}' in text
assert 'owner_admin_internal_execution = (request.actor_role or "").strip().lower() in {"owner", "admin", "owner_admin", "system"}' in text

print("RUN_AGENT_OWNER_ADMIN_CREDIT_BYPASS_TEST_PASSED")
'''.lstrip(), encoding="utf-8")

print("RUN_AGENT_OWNER_ADMIN_CREDIT_BYPASS_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")
print(f"Created/updated: {test_file}")