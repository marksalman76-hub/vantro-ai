from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN_FILE = ROOT / "backend" / "app" / "main.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"main_fastapi_header_import_fix_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

backup_path = BACKUP_DIR / "main.py"
shutil.copy2(MAIN_FILE, backup_path)

text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")

broken_block = """from fastapi import FastAPI
from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets
, Header"""

fixed_block = """from fastapi import FastAPI, Header

from backend.app.runtime.creative_asset_persistence_bridge import (
    get_persisted_creative_assets,
)"""

if broken_block in text:
    text = text.replace(broken_block, fixed_block, 1)
else:
    text = text.replace("from fastapi import FastAPI\n", "from fastapi import FastAPI, Header\n", 1)
    text = text.replace("\n, Header\n", "\n", 1)

    if "from backend.app.runtime.creative_asset_persistence_bridge import" not in text:
        marker = "from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet\n"
        insert = marker + """from backend.app.runtime.creative_asset_persistence_bridge import (
    get_persisted_creative_assets,
)
"""
        text = text.replace(marker, insert, 1)

MAIN_FILE.write_text(text, encoding="utf-8", newline="\n")

print("MAIN_FASTAPI_HEADER_IMPORT_FIXED")
print(f"Backup: {backup_path}")
print(f"Updated: {MAIN_FILE}")