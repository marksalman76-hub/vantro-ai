from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py"
BACKUP = ROOT / "backups" / f"future_import_position_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

future = "from __future__ import annotations\n"
text = text.replace(future, "")

TARGET.write_text(future + text.lstrip(), encoding="utf-8", newline="\n")

print("FUTURE_IMPORT_POSITION_FIXED")
print(f"Backup: {BACKUP}")