from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"main_before_execution_event_ledger_import_{timestamp}.py"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

lines = path.read_text(encoding="utf-8").splitlines()
import_line = "from backend.app.core.execution_event_ledger import execution_event_ledger"

if import_line not in lines:
    insert_at = None
    start = None

    for index, line in enumerate(lines):
        if line.strip() == "from backend.app.runtime.execution_stack import (":
            start = index

        if start is not None and index > start and line.strip() == ")":
            insert_at = index + 1
            break

    if insert_at is None:
        raise RuntimeError("Could not find execution_stack import block")

    lines.insert(insert_at, import_line)

path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("EXECUTION_EVENT_LEDGER_IMPORT_FIXED")
print(f"Backup: {backup}")