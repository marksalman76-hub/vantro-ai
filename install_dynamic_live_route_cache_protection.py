from pathlib import Path
from datetime import datetime, timezone
import shutil

root = Path.cwd()

files = [
    "frontend/src/app/client/page.tsx",
    "frontend/src/app/login/page.tsx",
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/activate/page.tsx",
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/admin-login/page.tsx",
    "frontend/src/app/client/billing/page.tsx",
    "frontend/src/app/client/billing/cancel/page.tsx",
    "frontend/src/app/client/billing/cancelled/page.tsx",
    "frontend/src/app/client/billing/success/page.tsx",
]

backup_dir = root / "backups" / f"dynamic_live_route_cache_protection_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

stamp_path = root / "frontend" / "src" / "app" / "deployment-stamp.ts"
stamp_value = datetime.now(timezone.utc).isoformat()

stamp_path.write_text(
    f'export const DEPLOYMENT_STAMP = "{stamp_value}";\n',
    encoding="utf-8",
)

changed = []

for rel in files:
    path = root / rel

    if not path.exists():
        print(f"SKIPPED missing: {rel}")
        continue

    shutil.copy2(path, backup_dir / path.name)

    text = path.read_text(encoding="utf-8")

    insert = 'export const dynamic = "force-dynamic";\nexport const revalidate = 0;\n\n'

    if 'export const dynamic = "force-dynamic"' not in text:
        text = insert + text
        path.write_text(text, encoding="utf-8")
        changed.append(rel)

print("DYNAMIC_LIVE_ROUTE_CACHE_PROTECTION_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Deployment stamp: {stamp_value}")
print("Changed:")
for item in changed:
    print(f"- {item}")