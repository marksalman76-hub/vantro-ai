from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
path = root / "backend" / "app" / "main.py"

text = path.read_text(encoding="utf-8")

backup_dir = root / "backups" / f"main_before_persisted_assets_response_shape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "main.py").write_text(text, encoding="utf-8")

old = '''        assets = get_persisted_creative_assets(limit=100)
        return {
            "success": True,
            "layer": "creative_asset_persistence_bridge",
            "status": "available",
            "asset_count": len(assets) if isinstance(assets, list) else 0,
            "assets": assets,
            "credential_values_exposed": False,
        }'''

new = '''        registry = get_persisted_creative_assets(limit=100)
        asset_list = registry.get("assets", []) if isinstance(registry, dict) else []
        return {
            "success": True,
            "layer": "creative_asset_persistence_bridge",
            "status": "available",
            "asset_count": len(asset_list),
            "total_asset_count": registry.get("total_asset_count", len(asset_list)) if isinstance(registry, dict) else len(asset_list),
            "assets": asset_list,
            "providers_checked": registry.get("providers_checked", []) if isinstance(registry, dict) else [],
            "credential_values_exposed": False,
        }'''

if old not in text:
    raise SystemExit("Expected route block not found. No changes made.")

path.write_text(text.replace(old, new), encoding="utf-8")

print("PERSISTED_ASSETS_RESPONSE_SHAPE_FIXED")
print("Backup:", backup_dir)