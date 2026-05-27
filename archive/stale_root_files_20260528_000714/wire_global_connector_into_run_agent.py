from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"main_before_global_connector_run_agent_{stamp}.py"
original = MAIN.read_text(encoding="utf-8")
backup.write_text(original, encoding="utf-8")

s = original

import_line = "from backend.app.runtime.global_real_provider_connector_layer import build_global_connector_execution_packet\n"

if import_line not in s:
    lines = s.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line.rstrip())
    s = "\n".join(lines) + "\n"

if '"global_provider_connector"' not in s:
    target = '''        "execution": execution_summary(execution_result)
        if execution_result
        else None,
        "memory": {'''

    replacement = '''        "execution": execution_summary(execution_result)
        if execution_result
        else None,
        "global_provider_connector": build_global_connector_execution_packet({
            "tenant_id": request.tenant_id,
            "requested_agent": request.requested_agent,
            "workflow_stage": request.workflow_stage,
            "action_type": request.action_type,
            "task": request.task,
        }),
        "memory": {'''

    if target not in s:
        raise SystemExit("RUN_AGENT_SUCCESS_RESPONSE_MARKER_NOT_FOUND")

    s = s.replace(target, replacement, 1)

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_global_connector_run_agent_wiring.py"
test.write_text(r'''
from pathlib import Path

main = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "build_global_connector_execution_packet" in main
assert '"global_provider_connector"' in main
assert "global_real_provider_connector_layer" in main

print("GLOBAL_CONNECTOR_RUN_AGENT_WIRING_OK")
''', encoding="utf-8")

print("GLOBAL_CONNECTOR_RUN_AGENT_WIRED")
print(f"Backup: {backup}")
print(f"Created: {test}")