from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
incidents = ops / "incidents"
registry = []

if incidents.exists():
    for file in incidents.glob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            registry.append({
                "file": str(file),
                "incident_id": data.get("incident_id"),
                "severity": data.get("severity"),
                "mode": data.get("mode"),
                "live_external_action_executed": data.get("live_external_action_executed", False)
            })
        except Exception as exc:
            registry.append({"file": str(file), "error": str(exc)})

report = {
    "success": True,
    "incident_history_registry_ready": True,
    "incident_count": len(registry),
    "incidents": registry,
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "incident-history-registry.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("INCIDENT_HISTORY_REGISTRY_READY")
print("INCIDENT_COUNT:", len(registry))
