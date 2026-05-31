from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("backend/app/main.py")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"main_before_quality_failure_payload_scope_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(TARGET, backup_file)

old = '''        add_execution_event(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            event_type="quality_gate_failed",
            title=f"{requested_agent} output rejected by premium quality gate",
            agent_id=requested_agent,
            payload=quality_failure_payload,
        )
'''

new = '''        add_execution_event(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            event_type="approval_gate_blocked",
            title=f"{requested_agent} action blocked before quality review",
            agent_id=requested_agent,
            payload=blocked_payload,
        )
'''

if old not in content:
    raise RuntimeError("Target quality_failure_payload misuse block not found.")

content = content.replace(old, new, 1)

TARGET.write_text(content, encoding="utf-8")

print("QUALITY_FAILURE_PAYLOAD_SCOPE_FIXED")
print("Backup:", backup_file)