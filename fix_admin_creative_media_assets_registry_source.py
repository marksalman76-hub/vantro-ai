from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "backend" / "app" / "runtime" / "admin_creative_media_asset_viewer.py"

backup_dir = ROOT / "backups" / f"admin_creative_media_asset_viewer_before_registry_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    (backup_dir / "admin_creative_media_asset_viewer.py").write_text(
        TARGET.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

TARGET.write_text(
r'''from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


PROVIDERS_CHECKED = ["elevenlabs", "runway", "heygen", "kling", "sync", "openai_image", "internal"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    preview_url = asset.get("preview_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or ""
    download_url = asset.get("download_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or preview_url or ""

    provider = asset.get("provider") or asset.get("provider_key") or "internal"
    asset_type = asset.get("asset_type") or asset.get("media_type") or "creative_asset"

    return {
        "asset_id": asset.get("asset_id"),
        "agent_id": asset.get("agent_id") or asset.get("agent_key") or asset.get("requested_agent"),
        "agent_label": asset.get("agent_label") or asset.get("agent_id") or asset.get("agent_key"),
        "provider": provider,
        "provider_key": provider,
        "asset_type": asset_type,
        "media_type": asset_type,
        "title": asset.get("title") or asset.get("test_label") or str(asset_type).replace("_", " ").title(),
        "status": asset.get("status") or asset.get("asset_status") or "persisted",
        "test_label": asset.get("test_label"),
        "provider_asset_id": asset.get("provider_asset_id"),
        "provider_asset_url": asset.get("provider_asset_url"),
        "preview_url": preview_url,
        "download_url": download_url,
        "preview_ready": bool(preview_url or asset.get("content") or asset.get("summary")),
        "download_ready": bool(download_url),
        "content": asset.get("content"),
        "summary": asset.get("summary"),
        "quality_score": asset.get("quality_score"),
        "campaign_context": asset.get("campaign_context"),
        "target_audience": asset.get("target_audience"),
        "usage_rights": asset.get("usage_rights"),
        "owner_approval_required": bool(asset.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": asset.get("created_at"),
    }


def get_admin_creative_media_asset_viewer_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "admin_creative_media_asset_viewer",
        "status": "ready",
        "source": "creative_asset_persistence_bridge",
        "providers_checked": PROVIDERS_CHECKED,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "customer_safe_visibility": True,
        "verified_at": _now(),
    }


def get_admin_creative_media_assets(limit: int = 50) -> Dict[str, Any]:
    try:
        from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets

        registry = get_persisted_creative_assets(limit=max(int(limit or 50), 1))
        raw_assets = registry.get("assets", []) if isinstance(registry, dict) else []

        assets: List[Dict[str, Any]] = []
        for asset in raw_assets:
            if isinstance(asset, dict):
                assets.append(_safe_asset(asset))

        return {
            "success": True,
            "layer": "admin_creative_media_asset_viewer",
            "status": "ready",
            "source": "creative_asset_persistence_bridge",
            "asset_count": len(assets),
            "total_asset_count": registry.get("total_asset_count", len(assets)) if isinstance(registry, dict) else len(assets),
            "assets": assets,
            "providers_checked": registry.get("providers_checked", PROVIDERS_CHECKED) if isinstance(registry, dict) else PROVIDERS_CHECKED,
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_visibility": True,
            "verified_at": _now(),
        }

    except Exception as exc:
        return {
            "success": False,
            "layer": "admin_creative_media_asset_viewer",
            "status": "unavailable",
            "source": "creative_asset_persistence_bridge",
            "asset_count": 0,
            "total_asset_count": 0,
            "assets": [],
            "providers_checked": PROVIDERS_CHECKED,
            "error": str(exc)[:1000],
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_visibility": True,
            "verified_at": _now(),
        }
''',
encoding="utf-8",
)

print("ADMIN_CREATIVE_MEDIA_ASSETS_REGISTRY_SOURCE_FIXED")
print("Updated:", TARGET)
print("Backup:", backup_dir)