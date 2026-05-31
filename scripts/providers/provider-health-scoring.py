from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"
ops.mkdir(parents=True, exist_ok=True)

providers = {
    "openai": {"configured": False, "health_score": 0, "status": "blocked_missing_secret"},
    "stripe": {"configured": False, "health_score": 0, "status": "blocked_missing_secret"},
    "brevo": {"configured": False, "health_score": 0, "status": "blocked_missing_secret"},
    "postgres": {"configured": False, "health_score": 0, "status": "blocked_missing_database_url"},
    "supabase": {"configured": False, "health_score": 0, "status": "blocked_missing_secret"}
}

report = {
    "success": True,
    "provider_health_scoring_ready": True,
    "live_provider_calls_executed": False,
    "providers": providers,
    "failover_allowed": False,
    "reason": "provider credentials not provisioned yet",
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "provider-health-scoring.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("PROVIDER_HEALTH_SCORING_READY")
print("LIVE_PROVIDER_CALLS_EXECUTED:false")
