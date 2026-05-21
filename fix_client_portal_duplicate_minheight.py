from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_duplicate_minheight_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

# Remove duplicate minHeight when the same inline style object already has one.
# This targets the automated Pass 2 insertion, not component logic.
text = re.sub(
    r'(minHeight:\s*"[^"]+",\s*[\s\S]{0,260}?)\n\s*minHeight:\s*"100%",',
    r'\1',
    text,
)

# Exact local cleanup for the known textarea/button-area pattern if still present.
text = text.replace(
    'padding: 20,\n                      minHeight: "100%",\n                fontSize: 13,',
    'padding: 20,\n                fontSize: 13,'
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_DUPLICATE_MINHEIGHT_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")