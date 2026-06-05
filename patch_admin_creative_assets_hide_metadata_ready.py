from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGETS = [
    ROOT / "backend/app/main.py",
    ROOT / "backend/app/api/admin_creative_media_assets_routes.py",
    ROOT / "backend/app/runtime/creative_asset_persistence_bridge.py",
    ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py",
]

existing = [p for p in TARGETS if p.exists()]
BACKUP = ROOT / "backups" / f"admin_creative_assets_hide_metadata_ready_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

patched = []

BAD_STATUSES = [
    "provider_job_created_or_attempted",
    "live_provider_ready_endpoint_missing",
    "metadata_fallback",
    "endpoint_missing",
    "blocked_owner_approval_required",
]

for target in existing:
    shutil.copy2(target, BACKUP / target.name)
    text = target.read_text(encoding="utf-8")
    original = text

    # Hard stop: these statuses must never be marked playable.
    text = text.replace(
        '"preview_ready": True,',
        '"preview_ready": False if str(asset.get("status", "")).lower() in ["provider_job_created_or_attempted", "live_provider_ready_endpoint_missing", "metadata_fallback", "endpoint_missing", "blocked_owner_approval_required"] else True,'
    )
    text = text.replace(
        '"download_ready": True,',
        '"download_ready": False if str(asset.get("status", "")).lower() in ["provider_job_created_or_attempted", "live_provider_ready_endpoint_missing", "metadata_fallback", "endpoint_missing", "blocked_owner_approval_required"] else True,'
    )

    # Remove fake preview/download URLs for metadata-only provider jobs.
    marker = 'provider_job_created_or_attempted'
    if marker in text and "def _is_metadata_only_asset" not in text:
        helper = '''
def _is_metadata_only_asset(asset):
    status = str(asset.get("status") or "").lower()
    if status in {
        "provider_job_created_or_attempted",
        "live_provider_ready_endpoint_missing",
        "metadata_fallback",
        "endpoint_missing",
        "blocked_owner_approval_required",
    }:
        return True
    return False

def _strip_metadata_only_asset_urls(asset):
    if not isinstance(asset, dict):
        return asset
    if _is_metadata_only_asset(asset):
        asset = dict(asset)
        asset["preview_ready"] = False
        asset["download_ready"] = False
        asset["preview_url"] = ""
        asset["download_url"] = ""
    return asset

'''
        text = helper + text

    # If an assets list is returned, sanitize it.
    text = text.replace(
        '"assets": assets,',
        '"assets": [_strip_metadata_only_asset_urls(a) for a in assets],'
    )
    text = text.replace(
        '"assets": media_assets,',
        '"assets": [_strip_metadata_only_asset_urls(a) for a in media_assets],'
    )

    if text != original:
        target.write_text(text, encoding="utf-8", newline="\n")
        patched.append(str(target))

print("ADMIN_CREATIVE_ASSETS_HIDE_METADATA_READY_PATCHED")
print("Patched:")
for p in patched:
    print(p)
print(f"Backup: {BACKUP}")