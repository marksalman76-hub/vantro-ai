from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"main_before_step209d_force_env_loader_{timestamp}.py"
text = main_file.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

force_import = "import sitecustomize  # Step 209D force local env loading"

if force_import not in text:
    lines = text.splitlines()
    insert_at = 0

    for i, line in enumerate(lines[:20]):
        if line.startswith("from __future__ import"):
            insert_at = i + 1

    lines.insert(insert_at, force_import)
    text = "\n".join(lines)

main_file.write_text(text, encoding="utf-8")
py_compile.compile(str(main_file), doraise=True)

print("STEP_209D_FORCE_ENV_LOADER_IN_MAIN_OK")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")