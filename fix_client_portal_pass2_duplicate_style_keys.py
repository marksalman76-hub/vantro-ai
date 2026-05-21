from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pass2_duplicate_style_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

# Fix exact duplicate introduced by automated spacing replacement.
text = text.replace(
    'gap: 16, alignItems: "flex-start", flexWrap: "wrap", alignItems: "center"',
    'gap: 16, flexWrap: "wrap", alignItems: "center"'
)

# General safety cleanup: inside any inline style object, remove earlier duplicate alignItems if both flex-start and center appear.
text = re.sub(
    r'alignItems:\s*"flex-start",\s*(flexWrap:\s*"wrap",\s*alignItems:\s*"center")',
    r'\1',
    text
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_PASS2_DUPLICATE_STYLE_KEYS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print("duplicate_pattern_remaining", 'alignItems: "flex-start", flexWrap: "wrap", alignItems: "center"' in text)