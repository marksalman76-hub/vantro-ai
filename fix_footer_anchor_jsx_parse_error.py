from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_footer_anchor_parse_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Fix invalid JSX inserted as style={ scrollMarginTop: 120 }
s = s.replace('style={ scrollMarginTop: 120 }', 'style={{ scrollMarginTop: 120 }}')

# Also catch any similar malformed div anchors.
s = re.sub(
    r'<div id="([^"]+)" style=\{ scrollMarginTop: 120 \} />',
    r'<div id="\1" style={{ scrollMarginTop: 120 }} />',
    s,
)

PAGE.write_text(s, encoding="utf-8")

print("FOOTER_ANCHOR_JSX_PARSE_ERROR_FIXED")
print(f"Backup: {backup}")