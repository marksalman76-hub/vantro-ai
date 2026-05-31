from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row9_admin_safe_wording_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

old = "No frontend view may expose provider secrets or internal prompts."
new = "No frontend view may expose protected provider details or private request instructions."

if old not in text:
    raise SystemExit("Expected admin wording not found.")

text = text.replace(old, new, 1)
target.write_text(text, encoding="utf-8")

print("ROW9_ADMIN_SAFE_WORDING_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")