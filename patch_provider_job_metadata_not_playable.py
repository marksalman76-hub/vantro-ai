from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py"
BACKUP = ROOT / "backups" / f"provider_job_metadata_not_playable_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "shared_creative_media_generation_runtime.py")

text = TARGET.read_text(encoding="utf-8")
original = text

helper = '''
def _has_real_media_url(asset: Dict[str, Any]) -> bool:
    values = [
        asset.get("preview_url"),
        asset.get("download_url"),
        asset.get("asset_url"),
        asset.get("media_url"),
        asset.get("video_url"),
        asset.get("audio_url"),
    ]
    for value in values:
        raw = str(value or "").strip()
        if not raw:
            continue
        if raw.startswith("http") or raw.startswith("data:video") or raw.startswith("data:audio") or raw.startswith("data:image"):
            return True
    return False

def _is_provider_job_metadata_only(asset: Dict[str, Any]) -> bool:
    status = str(asset.get("status") or "").lower()
    if "provider_job_created_or_attempted" in status:
        return not _has_real_media_url(asset)
    if "metadata_fallback" in status:
        return True
    return False

'''

if "def _has_real_media_url" not in text:
    marker = "def _compose_video_audio_asset("
    if marker not in text:
        raise RuntimeError("Compose helper marker not found")
    text = text.replace(marker, helper + marker, 1)

# Do not persist video asset records unless real playable media exists.
text = text.replace(
    '''        video_asset["persistence"] = _persist_media_asset(video_asset)
        video_assets.append(video_asset)''',
    '''        if not _is_provider_job_metadata_only(video_asset):
            video_asset["persistence"] = _persist_media_asset(video_asset)
            video_assets.append(video_asset)'''
)

# Do not persist audio metadata-only records as playable assets.
text = text.replace(
    '''        audio_asset["persistence"] = _persist_media_asset(audio_asset)
        audio_assets.append(audio_asset)''',
    '''        if not _is_provider_job_metadata_only(audio_asset):
            audio_asset["persistence"] = _persist_media_asset(audio_asset)
            audio_assets.append(audio_asset)'''
)

TARGET.write_text(text, encoding="utf-8", newline="\n")

print("PROVIDER_JOB_METADATA_NOT_PLAYABLE_PATCHED")
print(f"Backup: {BACKUP}")