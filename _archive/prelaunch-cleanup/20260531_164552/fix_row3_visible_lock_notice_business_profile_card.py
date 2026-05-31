from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row3_visible_lock_notice_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

old = '''                    <div style={{ marginTop: 5, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>'''

new = '''                    <div style={{ marginTop: 5, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>

                    <div style={{ marginTop: 8, color: darkModeEnabled ? "#fde68a" : "#92400e", fontSize: 12, fontWeight: 800, lineHeight: 1.45 }}>
                      Agent selections are locked after activation. Package changes, swaps, upgrades, or added agents require owner/admin approval.
                    </div>'''

if old not in text:
    raise SystemExit("Business profile live card insertion target not found.")

if "Agent selections are locked after activation. Package changes, swaps, upgrades, or added agents require owner/admin approval." not in text:
    text = text.replace(old, new, 1)
    target.write_text(text, encoding="utf-8")
    print("ROW3_VISIBLE_LOCK_NOTICE_INSERTED")
else:
    print("ROW3_VISIBLE_LOCK_NOTICE_ALREADY_PRESENT")

print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")