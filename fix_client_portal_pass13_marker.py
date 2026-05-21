from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pass13_marker_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

marker = "// client_portal_bottom_section_rebuild_locked"

if marker not in text:
    text = text.replace(
        "// client_portal_aligned_upper_ui_locked",
        "// client_portal_aligned_upper_ui_locked\n" + marker
    )

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_PASS13_MARKER_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print("marker_present", marker in text)