from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"persisted_creative_assets_route_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

shutil.copy2(MAIN_FILE, BACKUP / "main.py")

text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")

if "creative_asset_persistence_bridge import" not in text:
    marker = "from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet\n"
    text = text.replace(
        marker,
        marker + "from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets\n",
        1,
    )

ROUTE = '''

# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_START
@app.get("/admin/persisted-creative-assets")
async def admin_persisted_creative_assets():
    try:
        return get_persisted_creative_assets()
    except Exception as exc:
        return {
            "success": False,
            "layer": "creative_asset_persistence_bridge",
            "status": "unavailable",
            "error": str(exc),
            "credential_values_exposed": False,
        }
# PRODUCTION_CREATIVE_ASSET_PERSISTENCE_BRIDGE_END
'''

if "/admin/persisted-creative-assets" not in text:
    marker = '@app.get("/health", response_model=HealthResponse)'
    if marker not in text:
        raise RuntimeError("Could not find health route marker")
    text = text.replace(marker, ROUTE + "\n" + marker, 1)

MAIN_FILE.write_text(text, encoding="utf-8", newline="\n")

print("PERSISTED_CREATIVE_ASSETS_ROUTE_PATCHED")
print(f"Backup: {BACKUP}")
print(f"Updated: {MAIN_FILE}")