from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN_FILE = ROOT / "backend" / "app" / "main.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"main_unmatched_creative_import_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

shutil.copy2(MAIN_FILE, BACKUP / "main.py")

text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")
lines = text.splitlines()

cleaned = []
skip = False

for line in lines:
    if "creative_asset_persistence_bridge import" in line:
        skip = True
        continue
    if skip:
        if line.strip() == ")":
            skip = False
            continue
        if line.startswith("from ") or line.startswith("import "):
            skip = False
            cleaned.append(line)
            continue
        continue
    cleaned.append(line)

text = "\n".join(cleaned) + "\n"

import_line = (
    "from backend.app.runtime.creative_asset_persistence_bridge import "
    "get_persisted_creative_assets, persist_creative_agent_output\n"
)

if "persist_creative_agent_output" not in text:
    fastapi_index = text.find("from fastapi import")
    if fastapi_index == -1:
        raise RuntimeError("Could not find FastAPI import")

    line_end = text.find("\n", fastapi_index)
    text = text[:line_end + 1] + import_line + text[line_end + 1:]

MAIN_FILE.write_text(text, encoding="utf-8", newline="\n")

print("MAIN_UNMATCHED_CREATIVE_ASSET_IMPORT_FIXED")
print(f"Backup: {BACKUP}")
print(f"Updated: {MAIN_FILE}")