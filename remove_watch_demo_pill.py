from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_remove_watch_demo_pill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Remove Watch 90s Demo button/link blocks.
s = re.sub(r'\s*<a[^>]*>\s*Watch\s*90s\s*demo\s*</a>', '', s, flags=re.IGNORECASE | re.DOTALL)
s = re.sub(r'\s*<button[^>]*>\s*Watch\s*90s\s*demo\s*</button>', '', s, flags=re.IGNORECASE | re.DOTALL)

# Remove nearby small "Demo" pill/badge blocks.
s = re.sub(r'\s*<span[^>]*>\s*Demo\s*</span>', '', s, flags=re.IGNORECASE | re.DOTALL)
s = re.sub(r'\s*<div[^>]*>\s*Demo\s*</div>', '', s, flags=re.IGNORECASE | re.DOTALL)

PAGE.write_text(s, encoding="utf-8")

print("WATCH_90S_DEMO_AND_DEMO_PILL_REMOVED")
print(f"Backup: {backup}")