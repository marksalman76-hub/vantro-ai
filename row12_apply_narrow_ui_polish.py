from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"row12_narrow_ui_polish_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

targets = [
    Path("frontend/src/app/admin/page.tsx"),
    Path("frontend/src/app/client/page.tsx"),
]

for target in targets:
    if not target.exists():
        raise FileNotFoundError(f"Missing required file: {target}")
    backup_target = BACKUP_DIR / target.name
    shutil.copy2(target, backup_target)

admin_path = Path("frontend/src/app/admin/page.tsx")
admin_text = admin_path.read_text(encoding="utf-8", errors="ignore")

admin_text = admin_text.replace(
    'alert(JSON.stringify(json?.data || json, null, 2));',
    'alert("Execution evidence loaded successfully.");'
)

admin_path.write_text(admin_text, encoding="utf-8")

client_path = Path("frontend/src/app/client/page.tsx")
client_text = client_path.read_text(encoding="utf-8", errors="ignore")

client_replacements = {
    'alert(JSON.stringify(json?.data || json, null, 2));':
        'alert("Completed action evidence loaded successfully.");',
    'Real generated/uploaded media and runtime deliverables only.':
        'Real generated or uploaded media and completed deliverables only.',
    'Real generated media, uploaded brand files, previews, and deliverable assets will appear here once attached to the runtime result.':
        'Real generated media, uploaded brand files, previews, and deliverable assets will appear here once ready.',
    'Customer-safe proof of completed actions without exposing internal routing or credentials.':
        'Clear proof of completed actions and delivered results.',
}

for old, new in client_replacements.items():
    client_text = client_text.replace(old, new)

client_path.write_text(client_text, encoding="utf-8")

print("ROW12_NARROW_UI_POLISH_PATCH_APPLIED")
print("Backup folder:", BACKUP_DIR)
print("Updated:", admin_path)
print("Updated:", client_path)