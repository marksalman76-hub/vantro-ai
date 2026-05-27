from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()

targets = [
    "frontend/src/app/client/page.tsx",
    "frontend/src/app/login/page.tsx",
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/admin-login/page.tsx",
    "frontend/src/app/client/billing/page.tsx",
    "frontend/src/app/client/billing/cancel/page.tsx",
    "frontend/src/app/client/billing/cancelled/page.tsx",
    "frontend/src/app/client/billing/success/page.tsx",
]

backup_dir = root / "backups" / f"remove_dynamic_exports_from_client_pages_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

for rel in targets:
    path = root / rel

    if not path.exists():
        continue

    shutil.copy2(path, backup_dir / path.name)

    text = path.read_text(encoding="utf-8")

    if '"use client"' not in text:
        continue

    updated = text.replace('export const dynamic = "force-dynamic";\n', "")
    updated = updated.replace("export const revalidate = 0;\n", "")
    updated = updated.replace('\n\n\n', '\n\n')

    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed.append(rel)

print("DYNAMIC_EXPORTS_REMOVED_FROM_CLIENT_PAGES")
print(f"Backup folder: {backup_dir}")
print("Changed:")
for item in changed:
    print("-", item)