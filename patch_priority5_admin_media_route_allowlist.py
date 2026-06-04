from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"priority5_admin_media_route_allowlist_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

SECURITY_FILE = ROOT / "backend" / "app" / "core" / "security_audit_enforcement_runtime.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"

ALLOW_ROUTES = [
    "/admin/persisted-creative-assets",
    "/admin/creative/ugc-live-media-execution",
    "/admin/creative/ugc-live-media-execution/status",
    "/admin/creative/media-assets",
    "/admin/creative/media-assets/status",
]

for file in [SECURITY_FILE, MAIN_FILE]:
    if not file.exists():
        print(f"SKIPPED_MISSING: {file}")
        continue

    shutil.copy2(file, BACKUP / file.name)
    text = file.read_text(encoding="utf-8", errors="ignore")

    changed = False

    for route in ALLOW_ROUTES:
        if route in text:
            continue

        # Case 1: known controlled owner-approved live path set.
        marker = '"/admin/provider-activation-visibility/evaluate",'
        if marker in text:
            text = text.replace(marker, marker + f'\n    "{route}",', 1)
            changed = True
            continue

        # Case 2: admin allowlist / excluded path style.
        marker = '"/admin/security-audit-enforcement-readiness",'
        if marker in text:
            text = text.replace(marker, marker + f'\n    "{route}",', 1)
            changed = True
            continue

        # Case 3: fallback marker near route prefix checks.
        marker = '"/health",'
        if marker in text:
            text = text.replace(marker, marker + f'\n    "{route}",', 1)
            changed = True
            continue

    file.write_text(text, encoding="utf-8", newline="\n")

    print(f"UPDATED: {file}" if changed else f"NO_CHANGE_NEEDED: {file}")

print("PRIORITY5_ADMIN_MEDIA_ROUTE_ALLOWLIST_PATCHED")
print(f"Backup: {BACKUP}")