from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
file = ROOT / "backend" / "app" / "runtime" / "provider_connector_registry.py"

backup_dir = ROOT / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"provider_connector_registry_before_future_import_order_fix_{timestamp}.py"
backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

text = file.read_text(encoding="utf-8")

import_block = """from backend.app.runtime.ai_media_live_provider_execution import (
    detect_ai_media_provider_readiness,
    execute_ai_media_provider_ready_packet,
    select_provider_route,
)
"""

text = text.replace(import_block + "\n", "")
text = text.replace(import_block, "")

future_line = "from __future__ import annotations"

if future_line in text:
    text = text.replace(
        future_line,
        future_line + "\n\n" + import_block.strip(),
        1,
    )
else:
    text = import_block.strip() + "\n\n" + text

file.write_text(text, encoding="utf-8")

print("PROVIDER_CONNECTOR_FUTURE_IMPORT_ORDER_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {file}")