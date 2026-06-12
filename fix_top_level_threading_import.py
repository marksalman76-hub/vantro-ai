from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
BACKUP_DIR = ROOT / "backups" / f"top_level_threading_import_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

# Remove any accidental duplicate top-level import first only if present more than once later.
lines = text.splitlines()

# Find the top import block near the start.
top_preview = "\n".join(lines[:40])

if "import shutil" not in top_preview:
    raise SystemExit("TOP_LEVEL_IMPORT_SHUTIL_NOT_FOUND_IN_FIRST_40_LINES")

# Only insert top-level import threading if it is not already in the top import block.
if "import threading" not in top_preview:
    text = text.replace("import shutil\n", "import shutil\nimport threading\n", 1)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
verify_lines = verify.splitlines()
verify_top = "\n".join(verify_lines[:40])

if "import threading" not in verify_top:
    raise SystemExit("TOP_LEVEL_THREADING_IMPORT_NOT_INSTALLED")

print("TOP_LEVEL_THREADING_IMPORT_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")
print("\nTop import block:")
print(verify_top)