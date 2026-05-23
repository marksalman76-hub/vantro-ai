from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKEND = ROOT / "backend" / "app"

main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"main_before_step210d_owner_credit_variable_fix_{timestamp}.py"

text = main_file.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

old = '''    actor_role = (actor_role or "").strip().lower() if "actor_role" in locals() else ""
'''

new = '''    actor_role = (request.actor_role or "").strip().lower()
'''

if old not in text:
    raise RuntimeError("Expected broken actor_role line not found.")

text = text.replace(old, new)

main_file.write_text(text, encoding="utf-8")

py_compile.compile(str(main_file), doraise=True)

print("STEP_210D_OWNER_CREDIT_VARIABLE_FIX_OK")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")