from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_careers_press_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

s = s.replace(
    '["About","#platform"],["Blog","#features"],["Careers","/support-request"],["Press","/support-request"],["Contact","/support-request"]',
    '["About","#platform"],["Blog","#features"],["Contact","/support-request"]'
)

PAGE.write_text(s, encoding="utf-8")

print("FOOTER_CAREERS_PRESS_REMOVED")
print(f"Backup: {backup}")