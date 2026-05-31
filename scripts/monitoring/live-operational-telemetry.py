from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
ops.mkdir(parents=True, exist_ok=True)

def read(name):
    path = ops / name
    if not path.exists():
        return {"success": False, "missing_report": name}
    return json.loads(path.read_text(encoding="utf-8"))

monitoring = read("operational-monitoring-runtime.json")
incident = read("incident-response-runtime.json")
failover = read("provider-failover-runtime.json")
backup = read("postgres-backup-restore-runtime.json")

report = {
    "success": True,
    "phase": "Phase 2 - Monitoring & incident operations",
    "live_external_actions_enabled": False,
    "telemetry_aggregation_ready": True,
    "sources": {
        "monitoring_runtime": monitoring.get("success") is True,
        "incident_response_runtime": incident.get("success") is True,
        "provider_failover_runtime": failover.get("success") is True,
        "backup_restore_runtime": backup.get("success") is True,
    },
    "operational_readiness_score": sum([
        monitoring.get("success") is True,
        incident.get("success") is True,
        failover.get("success") is True,
        backup.get("success") is True,
    ]),
    "max_score": 4,
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "live-operational-telemetry.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_OPERATIONAL_TELEMETRY_READY")
print("READINESS_SCORE:", report["operational_readiness_score"], "/", report["max_score"])
