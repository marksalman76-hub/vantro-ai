from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/admin_creative_media_asset_viewer.py"
BACKUP = ROOT / "backups" / f"admin_asset_viewer_registry_scope_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

replacements = {
    'registry.get("asset_count", len(assets))': '(locals().get("registry") or {}).get("asset_count", len(locals().get("assets") or []))',
    'registry.get("total_asset_count", len(assets))': '(locals().get("registry") or {}).get("total_asset_count", len(locals().get("assets") or []))',
    'registry.get("asset_count")': '(locals().get("registry") or {}).get("asset_count")',
    'registry.get("total_asset_count")': '(locals().get("registry") or {}).get("total_asset_count")',
    'registry.get("last_supabase_registry_read")': '(locals().get("registry") or {}).get("last_supabase_registry_read")',
    'registry.get("last_supabase_registry_write")': '(locals().get("registry") or {}).get("last_supabase_registry_write")',
    'registry.get("last_supabase_media_upload")': '(locals().get("registry") or {}).get("last_supabase_media_upload")',
}

for old, new in replacements.items():
    text = text.replace(old, new)

TARGET.write_text(text, encoding="utf-8", newline="\n")

print("ADMIN_ASSET_VIEWER_REGISTRY_SCOPE_FIXED")
print(f"Backup: {BACKUP}")