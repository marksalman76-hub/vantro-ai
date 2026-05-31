from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()

security_dir = ROOT / "telemetry" / "security"
ops_dir = ROOT / "telemetry" / "operations"
load_dir = ROOT / "telemetry" / "load-testing"

def read(path):
    if not path.exists():
        return {"success": False, "missing": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))

phase1 = read(security_dir / "phase1-final-completion-verifier.json")
phase2 = read(ops_dir / "phase2-completion-verifier.json")
phase3 = read(load_dir / "phase3-readiness-verifier.json")
env = read(security_dir / "production-env-validator.json")
provider = read(security_dir / "provider-secret-enforcement.json")

report = {
    "success": (
        phase1.get("success") is True
        and phase2.get("success") is True
        and phase3.get("success") is True
    ),
    "mode": "pre_activation_readiness",
    "live_external_actions_enabled": False,
    "owner_approval_required": True,
    "phase_foundations": {
        "phase1_security": phase1.get("success") is True,
        "phase2_operations": phase2.get("success") is True,
        "phase3_scaling_governance": phase3.get("success") is True
    },
    "production_env_ready": env.get("success") is True,
    "provider_secret_enforcement_ready": provider.get("success") is True,
    "activation_state": "foundations_ready_live_secrets_pending",
    "next_owner_actions": [
        "rotate and provision production secrets",
        "verify Render/Vercel/Supabase env values",
        "run live provider readiness validation",
        "approve controlled live load window",
        "run final production activation verifier"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-activation-readiness.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_ACTIVATION_READINESS_READY")
print("ACTIVATION_STATE:", report["activation_state"])
print("LIVE_EXTERNAL_ACTIONS_ENABLED:false")
