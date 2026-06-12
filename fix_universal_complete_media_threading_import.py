from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
BACKUP_DIR = ROOT / "backups" / f"universal_complete_media_threading_import_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

if "import threading" not in text:
    marker = "import shutil\n"
    if marker not in text:
        raise SystemExit("IMPORT_MARKER_NOT_FOUND")
    text = text.replace(marker, marker + "import threading\n", 1)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
if "import threading" not in verify:
    raise SystemExit("THREADING_IMPORT_NOT_INSTALLED")

print("UNIVERSAL_COMPLETE_MEDIA_THREADING_IMPORT_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")