from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_footer_socials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

s = re.sub(
    r'\s*<div className="footer__social">.*?</div>',
    '',
    s,
    flags=re.DOTALL
)

PAGE.write_text(s, encoding="utf-8")

print("FOOTER_SOCIAL_LINKS_REMOVED")
print(f"Backup: {backup}")