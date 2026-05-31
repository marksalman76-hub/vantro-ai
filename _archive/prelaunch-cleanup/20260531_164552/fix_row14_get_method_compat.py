from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "ai_media_session_auth_compat.py"

backup_dir = ROOT / "backups" / f"row14_get_method_compat_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old = '''    if method not in {"POST", "OPTIONS"}:
'''

new = '''    allowed_methods = {
        "/admin/ai-media-pipeline/run": {"POST", "OPTIONS"},
        "/admin/provider-action-readiness": {"GET", "OPTIONS"},
        "/admin/provider-action-readiness/evaluate": {"POST", "OPTIONS"},
    }

    if method not in allowed_methods.get(path, set()):
'''

if old not in text:
    raise SystemExit("Original method block not found")

text = text.replace(old, new)

target.write_text(text, encoding="utf-8")

print("ROW14_GET_METHOD_COMPAT_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")