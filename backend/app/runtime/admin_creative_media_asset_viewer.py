from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json


ROOT = Path(__file__).resolve().parents[3]
RUNTIME_OUTPUTS = ROOT / "runtime_outputs"

MEDIA_FOLDERS = {
    "elevenlabs": RUNTIME_OUTPUTS / "elevenlabs_quality_tests",
    "runway": RUNTIME_OUTPUTS / "runway_quality_tests",
    "heygen": RUNTIME_OUTPUTS / "heygen_quality_tests",
    "kling": RUNTIME_OUTPUTS / "kling_quality_tests",
    "sync": RUNTIME_OUTPUTS / "sync_lipsync_quality_tests",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def _asset_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".mp4", ".mov", ".webm"}:
        return "video"
    if suffix in {".mp3", ".wav", ".m4a", ".ogg"}:
        return "audio"
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"
    if suffix == ".json":
        return "metadata"
    return "unknown"


def _collect_provider_assets(provider: str, folder: Path) -> List[Dict[str, Any]]:
    if not folder.exists():
        return []

    assets: List[Dict[str, Any]] = []

    for path in sorted(folder.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
        if not path.is_file():
            continue

        asset_type = _asset_type(path)
        if asset_type == "metadata":
            continue

        metadata_path = path.with_suffix(".json")
        metadata = _read_json(metadata_path) if metadata_path.exists() else {}

        assets.append(
            {
                "provider": provider,
                "asset_type": asset_type,
                "file_name": path.name,
                "local_path": str(path),
                "metadata_path": str(metadata_path) if metadata_path.exists() else None,
                "size_bytes": path.stat().st_size,
                "created_at_unix": path.stat().st_mtime,
                "test_label": metadata.get("test_label"),
                "task_id": metadata.get("task_id") or metadata.get("video_id") or metadata.get("generation_id"),
                "status": metadata.get("status"),
                "credential_values_exposed": False,
                "customer_safe": True,
                "preview_ready": asset_type in {"video", "audio", "image"},
                "download_ready": True,
            }
        )

    return assets


def get_admin_creative_media_assets(limit: int = 50) -> Dict[str, Any]:
    all_assets: List[Dict[str, Any]] = []

    for provider, folder in MEDIA_FOLDERS.items():
        all_assets.extend(_collect_provider_assets(provider, folder))

    all_assets = sorted(all_assets, key=lambda item: item["created_at_unix"], reverse=True)
    limited_assets = all_assets[: max(1, int(limit))]

    return {
        "success": True,
        "layer": "admin_creative_media_asset_viewer",
        "status": "ready",
        "asset_count": len(limited_assets),
        "total_asset_count": len(all_assets),
        "assets": limited_assets,
        "providers_checked": list(MEDIA_FOLDERS.keys()),
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "customer_safe_visibility": True,
        "verified_at": _now(),
    }


def get_admin_creative_media_asset_viewer_status() -> Dict[str, Any]:
    folder_status = {
        provider: {
            "folder": str(folder),
            "exists": folder.exists(),
            "file_count": len(list(folder.glob("*"))) if folder.exists() else 0,
        }
        for provider, folder in MEDIA_FOLDERS.items()
    }

    return {
        "success": True,
        "layer": "admin_creative_media_asset_viewer",
        "status": "ready",
        "media_asset_viewer_enabled": True,
        "supported_asset_types": ["video", "audio", "image", "metadata"],
        "providers_checked": list(MEDIA_FOLDERS.keys()),
        "folder_status": folder_status,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "verified_at": _now(),
    }
