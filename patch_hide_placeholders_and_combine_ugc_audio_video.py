from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

# ---------- Patch admin creative assets viewer ----------
VIEWER = ROOT / "frontend/src/app/admin/creative-assets/page.tsx"
VIEWER_BACKUP = ROOT / "backups" / f"creative_viewer_hide_placeholders_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
VIEWER_BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(VIEWER, VIEWER_BACKUP / "page.tsx")

text = VIEWER.read_text(encoding="utf-8")

helper = '''
function isPlaceholderAsset(asset: CreativeMediaAsset): boolean {
  const status = String(asset.status || "").toLowerCase();
  return status.includes("live_provider_ready_endpoint_missing") || status.includes("endpoint_missing");
}

'''

if "function isPlaceholderAsset" not in text:
    marker = "function getPreviewUrl(asset: CreativeMediaAsset): string {"
    if marker not in text:
        raise RuntimeError("Viewer getPreviewUrl marker not found")
    text = text.replace(marker, helper + marker, 1)

text = text.replace(
    '''  const hasPreview = Boolean(previewUrl);
  const hasDownload = Boolean(downloadUrl);''',
    '''  const isPlaceholder = isPlaceholderAsset(asset);
  const hasPreview = Boolean(previewUrl) && !isPlaceholder;
  const hasDownload = Boolean(downloadUrl) && !isPlaceholder;'''
)

text = text.replace(
    '''      ) : (
        <div style={warningBoxStyle}>
          Signed backend preview URL unavailable. This asset will not use the raw provider URL.
        </div>
      )}''',
    '''      ) : (
        <div style={warningBoxStyle}>
          {isPlaceholder
            ? "Provider endpoint missing — no real media file was generated yet."
            : "Signed backend preview URL unavailable. This asset will not use the raw provider URL."}
        </div>
      )}'''
)

VIEWER.write_text(text, encoding="utf-8", newline="\n")

# ---------- Patch shared media runtime to compose audio+video ----------
RUNTIME = ROOT / "backend/app/runtime/shared_creative_media_generation_runtime.py"
RUNTIME_BACKUP = ROOT / "backups" / f"shared_media_combine_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
RUNTIME_BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(RUNTIME, RUNTIME_BACKUP / "shared_creative_media_generation_runtime.py")

rt = RUNTIME.read_text(encoding="utf-8")

compose_helper = '''
def _compose_video_audio_asset(
    video_assets: List[Dict[str, Any]],
    audio_assets: List[Dict[str, Any]],
    agent_id: str,
    tenant_id: str,
    pack_id: str,
    prompt: str,
) -> Dict[str, Any]:
    if not video_assets or not audio_assets:
        return {}

    video = video_assets[0]
    audio = audio_assets[0]

    video_url = video.get("download_url") or video.get("preview_url") or video.get("asset_url") or video.get("media_url")
    audio_url = audio.get("download_url") or audio.get("preview_url") or audio.get("asset_url") or audio.get("media_url")

    if not video_url or not audio_url:
        return {}

    try:
        from backend.app.runtime.sync_live_lipsync_adapter import compose_lipsync_video
        composed = compose_lipsync_video(
            video_url=video_url,
            audio_url=audio_url,
            script=audio.get("script") or audio.get("prompt") or prompt,
            tenant_id=tenant_id,
            agent_id=agent_id,
        )
    except Exception as exc:
        return {
            "success": False,
            "status": "combined_video_compose_failed",
            "error": str(exc)[:500],
        }

    composed_url = (
        composed.get("composed_video_url")
        or composed.get("final_video_url")
        or composed.get("video_url")
        or composed.get("download_url")
        or composed.get("video_path")
    )

    if not composed_url:
        return {
            "success": False,
            "status": composed.get("status") or "combined_video_not_available",
            "compose_result": composed,
        }

    return {
        "success": True,
        "asset_id": f"combined_video_asset_{uuid.uuid4().hex[:10]}",
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "pack_id": pack_id,
        "provider": composed.get("provider") or "sync",
        "asset_type": "combined_video",
        "media_type": "combined_video",
        "status": composed.get("status") or "combined_video_created",
        "asset_url": composed_url,
        "preview_url": composed_url,
        "download_url": composed_url,
        "prompt": prompt,
        "script": audio.get("script") or audio.get("prompt") or prompt,
        "real_media_asset_created": True,
        "source_video_asset_id": video.get("asset_id"),
        "source_audio_asset_id": audio.get("asset_id"),
        "provider_result": composed,
    }

'''

if "def _compose_video_audio_asset" not in rt:
    marker = "def _is_provider_endpoint_placeholder(asset: Dict[str, Any], result: Dict[str, Any]) -> bool:"
    if marker not in rt:
        marker = "def _persist_media_asset(asset: Dict[str, Any]) -> Dict[str, Any]:"
    if marker not in rt:
        raise RuntimeError("Runtime helper marker not found")
    rt = rt.replace(marker, compose_helper + marker, 1)

old_media = '''    media_assets = [*image_assets, *video_assets, *audio_assets, *avatar_assets]

    return {
        "success": True,
        "media_pack_id": pack_id,'''

new_media = '''    combined_video_assets: List[Dict[str, Any]] = []
    combined_video_asset = _compose_video_audio_asset(
        video_assets=video_assets,
        audio_assets=audio_assets,
        agent_id=agent_id,
        tenant_id=tenant_id,
        pack_id=pack_id,
        prompt=task,
    )
    if combined_video_asset.get("success") and combined_video_asset.get("real_media_asset_created"):
        combined_video_asset["persistence"] = _persist_media_asset(combined_video_asset)
        combined_video_assets.append(combined_video_asset)

    media_assets = [*image_assets, *combined_video_assets, *video_assets, *audio_assets, *avatar_assets]

    return {
        "success": True,
        "media_pack_id": pack_id,'''

if old_media not in rt:
    raise RuntimeError("media_assets return block not found")

rt = rt.replace(old_media, new_media, 1)

rt = rt.replace(
    '''        "audio_assets": audio_assets,
        "video_assets": video_assets,
        "avatar_assets": avatar_assets,
        "media_assets": media_assets,''',
    '''        "audio_assets": audio_assets,
        "video_assets": video_assets,
        "combined_video_assets": combined_video_assets,
        "avatar_assets": avatar_assets,
        "media_assets": media_assets,'''
)

rt = rt.replace(
    '''        "video_url": video_assets[0].get("download_url", "") if video_assets else "",
        "avatar_video_url": avatar_assets[0].get("download_url", "") if avatar_assets else "",''',
    '''        "video_url": combined_video_assets[0].get("download_url", "") if combined_video_assets else (video_assets[0].get("download_url", "") if video_assets else ""),
        "combined_video_url": combined_video_assets[0].get("download_url", "") if combined_video_assets else "",
        "avatar_video_url": avatar_assets[0].get("download_url", "") if avatar_assets else "",'''
)

RUNTIME.write_text(rt, encoding="utf-8", newline="\n")

print("HIDE_PLACEHOLDERS_AND_COMBINE_UGC_AUDIO_VIDEO_PATCHED")
print(f"Viewer backup: {VIEWER_BACKUP}")
print(f"Runtime backup: {RUNTIME_BACKUP}")