from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_ugc_media_security_allowlist_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

FILES = [
    ROOT / "backend" / "app" / "main.py",
    ROOT / "backend" / "app" / "core" / "security_audit_enforcement_runtime.py",
]

PATHS_TO_ALLOW = [
    "/admin/creative/ugc-live-media-execution",
    "/admin/creative/ugc-live-media-execution/status",
    "/admin/persisted-creative-assets",
    "/admin/creative/media-assets",
    "/admin/creative/media-assets/status",
]

for file in FILES:
    if not file.exists():
        continue

    shutil.copy2(file, BACKUP / file.name)
    text = file.read_text(encoding="utf-8", errors="ignore")

    for route in PATHS_TO_ALLOW:
        if route not in text and "/admin/provider-activation-visibility/evaluate" in text:
            text = text.replace(
                '"/admin/provider-activation-visibility/evaluate",',
                f'"/admin/provider-activation-visibility/evaluate",\n    "{route}",',
            )

    file.write_text(text, encoding="utf-8", newline="\n")

print("ADMIN_UGC_MEDIA_SECURITY_ALLOWLIST_PATCHED")
print(f"Backup: {BACKUP}")