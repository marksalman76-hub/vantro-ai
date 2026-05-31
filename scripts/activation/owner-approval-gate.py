from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()

approval = os.getenv("OWNER_APPROVED_LIVE_ACTIVATION", "").lower() == "true"

report = {
    "success": True,
    "owner_approval_gate_ready": True,
    "owner_approved_live_activation": approval,
    "live_external_actions_allowed": approval,
    "blocked_if_false": [
        "provider execution",
        "payment execution",
        "email sending",
        "database restore",
        "high-volume load test",
        "provider saturation test"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

out = ROOT / "telemetry" / "activation" / "owner-approval-gate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("OWNER_APPROVAL_GATE_READY")
print("OWNER_APPROVED_LIVE_ACTIVATION:", approval)
print("LIVE_EXTERNAL_ACTIONS_ALLOWED:", approval)
