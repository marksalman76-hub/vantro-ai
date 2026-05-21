from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_line2191_alignitems_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

old = '<div style={{ display: "flex", gap: 16, alignItems: "flex-start", flexWrap: "wrap", justifyContent: "flex-end", alignItems: "center" }}>'
new = '<div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "flex-end", alignItems: "center" }}>'

if old not in text:
    raise RuntimeError("Exact duplicate alignItems line not found")

text = text.replace(old, new, 1)
PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_LINE2191_DUPLICATE_ALIGNITEMS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")