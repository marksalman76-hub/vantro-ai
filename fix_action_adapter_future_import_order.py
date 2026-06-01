from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"action_adapter_future_import_order_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

future = "from __future__ import annotations\n"

# Remove all misplaced future imports.
s = s.replace(future, "")

# Put future import at absolute top.
s = future + s.lstrip()

TARGET.write_text(s, encoding="utf-8")

print("ACTION_ADAPTER_FUTURE_IMPORT_ORDER_FIXED")
print("Backup:", BACKUP)