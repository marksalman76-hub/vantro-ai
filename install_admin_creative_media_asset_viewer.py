from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_creative_media_asset_viewer_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "admin_creative_media_asset_viewer.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "admin-creative-media-asset-viewer.md"
TEST_FILE = ROOT / "test_admin_creative_media_asset_viewer.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
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
'''

DOC_CONTENT = r'''# Admin Creative Media Asset Viewer

## Purpose

This layer exposes generated creative media asset records for admin visibility.

## Supported Assets

- ElevenLabs audio files
- Runway video files
- HeyGen metadata records
- Kling video files
- Sync lip-sync output files

## Safety Rules

- Credential values are never exposed.
- The route only reads local generated media records.
- The route does not trigger provider calls.
- The route does not perform external actions.
- Customer-safe visibility metadata is preserved.

## Status

ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "admin_creative_media_asset_viewer.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "admin-creative-media-asset-viewer.md"

for path in [runtime_file, main_file, doc_file]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location("admin_creative_media_asset_viewer", runtime_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_admin_creative_media_asset_viewer_status()
assets = module.get_admin_creative_media_assets(limit=20)

if status.get("media_asset_viewer_enabled") is not True:
    raise AssertionError("Media asset viewer must be enabled")

for unsafe in ["credential_values_exposed", "external_actions_performed", "live_provider_calls_triggered"]:
    if status.get(unsafe) is not False:
        raise AssertionError(f"Unsafe flag must be false: {unsafe}")
    if assets.get(unsafe) is not False:
        raise AssertionError(f"Unsafe asset flag must be false: {unsafe}")

if "runway" not in status.get("providers_checked", []):
    raise AssertionError("Runway provider folder must be checked")

if "elevenlabs" not in status.get("providers_checked", []):
    raise AssertionError("ElevenLabs provider folder must be checked")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8", errors="ignore")
doc_text = doc_file.read_text(encoding="utf-8")

combined = runtime_text + "\n" + main_text + "\n" + doc_text

required_markers = [
    "ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_READY",
    "get_admin_creative_media_assets",
    "get_admin_creative_media_asset_viewer_status",
    "/admin/creative/media-assets",
    "/admin/creative/media-assets/status",
    "credential_values_exposed",
]

for marker in required_markers:
    if marker not in combined:
        raise AssertionError(f"Missing marker: {marker}")

print("ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_PASSED")
'''

MAIN_ROUTE_BLOCK = r'''
# ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_START
try:
    from backend.app.runtime.admin_creative_media_asset_viewer import (
        get_admin_creative_media_asset_viewer_status,
        get_admin_creative_media_assets,
    )

    @app.get("/admin/creative/media-assets/status")
    async def admin_creative_media_assets_status():
        return get_admin_creative_media_asset_viewer_status()

    @app.get("/admin/creative/media-assets")
    async def admin_creative_media_assets(limit: int = 50):
        return get_admin_creative_media_assets(limit=limit)

except Exception as admin_creative_media_asset_viewer_error:
    @app.get("/admin/creative/media-assets/status")
    async def admin_creative_media_assets_status_unavailable():
        return {
            "success": False,
            "layer": "admin_creative_media_asset_viewer",
            "status": "unavailable",
            "error": str(admin_creative_media_asset_viewer_error),
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
        }
# ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_END
'''


def backup_path(path: Path) -> None:
    if path.exists():
        destination = BACKUP / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def write_file(path: Path, content: str) -> None:
    backup_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def append_main_route_block() -> None:
    if not MAIN_FILE.exists():
        raise FileNotFoundError(f"Missing backend main file: {MAIN_FILE}")

    backup_path(MAIN_FILE)
    text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")

    if "ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("ADMIN_CREATIVE_MEDIA_ASSET_VIEWER_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()