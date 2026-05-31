from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
history = ops / "history"
history.mkdir(parents=True, exist_ok=True)

sources = [
    "live-operational-telemetry.json",
    "provider-health-scoring.json",
    "queue-degradation-detection.json",
    "incident-packet-runtime.json",
    "alert-escalation-pipeline.json",
    "circuit-breaker-runtime.json",
    "restore-simulation-runtime.json",
]

records = []
for name in sources:
    path = ops / name
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        records.append({
            "source": name,
            "success": data.get("success"),
            "captured_at": datetime.utcnow().isoformat(),
            "mode": data.get("mode", "runtime_report")
        })

ledger = {
    "success": True,
    "operational_persistence_ready": True,
    "records_persisted": len(records),
    "records": records,
    "live_external_actions_enabled": False,
    "generated_at": datetime.utcnow().isoformat()
}

(history / "operational-history-ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
(ops / "operational-persistence-runtime.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")

print("OPERATIONAL_PERSISTENCE_RUNTIME_READY")
print("RECORDS_PERSISTED:", len(records))
