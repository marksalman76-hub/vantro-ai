from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py"
BACKUP = ROOT / "backups" / f"runway_direct_video_path_mapping_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "shared_creative_media_generation_runtime.py")

text = TARGET.read_text(encoding="utf-8")
original = text

old_call = '''        return _safe_call(
            run_runway_text_to_video_quality_test,
            prompt=prompt,
            task=prompt,
            agent_id=agent_id,
            tenant_id=tenant_id,
            pack_id=pack_id,
            test_label=f"{pack_id}_runway_live_video",
        )'''

new_call = '''        return _safe_call(
            run_runway_text_to_video_quality_test,
            prompt_text=prompt,
            test_label=f"{pack_id}_runway_live_video",
            allow_live_execution=True,
        )'''

if old_call not in text:
    raise RuntimeError("Runway direct _safe_call block not found")

text = text.replace(old_call, new_call, 1)

# Add Runway output keys into URL extraction.
text = text.replace(
    '''        "output_url",
    ]:''',
    '''        "output_url",
        "video_path",
        "video_url_preview",
    ]:''',
    1,
)

# Add nested variants too.
text = text.replace(
    '''                    for nested_key in ["url", "asset_url", "media_url", "download_url", "preview_url", "path"]:''',
    '''                    for nested_key in ["url", "asset_url", "media_url", "download_url", "preview_url", "path", "video_path", "video_url_preview"]:''',
    1,
)

# Prefer real downloaded local mp4 path when present.
old_preview = '''    preview_url = result.get("preview_url") or (output_urls[0] if output_urls else "")
    download_url = result.get("download_url") or result.get("asset_url") or result.get("media_url") or preview_url'''

new_preview = '''    local_video_path = result.get("video_path") if result.get("video_saved") else ""
    preview_url = result.get("preview_url") or local_video_path or result.get("video_url_preview") or (output_urls[0] if output_urls else "")
    download_url = result.get("download_url") or result.get("asset_url") or result.get("media_url") or local_video_path or preview_url'''

if old_preview not in text:
    raise RuntimeError("Preview/download mapping block not found")

text = text.replace(old_preview, new_preview, 1)

# Treat video_saved as real media created.
text = text.replace(
    '''    real_media_asset_created = bool(preview_url or download_url or result.get("real_media_asset_created"))''',
    '''    real_media_asset_created = bool(preview_url or download_url or result.get("real_media_asset_created") or result.get("video_saved"))''',
    1,
)

TARGET.write_text(text, encoding="utf-8", newline="\n")

print("RUNWAY_DIRECT_EXECUTION_AND_VIDEO_PATH_MAPPING_PATCHED")
print(f"Backup: {BACKUP}")