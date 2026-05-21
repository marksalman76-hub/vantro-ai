from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_all_duplicate_alignitems_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

patterns = [
    (
        r'alignItems:\s*"flex-start",\s*(gap:\s*16,\s*flexWrap:\s*"wrap",\s*justifyContent:\s*"flex-end",\s*alignItems:\s*"center")',
        r'\1',
    ),
    (
        r'alignItems:\s*"flex-start",\s*(gap:\s*16,\s*flexWrap:\s*"wrap",\s*alignItems:\s*"center")',
        r'\1',
    ),
    (
        r'alignItems:\s*"flex-start",\s*(flexWrap:\s*"wrap",\s*alignItems:\s*"center")',
        r'\1',
    ),
]

for pattern, replacement in patterns:
    text = re.sub(pattern, replacement, text)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_ALL_DUPLICATE_ALIGNITEMS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")

checks = [
    'alignItems: "flex-start", gap: 16, flexWrap: "wrap", justifyContent: "flex-end", alignItems: "center"',
    'alignItems: "flex-start", gap: 16, flexWrap: "wrap", alignItems: "center"',
    'alignItems: "flex-start", flexWrap: "wrap", alignItems: "center"',
]

for check in checks:
    print(check, check in text)