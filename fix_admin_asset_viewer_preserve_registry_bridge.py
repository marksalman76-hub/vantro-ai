from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/admin_creative_media_asset_viewer.py"
BACKUP = ROOT / "backups" / f"admin_asset_viewer_registry_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / TARGET.name)

text = TARGET.read_text(encoding="utf-8")
original = text

# Ensure the admin viewer response preserves registry diagnostics/counts from creative_asset_persistence_bridge.
text = text.replace(
    '"asset_count": len(assets),',
    '"asset_count": registry.get("asset_count", len(assets)),'
)

text = text.replace(
    '"total_asset_count": len(assets),',
    '"total_asset_count": registry.get("total_asset_count", len(assets)),'
)

# Add bridge diagnostics into the returned admin viewer payload if not already present.
needle = '"credential_values_exposed": False,'
insert = '''"credential_values_exposed": False,
            "bridge_asset_count": registry.get("asset_count"),
            "bridge_total_asset_count": registry.get("total_asset_count"),
            "last_supabase_registry_read": registry.get("last_supabase_registry_read"),
            "last_supabase_registry_write": registry.get("last_supabase_registry_write"),
            "last_supabase_media_upload": registry.get("last_supabase_media_upload"),'''

if "bridge_total_asset_count" not in text:
    text = text.replace(needle, insert)

if text == original:
    print("NO_CHANGE_ADMIN_ASSET_VIEWER_ALREADY_PATCHED")
else:
    TARGET.write_text(text, encoding="utf-8", newline="\n")
    print("ADMIN_ASSET_VIEWER_REGISTRY_BRIDGE_PATCHED")
    print(f"Backup: {BACKUP}")