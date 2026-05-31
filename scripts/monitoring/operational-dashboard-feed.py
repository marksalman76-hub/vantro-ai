from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
ops.mkdir(parents=True, exist_ok=True)

def read(name):
    path = ops / name
    if not path.exists():
        return {"success": False, "missing": name}
    return json.loads(path.read_text(encoding="utf-8"))

feed = {
    "success": True,
    "dashboard_feed_ready": True,
    "phase": "Phase 2 - Monitoring & incident operations",
    "cards": {
        "telemetry": read("live-operational-telemetry.json"),
        "provider_health": read("provider-health-scoring.json"),
        "queue_degradation": read("queue-degradation-detection.json"),
        "incident_pipeline": read("incident-packet-runtime.json"),
        "alert_escalation": read("alert-escalation-pipeline.json"),
        "circuit_breakers": read("circuit-breaker-runtime.json"),
        "restore_simulation": read("restore-simulation-runtime.json"),
        "backup_manifest": read("backup-manifest-runtime.json"),
    },
    "live_external_actions_enabled": False,
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "operational-dashboard-feed.json").write_text(json.dumps(feed, indent=2), encoding="utf-8")

print("OPERATIONAL_DASHBOARD_FEED_READY")
print("CARDS:", len(feed["cards"]))
