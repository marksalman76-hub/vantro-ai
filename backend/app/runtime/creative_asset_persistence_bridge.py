
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[3]

REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_FILE = REGISTRY_DIR / "creative_assets.json"

def _load_registry():
    if not REGISTRY_FILE.exists():
        return []

    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def _save_registry(data):
    REGISTRY_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

def persist_creative_asset(asset_packet: dict):
    registry = _load_registry()

    packet = {
        "provider": asset_packet.get("provider"),
        "asset_type": asset_packet.get("asset_type"),
        "test_label": asset_packet.get("test_label"),
        "provider_asset_url": asset_packet.get("provider_asset_url"),
        "provider_asset_id": asset_packet.get("provider_asset_id"),
        "preview_url": asset_packet.get("preview_url"),
        "download_url": asset_packet.get("download_url"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "governed": True,
        "credential_values_exposed": False
    }

    registry.insert(0, packet)

    registry = registry[:200]

    _save_registry(registry)

    return {
        "success": True,
        "registry_count": len(registry)
    }

def get_persisted_creative_assets():
    registry = _load_registry()

    return {
        "success": True,
        "asset_count": len(registry),
        "assets": registry
    }
