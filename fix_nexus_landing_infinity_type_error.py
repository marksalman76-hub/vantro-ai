from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_nexus_infinity_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")
s = s.replace("repeat: Infinity", "repeat: Number.POSITIVE_INFINITY")

TARGET.write_text(s, encoding="utf-8")

print("NEXUS_LANDING_INFINITY_TYPE_ERROR_FIXED")
print(f"Backup: {backup}")