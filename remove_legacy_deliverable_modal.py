from pathlib import Path
from datetime import datetime

root = Path.cwd()

target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = backup_dir / f"client_page_before_legacy_modal_removal_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")

backup.write_text(s, encoding="utf-8")

start_marker = "      {showDeliverableModal ? ("
popup_marker = "/* OUTPUT_VIEWER_POPUP_MODAL_LOCKED_V1 */"

start = s.find(start_marker)
popup = s.find(popup_marker)

if start == -1:
    raise SystemExit("Legacy modal start not found.")

if popup == -1:
    raise SystemExit("Popup modal marker not found.")

legacy_block = s[start:popup]

s = s.replace(legacy_block, "")

target.write_text(s, encoding="utf-8")

print("LEGACY_DELIVERABLE_MODAL_REMOVED")
print(f"Backup: {backup}")
print(f"Updated: {target}")