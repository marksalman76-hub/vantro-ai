from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"non_owned_autonomous_route_marker_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old = '''            packet_result.update({
                "execution_status": "agent_not_owned",
                "delegate_execution": "blocked",
                "recommendation_visibility": True,
                "upsell_visibility": True,
                "execution_preview": "allowed",
                "completed_output": None,
                "upgrade_recommendation": assigned_agent,
            })
'''

new = '''            packet_result.update({
                "execution_status": "agent_not_owned",
                "delegate_execution": "blocked",
                "recommendation_visibility": True,
                "upsell_visibility": True,
                "execution_preview": "allowed",
                "completed_output": None,
                "upgrade_recommendation": assigned_agent,
                "autonomous_governance": True,
                "autonomous_route": "recommendation_only",
                "performed_actual_action": False,
                "real_execution": False,
            })
'''

if old not in content:
    raise SystemExit("NON_OWNED_BLOCK_NOT_FOUND")

content = content.replace(old, new)
runtime_file.write_text(content, encoding="utf-8")

print("NON_OWNED_AUTONOMOUS_ROUTE_MARKER_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")