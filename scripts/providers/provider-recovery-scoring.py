from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
ops.mkdir(parents=True, exist_ok=True)

health_path = ops / "provider-health-scoring.json"
health = json.loads(health_path.read_text(encoding="utf-8")) if health_path.exists() else {}

providers = health.get("providers", {})
scores = {}

for name, data in providers.items():
    configured = data.get("configured") is True
    base_score = 100 if configured else 0
    scores[name] = {
        "configured": configured,
        "recovery_score": base_score,
        "failover_ready": configured,
        "status": data.get("status", "unknown")
    }

report = {
    "success": True,
    "provider_recovery_scoring_ready": True,
    "live_provider_calls_executed": False,
    "scores": scores,
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "provider-recovery-scoring.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("PROVIDER_RECOVERY_SCORING_READY")
print("PROVIDERS:", len(scores))
