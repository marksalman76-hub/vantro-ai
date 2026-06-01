from pathlib import Path
from datetime import datetime, timezone
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

BACKUP = ROOT / "backups" / f"insert_ugc_route_action_adapter_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

route = r'''
    if assigned_agent == "ugc_creative_agent":
        ugc_output = _generate_ugc_creative_deliverable(user_requested_task)
        return {
            "success": True,
            "execution_id": f"ugc_exec_{uuid4().hex[:12]}",
            "adapter": "ugc_creative_deliverable_adapter",
            "tenant_id": tenant_id,
            "performed_actual_action": True,
            "execution_status": "creative_deliverable_generated",
            "customer_safe": True,
            "credential_values_exposed": False,
            "external_provider_called": False,
            "live_external_call_executed": False,
            "actions_performed": [
                {
                    "type": "ugc_campaign_deliverable_created",
                    "status": "created",
                    "target_system": "creative_deliverable_runtime",
                    "record_id": f"ugc_{uuid4().hex[:10]}",
                }
            ],
            "output": ugc_output,
            "asset": {
                "asset_id": f"asset_{uuid4().hex[:12]}",
                "status": "created",
                "preview_ready": True,
                "download_ready": False,
                "customer_safe": True,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

'''

# Add needed import if missing.
if "from uuid import uuid4" not in s:
    s = s.replace("from __future__ import annotations\n", "from __future__ import annotations\nfrom uuid import uuid4\n")

if "from datetime import datetime, timezone" not in s:
    s = s.replace("from __future__ import annotations\n", "from __future__ import annotations\nfrom datetime import datetime, timezone\n")

# Insert after assigned_agent is set inside execute_action_adapter.
needle = '    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip()'
if needle not in s:
    needle = '    assigned_agent = packet.get("assigned_agent")'

if needle not in s:
    raise SystemExit("Could not find assigned_agent assignment in execute_action_adapter.")

if 'if assigned_agent == "ugc_creative_agent":' not in s:
    s = s.replace(needle, needle + "\n" + route)

TARGET.write_text(s, encoding="utf-8")

print("UGC_ROUTE_INSERTED_INTO_ACTION_ADAPTER")
print("Backup:", BACKUP)