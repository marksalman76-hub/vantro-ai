from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pass17_duplicate_transition_fix_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

text = re.sub(
    r'transition:\s*"transform 0\.16s ease, box-shadow 0\.16s ease, border-color 0\.16s ease",\s*\n\s*textAlign:\s*"left",\s*\n\s*fontSize:\s*11\.8,\s*\n\s*fontWeight:\s*700,\s*\n\s*transition:\s*"all 0\.18s ease",',
    'textAlign: "left",\n                          fontSize: 11.8,\n                          fontWeight: 700,\n                          transition: "all 0.18s ease",',
    text,
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_PORTAL_PASS17_DUPLICATE_TRANSITION_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print("duplicate_transition_pattern_remaining", 'border-color 0.16s ease",\n                          textAlign: "left",\n                          fontSize: 11.8,\n                          fontWeight: 700,\n                          transition: "all 0.18s ease"' in text)