from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

targets = [
    ROOT / "backend" / "app" / "core" / "session_auth_hardening_runtime.py",
    ROOT / "backend" / "app" / "core" / "security_audit_enforcement_runtime.py",
]

backup_dir = ROOT / "backups" / f"owner_admin_role_global_auth_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

for target in targets:
    shutil.copy2(target, backup_dir / target.name)

    text = target.read_text(encoding="utf-8")

    text = text.replace(
        '{"owner", "admin", "system"}',
        '{"owner", "admin", "owner_admin", "system"}'
    )

    target.write_text(text, encoding="utf-8")

print("OWNER_ADMIN_ROLE_GLOBAL_AUTH_FIXED")
print(f"Backup folder: {backup_dir}")
for target in targets:
    print(f"Updated: {target}")