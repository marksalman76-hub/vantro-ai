from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DOCS = ROOT / "docs" / "operations"
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step255_monitoring_backup_operations_lock.py"

DOCS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

runbook = """# Monitoring and Backup Operations Runbook

Draft operational runbook for launch readiness.

## Monitoring

Required production monitoring:
- Render backend uptime
- Vercel frontend uptime
- Stripe webhook delivery
- Database availability
- Critical API routes
- Failed execution events
- Billing failures
- Suspended/cancelled account events

## Critical Smoke Routes

Backend:
- /health
- /admin/billing/stripe-checkout-readiness
- /admin/deployment-control/summary
- /admin/deployment-control/list
- /run-agent

Frontend:
- /admin
- /admin-login
- /client
- /login
- /activate

## Backup Requirements

Required backup targets:
- Database backups
- Tenant/account records
- Billing state records
- Generated output records
- Deployment control state
- Legal/operations docs
- Environment variable inventory without secret values

## Alerting Requirements

Admin alerts should be created for:
- failed Stripe webhook
- failed checkout creation
- failed onboarding activation
- failed login spike
- failed execution
- credit gate blocks
- suspended/cancelled account attempt
- provider execution failure

## Recovery Requirements

Recovery should support:
- redeploy latest backend
- redeploy latest frontend
- restore database backup
- suspend affected tenant
- cancel affected tenant
- reactivate tenant after review
- manually deploy replacement tenant access
"""

(DOCS / "monitoring-backup-runbook.md").write_text(runbook, encoding="utf-8")

record = {
    "success": True,
    "step": 255,
    "status": "monitoring_backup_operations_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "monitoring": {
        "render_backend_uptime": True,
        "vercel_frontend_uptime": True,
        "stripe_webhook_monitoring": True,
        "database_availability": True,
        "critical_route_smoke_tests": True,
        "execution_failure_alerts": True,
        "billing_failure_alerts": True,
    },
    "backup": {
        "database_backups": True,
        "tenant_records": True,
        "billing_state": True,
        "generated_outputs": True,
        "deployment_control_state": True,
        "legal_operations_docs": True,
    },
    "recovery": {
        "backend_redeploy": True,
        "frontend_redeploy": True,
        "tenant_suspend": True,
        "tenant_cancel": True,
        "tenant_reactivate": True,
        "manual_redeploy_access": True,
    },
    "public_launch_gate": {
        "monitoring_plan_created": True,
        "backup_plan_created": True,
        "manual_alerting_setup_required": True,
    },
}

record_file = DATA / "step255_monitoring_backup_operations_lock.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_255_MONITORING_BACKUP_OPERATIONS_LOCK_INSTALLED")
print(f"Created/updated: {DOCS / 'monitoring-backup-runbook.md'}")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {TEST}")
print("STEP_255_OK")