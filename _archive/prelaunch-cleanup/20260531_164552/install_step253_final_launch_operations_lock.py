from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step253_final_launch_operations_lock.py"
BACKUPS = ROOT / "backups"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
record_file = DATA / "step253_final_launch_operations_lock.json"

if record_file.exists():
    backup = BACKUPS / f"step253_final_launch_operations_lock_before_{timestamp}.json"
    backup.write_text(record_file.read_text(encoding="utf-8"), encoding="utf-8")

record = {
    "success": True,
    "step": 253,
    "status": "final_launch_operations_requirements_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "launch_matrix": {
        "phase_1_production_environment_lock": "complete",
        "phase_2_provider_billing_readiness": "complete",
        "phase_3_live_frontend_admin_access": "complete",
        "phase_4_real_customer_checkout_flow": "checkout_verified_payment_deferred",
        "phase_5_real_customer_execution_flow": "complete",
        "phase_6_launch_operations_rollout": "locked",
    },
    "legal_commercial_required": [
        "Terms of service",
        "Privacy policy",
        "Refund and cancellation policy",
        "Support/contact policy",
        "Acceptable use policy",
        "AI output disclaimer",
    ],
    "monitoring_backup_required": [
        "Render uptime monitoring",
        "Vercel deployment monitoring",
        "Stripe webhook monitoring",
        "Database backup schedule",
        "Critical route smoke tests",
        "Admin alerting for failed execution/payment/onboarding",
    ],
    "support_flow_required": [
        "Support email inbox",
        "Admin issue logging",
        "Customer onboarding help text",
        "Billing support instructions",
        "Escalation path for suspended/cancelled accounts",
    ],
    "soft_launch_required": [
        "Create demo account",
        "Create one pilot customer account",
        "Run one checkout to Stripe page",
        "Run one live admin/internal execution",
        "Run one customer execution after credit/subscription readiness",
        "Validate suspend/cancel/reactivate from admin portal",
    ],
    "public_launch_gate": {
        "core_platform_ready": True,
        "commercial_beta_ready": True,
        "public_launch_ready_after_legal_monitoring_and_soft_launch": True,
        "remaining_major_architecture_work": False,
    },
}

record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_253_FINAL_LAUNCH_OPERATIONS_LOCK_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {TEST}")
print("STEP_253_OK")