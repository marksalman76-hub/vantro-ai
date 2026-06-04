from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
path = root / "backend" / "app" / "main.py"

text = path.read_text(encoding="utf-8")

backup_dir = root / "backups" / f"main_before_persisted_creative_assets_route_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "main.py").write_text(text, encoding="utf-8")

start = "# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_START"
end = "# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_END"

start_index = text.index(start)
end_index = text.index(end) + len(end)

replacement = '''# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_START
@app.get("/admin/persisted-creative-assets")
async def admin_persisted_creative_assets():
    try:
        assets = get_persisted_creative_assets(limit=100)
        return {
            "success": True,
            "layer": "creative_asset_persistence_bridge",
            "status": "available",
            "asset_count": len(assets) if isinstance(assets, list) else 0,
            "assets": assets,
            "credential_values_exposed": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "layer": "creative_asset_persistence_bridge",
            "status": "unavailable",
            "error": str(exc),
            "credential_values_exposed": False,
        }
# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_END'''

text = text[:start_index] + replacement + text[end_index:]

path.write_text(text, encoding="utf-8")

print("PERSISTED_CREATIVE_ASSETS_ROUTE_FIXED")
print("Backup:", backup_dir)