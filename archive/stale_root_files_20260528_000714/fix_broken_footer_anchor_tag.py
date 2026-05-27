from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_broken_footer_anchor_tag_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Repair broken invisible anchor placed directly before footer.
s = re.sub(
    r'<div id="workflow"\s+style=\{\{\s*scrollMarginTop:\s*120\s*\}\}\s*\n\s*<footer',
    '<div id="workflow" style={{ scrollMarginTop: 120 }} />\n      <footer',
    s,
)

# Repair any other broken anchor before footer.
s = re.sub(
    r'<div id="([^"]+)"\s+style=\{\{\s*scrollMarginTop:\s*120\s*\}\}\s*\n\s*<footer',
    r'<div id="\1" style={{ scrollMarginTop: 120 }} />\n      <footer',
    s,
)

PAGE.write_text(s, encoding="utf-8")

print("BROKEN_FOOTER_ANCHOR_TAG_FIXED")
print(f"Backup: {backup}")