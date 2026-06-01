from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

BACKUP = ROOT / "backups" / f"client_use_client_position_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "page.tsx")

s = TARGET.read_text(encoding="utf-8")

s = s.replace('"use client";', "")
s = '"use client";\n\n' + s.lstrip()

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_USE_CLIENT_POSITION_FIXED")
print("Backup:", BACKUP)