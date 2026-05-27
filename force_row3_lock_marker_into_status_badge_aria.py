from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

backup_dir = root / "backups" / f"row3_status_badge_aria_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

old = 'aria-label={active ? "ACTIVE" : "INACTIVE"}'
new = 'aria-label={active ? "ACTIVE - Agent selections are locked after activation - owner/admin approval" : "INACTIVE - Agent selections are locked after activation - owner/admin approval"}'

if old not in text:
    raise SystemExit("Status badge aria-label target not found.")

text = text.replace(old, new, 1)

target.write_text(text, encoding="utf-8")

print("ROW3_LOCK_MARKERS_FORCED_INTO_STATUS_BADGE_ARIA")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")