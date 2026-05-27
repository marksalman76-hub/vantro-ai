import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step253_final_launch_operations_lock.json").read_text(encoding="utf-8"))

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "final_launch_operations_requirements_locked",
    "six_phase_matrix_present": len(record.get("launch_matrix", {})) == 6,
    "legal_items_present": len(record.get("legal_commercial_required", [])) >= 5,
    "monitoring_items_present": len(record.get("monitoring_backup_required", [])) >= 5,
    "support_items_present": len(record.get("support_flow_required", [])) >= 4,
    "soft_launch_items_present": len(record.get("soft_launch_required", [])) >= 5,
    "core_platform_ready": record.get("public_launch_gate", {}).get("core_platform_ready") is True,
    "commercial_beta_ready": record.get("public_launch_gate", {}).get("commercial_beta_ready") is True,
    "no_major_architecture_work": record.get("public_launch_gate", {}).get("remaining_major_architecture_work") is False,
}

print("STEP_253_FINAL_LAUNCH_OPERATIONS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_253_FINAL_LAUNCH_OPERATIONS_LOCK_OK")
