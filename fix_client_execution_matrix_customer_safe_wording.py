from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()

targets = [
    root / "frontend" / "src" / "app" / "api" / "client-execution-matrix" / "route.ts",
    root / "backend" / "app" / "main.py",
]

backup_dir = root / "backups" / f"client_execution_matrix_safe_wording_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

replacements = {
    "internal_prompt_exposure_blocked": "request_details_protected",
    "backend_architecture_exposure_blocked": "system_details_protected",
    "internal prompt": "request details",
    "system prompt": "request details",
    "developer message": "request details",
    "raw json": "details",
    "debug": "support",
    "webhook": "connection",
    "runtime": "system",
}

changed = []

for path in targets:
    if not path.exists():
        print(f"SKIPPED missing: {path}")
        continue

    shutil.copy2(path, backup_dir / path.name)

    text = path.read_text(encoding="utf-8")
    updated = text

    for old, new in replacements.items():
        updated = updated.replace(old, new)

    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed.append(str(path))

print("CLIENT_EXECUTION_MATRIX_CUSTOMER_SAFE_WORDING_FIXED")
print(f"Backup folder: {backup_dir}")
print("Changed:")
for item in changed:
    print(f"- {item}")