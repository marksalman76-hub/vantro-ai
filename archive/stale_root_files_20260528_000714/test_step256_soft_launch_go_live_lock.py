import json
from pathlib import Path

ROOT = Path.cwd()
checklist = ROOT / "docs" / "operations" / "soft-launch-pilot-checklist.md"
record = json.loads((ROOT / "backend" / "app" / "data" / "step256_soft_launch_go_live_lock.json").read_text(encoding="utf-8"))

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "soft_launch_go_live_readiness_locked",
    "checklist_created": checklist.exists(),
    "six_phase_matrix_present": len(record.get("six_phase_launch_matrix", {})) == 6,
    "commercial_beta_ready": record.get("go_live_status", {}).get("commercial_beta_ready") is True,
    "soft_launch_ready": record.get("go_live_status", {}).get("soft_launch_ready") is True,
    "no_major_architecture_remaining": record.get("go_live_status", {}).get("major_architecture_remaining") is False,
    "remaining_public_launch_items_present": len(record.get("remaining_before_public_launch", [])) >= 5,
}

print("STEP_256_SOFT_LAUNCH_GO_LIVE_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_256_SOFT_LAUNCH_GO_LIVE_LOCK_OK")
