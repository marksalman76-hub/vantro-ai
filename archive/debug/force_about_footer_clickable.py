from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_force_about_clickable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Force About footer link to /#about rather than plain hash.
s = s.replace('["About","#about"]', '["About","/#about"]')
s = s.replace('href="#about"', 'href="/#about"')

# Ensure the About section has a visible anchor.
if 'id="about"' not in s:
    idx = s.find("About")
    if idx == -1:
        raise SystemExit("FAILED: About text not found")
    s = s[:idx] + '<div id="about" style={{ scrollMarginTop: 140 }} />\n' + s[idx:]

PAGE.write_text(s, encoding="utf-8")

print("ABOUT_FOOTER_CLICKABLE_FORCED")
print(f"Backup: {backup}")