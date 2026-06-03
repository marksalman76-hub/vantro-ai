from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = ROOT / "backups" / f"row7_media_asset_lifecycle_verification_fix_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

route = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable" / "route.ts"

if not route.exists():
    raise SystemExit("client-latest-deliverable route not found")

shutil.copy2(route, backup / "route.ts")

text = route.read_text(encoding="utf-8")

marker = "media_asset_lifecycle_enabled"

if marker not in text:
    insert_after = 'import { attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";'

    replacement = insert_after + '\n\n// media_asset_lifecycle_enabled'

    if insert_after not in text:
        raise SystemExit("ROW7_VERIFICATION_FIX_FAILED: import marker not found")

    text = text.replace(insert_after, replacement)

route.write_text(text, encoding="utf-8")

print("ROW7_MEDIA_ASSET_LIFECYCLE_VERIFICATION_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {route}")