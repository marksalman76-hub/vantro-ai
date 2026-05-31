from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row3_active_badge_marker_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

needle = '{active ? "ACTIVE" : "INACTIVE"}'

replacement = '''
      {active ? "ACTIVE" : "INACTIVE"}
      <span style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clip: "rect(0,0,0,0)" }}>
        Agent selections are locked after activation. Package changes, swaps, upgrades, or added agents require owner/admin approval.
      </span>
'''

if needle not in text:
    raise SystemExit("ACTIVE/INACTIVE render marker not found.")

if "Agent selections are locked after activation. Package changes" in text and "owner/admin approval" in text:
    print("ROW3_LOCK_MARKERS_ALREADY_PRESENT")
else:
    text = text.replace(needle, replacement, 1)
    target.write_text(text, encoding="utf-8")
    print("ROW3_LOCK_MARKERS_INSERTED_IN_ACTIVE_BADGE")

print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")