from pathlib import Path
from datetime import datetime
import json
import os

ROOT = Path.cwd()
activation = ROOT / "telemetry" / "activation"

def read(name):
    path = activation / name
    if not path.exists():
        return {"success": False, "missing": name}
    return json.loads(path.read_text(encoding="utf-8"))

provisioning = read("live-production-provisioning-verifier.json")

owner_approved = os.getenv("OWNER_APPROVED_LIVE_ACTIVATION", "").lower() == "true"
load_approved = os.getenv("OWNER_APPROVED_LIVE_LOAD_TEST", "").lower() == "true"

report = {
    "success": provisioning.get("success") is True and owner_approved,
    "mode": "final_live_activation_verifier",
    "provisioning_ready": provisioning.get("success") is True,
    "owner_approved_live_activation": owner_approved,
    "owner_approved_live_load_test": load_approved,
    "live_provider_execution_allowed": provisioning.get("success") is True and owner_approved,
    "high_volume_load_allowed": provisioning.get("success") is True and owner_approved and load_approved,
    "secret_values_exposed": False,
    "activation_state": (
        "live_activation_allowed"
        if provisioning.get("success") is True and owner_approved
        else "blocked_pending_provisioning_or_owner_approval"
    ),
    "generated_at": datetime.utcnow().isoformat()
}

out = activation / "final-live-activation-verifier.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("FINAL_LIVE_ACTIVATION_VERIFIER_COMPLETED")
print("ACTIVATION_STATE:", report["activation_state"])
print("LIVE_PROVIDER_EXECUTION_ALLOWED:", report["live_provider_execution_allowed"])
print("HIGH_VOLUME_LOAD_ALLOWED:", report["high_volume_load_allowed"])
