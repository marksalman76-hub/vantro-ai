from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py"
BACKUP = ROOT / "backups" / f"avatar_video_fallback_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "shared_creative_media_generation_runtime.py")

text = TARGET.read_text(encoding="utf-8")
original = text

helper = '''
def _is_provider_endpoint_placeholder(asset: Dict[str, Any]) -> bool:
    status = str(asset.get("status") or asset.get("execution_status") or "").lower()
    provider_result = asset.get("provider_result") if isinstance(asset.get("provider_result"), dict) else {}
    provider_status = str(provider_result.get("execution_status") or provider_result.get("status") or "").lower()
    return "live_provider_ready_endpoint_missing" in status or "live_provider_ready_endpoint_missing" in provider_status

'''

if "def _is_provider_endpoint_placeholder" not in text:
    marker = "def _persist_media_asset(asset: Dict[str, Any]) -> Dict[str, Any]:"
    if marker not in text:
        raise RuntimeError("Could not find _persist_media_asset marker")
    text = text.replace(marker, helper + marker, 1)

old = '''        avatar_asset = _normalise_asset_from_result(
            result=provider_result,
            provider=provider,
            media_type="avatar_video",
            agent_id=agent_id,
            tenant_id=tenant_id,
            prompt=avatar_prompt,
        )
        avatar_asset["persistence"] = _persist_media_asset(avatar_asset)
        avatar_assets.append(avatar_asset)
'''

new = '''        avatar_asset = _normalise_asset_from_result(
            result=provider_result,
            provider=provider,
            media_type="avatar_video",
            agent_id=agent_id,
            tenant_id=tenant_id,
            prompt=avatar_prompt,
        )

        # If HeyGen/avatar provider is only endpoint-ready but not actually configured,
        # do not persist a dead video placeholder. Reuse the working generated video
        # asset as the avatar-video fallback so the portal shows a real playable video.
        if _is_provider_endpoint_placeholder(avatar_asset) and video_assets:
            fallback_video = dict(video_assets[0])
            avatar_asset = dict(fallback_video)
            avatar_asset.update({
                "asset_id": f"avatar_video_asset_{uuid.uuid4().hex[:10]}",
                "asset_type": "avatar_video",
                "media_type": "avatar_video",
                "provider": fallback_video.get("provider") or "runway",
                "status": "fallback_to_real_video_asset",
                "prompt": avatar_prompt,
                "script": avatar_prompt,
                "real_media_asset_created": bool(
                    fallback_video.get("preview_url")
                    or fallback_video.get("download_url")
                    or fallback_video.get("asset_url")
                    or fallback_video.get("media_url")
                ),
                "fallback_reason": "avatar_provider_endpoint_missing",
                "fallback_source_asset_id": fallback_video.get("asset_id"),
            })

        # Only persist avatar cards that have a real playable/downloadable media asset.
        if avatar_asset.get("real_media_asset_created") or avatar_asset.get("preview_url") or avatar_asset.get("download_url") or avatar_asset.get("asset_url") or avatar_asset.get("media_url"):
            avatar_asset["persistence"] = _persist_media_asset(avatar_asset)
            avatar_assets.append(avatar_asset)
'''

if old not in text:
    raise RuntimeError("Exact avatar asset block not found")

text = text.replace(old, new, 1)
TARGET.write_text(text, encoding="utf-8", newline="\n")

print("AVATAR_VIDEO_FALLBACK_TO_REAL_VIDEO_ASSET_PATCHED")
print(f"Backup: {BACKUP}")