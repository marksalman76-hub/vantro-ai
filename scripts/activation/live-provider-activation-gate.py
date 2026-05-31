from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

required = {
    "openai": ["OPENAI_API_KEY"],
    "stripe": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
    "email": ["SMTP_PASSWORD", "BREVO_API_KEY"],
    "database": ["DATABASE_URL"],
    "supabase": ["SUPABASE_SERVICE_ROLE_KEY"],
}

providers = {}
for provider, secrets in required.items():
    missing = [name for name in secrets if not os.getenv(name)]
    providers[provider] = {
        "ready": len(missing) == 0,
        "missing": missing,
        "live_execution_allowed": False
    }

report = {
    "success": True,
    "live_provider_activation_gate_ready": True,
    "live_provider_execution_enabled": False,
    "providers": providers,
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-provider-activation-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_PROVIDER_ACTIVATION_GATE_READY")
print("LIVE_PROVIDER_EXECUTION_ENABLED:false")
