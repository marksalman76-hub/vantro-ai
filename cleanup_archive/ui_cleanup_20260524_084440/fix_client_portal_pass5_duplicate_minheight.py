from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pass5_duplicate_minheight_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

# Remove duplicate minHeight: 120 when any earlier minHeight exists in same nearby style object.
text = re.sub(
    r'(minHeight:\s*[^,\n]+,\s*[\s\S]{0,260}?)\n\s*minHeight:\s*120,',
    r'\1',
    text,
)

# Exact known cleanup around line 1029 if still present.
text = text.replace(
    'padding: 14,\n                    fontSize: 13.5,\n                    minHeight: 120,\n                    lineHeight: 1.55,',
    'padding: 14,\n                    fontSize: 13.5,\n                    lineHeight: 1.55,'
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_PASS5_DUPLICATE_MINHEIGHT_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print("remaining_exact_duplicate", 'fontSize: 13.5,\n                    minHeight: 120,\n                    lineHeight: 1.55' in text)