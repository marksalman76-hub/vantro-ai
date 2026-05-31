from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"main_before_step208_owner_fallback_logging_{timestamp}.py"

text = main_file.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

old = '''                    "recovered_error_type": type(exc).__name__,
                    "recovered_at": datetime.now(timezone.utc).isoformat(),
'''

new = '''                    "recovered_error_type": type(exc).__name__,
                    "recovered_error_message": str(exc),
                    "recovered_at": datetime.now(timezone.utc).isoformat(),
'''

if old not in text:
    raise RuntimeError("Expected owner fallback response block not found.")

text = text.replace(old, new)

main_file.write_text(text, encoding="utf-8")

py_compile.compile(str(main_file), doraise=True)

print("STEP_208_OWNER_FALLBACK_ERROR_LOGGING_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print("STEP_208_OK")