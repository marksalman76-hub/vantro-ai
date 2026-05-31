from pathlib import Path
from datetime import datetime
import json
import uuid

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
incident_dir = ops / "incidents"
incident_dir.mkdir(parents=True, exist_ok=True)

packet = {
    "incident_id": "dryrun-" + str(uuid.uuid4()),
    "severity": "medium",
    "mode": "dry_run",
    "live_external_action_executed": False,
    "owner_notification_required": False,
    "summary": "Phase 2 incident packet persistence dry run",
    "recommended_actions": [
        "review incident packet",
        "confirm provider health",
        "escalate only if live runtime signal appears"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

path = incident_dir / f"{packet['incident_id']}.json"
path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

summary = {
    "success": True,
    "incident_packet_runtime_ready": True,
    "packet_created": str(path),
    "mode": "dry_run",
    "live_external_action_executed": False
}

(ops / "incident-packet-runtime.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

print("INCIDENT_PACKET_RUNTIME_READY")
print("MODE:dry_run")
