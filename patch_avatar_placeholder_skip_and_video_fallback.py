from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py"
BACKUP = ROOT / "backups" / f"avatar_placeholder_skip_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "shared_creative_media_generation_runtime.py")

text = TARGET.read_text(encoding="utf-8")
original = text

helper = '''
def _is_provider_endpoint_placeholder(asset: Dict[str, Any], result: Dict[str, Any]) -> bool:
    status = str(asset.get("status") or asset.get("execution_status") or "").lower()
    result_status = str(result.get("execution_status") or result.get("status") or "").lower()
    return "live_provider_ready_endpoint_missing" in status or "live_provider_ready_endpoint_missing" in result_status

'''

if "def _is_provider_endpoint_placeholder" not in text:
    marker = "def _persist_media_asset(asset: Dict[str, Any]) -> Dict[str, Any]:"
    if marker not in text:
        raise RuntimeError("Could not find _persist_media_asset marker")
    text = text.replace(marker, helper + marker, 1)

old = '''        avatar_asset["persistence"] = _persist_media_asset(avatar_asset)
        avatar_assets.append(avatar_asset)
        generation_jobs.append(
            {
                "job_id": provider_result.get("job_id") or provider_result.get("provider_job_id") or f"avatar_job_{uuid.uuid4().hex[:10]}",
                "media_type": "avatar_video",
                "provider": provider,
                "status": avatar_asset.get("status"),
                "live_generation_available": _provider_configured(provider),
                "live_provider_execution_attempted": provider_result.get("live_provider_execution_attempted", True),
                "real_media_asset_created": avatar_asset.get("real_media_asset_created", False),
                "prompt": avatar_prompt,
            }
        )
'''

new = '''        if _is_provider_endpoint_placeholder(avatar_asset, provider_result):
            if video_assets:
                source_video = dict(video_assets[0])
                avatar_asset = dict(source_video)
                avatar_asset.update(
                    {
                        "asset_id": f"avatar_video_asset_{uuid.uuid4().hex[:10]}",
                        "asset_type": "avatar_video",
                        "media_type": "avatar_video",
                        "provider": source_video.get("provider") or "runway",
                        "status": "fallback_to_real_video_asset",
                        "prompt": avatar_prompt,
                        "script": audio_script,
                        "fallback_reason": "avatar_provider_endpoint_missing",
                        "fallback_source_asset_id": source_video.get("asset_id"),
                        "real_media_asset_created": bool(
                            source_video.get("preview_url")
                            or source_video.get("download_url")
                            or source_video.get("asset_url")
                            or source_video.get("media_url")
                        ),
                    }
                )
            else:
                avatar_asset["status"] = "avatar_provider_endpoint_missing_no_video_fallback"
                avatar_asset["real_media_asset_created"] = False

        if (
            avatar_asset.get("real_media_asset_created")
            or avatar_asset.get("preview_url")
            or avatar_asset.get("download_url")
            or avatar_asset.get("asset_url")
            or avatar_asset.get("media_url")
        ):
            avatar_asset["persistence"] = _persist_media_asset(avatar_asset)
            avatar_assets.append(avatar_asset)

        generation_jobs.append(
            {
                "job_id": provider_result.get("job_id") or provider_result.get("provider_job_id") or f"avatar_job_{uuid.uuid4().hex[:10]}",
                "media_type": "avatar_video",
                "provider": avatar_asset.get("provider") or provider,
                "status": avatar_asset.get("status"),
                "live_generation_available": _provider_configured(provider),
                "live_provider_execution_attempted": provider_result.get("live_provider_execution_attempted", True),
                "real_media_asset_created": avatar_asset.get("real_media_asset_created", False),
                "prompt": avatar_prompt,
            }
        )
'''

if old not in text:
    raise RuntimeError("Exact current avatar persistence/job block not found")

text = text.replace(old, new, 1)
TARGET.write_text(text, encoding="utf-8", newline="\n")

print("AVATAR_PLACEHOLDER_SKIP_AND_VIDEO_FALLBACK_PATCHED")
print(f"Backup: {BACKUP}")