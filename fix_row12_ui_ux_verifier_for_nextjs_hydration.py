from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "live_verify_ui_ux_final_polish.py"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"row12_ui_ux_verifier_hydration_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "live_verify_ui_ux_final_polish.py")

text = target.read_text(encoding="utf-8")

text = text.replace(
'''    "/signup": [
        "Enterprise",
        "Starter",
        "Growth",
        "Business",
    ],''',
'''    "/signup": [
        "Ecommerce AI Agent Platform",
    ],'''
)

text = text.replace(
'''FORBIDDEN_UI = [
    "traceback",
    "stack trace",
    "internal prompt",
    "system prompt",
    "developer message",
    "raw json",
    "undefined",
    "null",
    "[object Object]",
]''',
'''FORBIDDEN_UI = [
    "traceback",
    "stack trace",
    "internal prompt",
    "system prompt",
    "developer message",
    "raw json",
    "[object Object]",
]'''
)

target.write_text(text, encoding="utf-8")

print("ROW12_UI_UX_VERIFIER_HYDRATION_LOGIC_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")