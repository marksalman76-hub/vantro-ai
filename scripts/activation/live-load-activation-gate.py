from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

approved = os.getenv("OWNER_APPROVED_LIVE_LOAD_TEST", "").lower() == "true"

report = {
    "success": True,
    "live_load_activation_gate_ready": True,
    "owner_approved_live_load_test": approved,
    "high_volume_load_allowed": approved,
    "default_allowed_without_owner_approval": "dry_run_or_safe_low_volume_only",
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "live-load-activation-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_LOAD_ACTIVATION_GATE_READY")
print("HIGH_VOLUME_LOAD_ALLOWED:", approved)
