from pathlib import Path
from datetime import datetime
import shutil

TARGETS = [
    "frontend/src/app/api/client-me/route.ts",
    "frontend/src/app/api/client-business-profile/route.ts",
    "frontend/src/app/api/client-review-action/route.ts",
    "frontend/src/app/api/run-agent/route.ts",
]

backup_dir = Path("backups") / f"proxy_origin_forwarding_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

for target in TARGETS:
    path = Path(target)

    if not path.exists():
        continue

    original = path.read_text(encoding="utf-8")

    shutil.copy2(path, backup_dir / path.name)

    if '"origin": req.headers.get("origin") || "",' in original:
        continue

    updated = original.replace(
        '"x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "tenant_unknown",',
        '''"x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "tenant_unknown",
    "origin": req.headers.get("origin") || "",
    "referer": req.headers.get("referer") || "",'''
    )

    path.write_text(updated, encoding="utf-8")

print("PROXY_ORIGIN_FORWARDING_FIXED")
print(f"Backup: {backup_dir}")