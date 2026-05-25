from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_real_nav_array_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

s = s.replace(
    '["Platform", "Agents", "Studio", "Pricing", "Enterprise"]',
    '["Agents", "Pricing", "Enterprise"]'
)

PAGE.write_text(s, encoding="utf-8")

print("PLATFORM_AND_STUDIO_REMOVED_FROM_REAL_NAV_ARRAYS")
print(f"Backup: {backup}")