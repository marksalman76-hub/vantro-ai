from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()

MAIN_FILE = ROOT / "backend" / "app" / "main.py"
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"
PERSIST_FILE = RUNTIME_DIR / "creative_asset_persistence_bridge.py"

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

backup_dir = ROOT / "backups" / f"creative_asset_persistence_bridge_before_{timestamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

if MAIN_FILE.exists():
    shutil.copy2(MAIN_FILE, backup_dir / MAIN_FILE.name)

bridge_code = r'''
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
'''

PERSIST_FILE.write_text(bridge_code, encoding="utf-8")

main_text = MAIN_FILE.read_text(encoding="utf-8")

import_line = (
    "from backend.app.runtime.creative_asset_persistence_bridge "
    "import get_persisted_creative_assets\n"
)

if import_line not in main_text:
    marker = "from fastapi import FastAPI"
    main_text = main_text.replace(marker, marker + "\n" + import_line)

route_block = r'''

@app.get("/admin/persisted-creative-assets")
async def admin_persisted_creative_assets():

    try:
        return get_persisted_creative_assets()
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)
        }
'''

if "/admin/persisted-creative-assets" not in main_text:
    insert_marker = "@app.get(\"/health\")"
    main_text = main_text.replace(insert_marker, route_block + "\n\n" + insert_marker)

MAIN_FILE.write_text(main_text, encoding="utf-8")

print("PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Created: {PERSIST_FILE}")
print(f"Updated: {MAIN_FILE}")