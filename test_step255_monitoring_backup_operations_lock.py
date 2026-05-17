import json
from pathlib import Path

ROOT = Path.cwd()
runbook = ROOT / "docs" / "operations" / "monitoring-backup-runbook.md"
record = json.loads((ROOT / "backend" / "app" / "data" / "step255_monitoring_backup_operations_lock.json").read_text(encoding="utf-8"))

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "monitoring_backup_operations_locked",
    "runbook_created": runbook.exists(),
    "monitoring_items_locked": all(record.get("monitoring", {}).values()),
    "backup_items_locked": all(record.get("backup", {}).values()),
    "recovery_items_locked": all(record.get("recovery", {}).values()),
    "launch_gate_created": record.get("public_launch_gate", {}).get("monitoring_plan_created") is True,
}

print("STEP_255_MONITORING_BACKUP_OPERATIONS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_255_MONITORING_BACKUP_OPERATIONS_LOCK_OK")
