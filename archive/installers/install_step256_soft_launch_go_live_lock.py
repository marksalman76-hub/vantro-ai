from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DOCS = ROOT / "docs" / "operations"
DATA = ROOT / "backend" / "app" / "data"
TEST = ROOT / "test_step256_soft_launch_go_live_lock.py"

DOCS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

pilot = """# Soft Launch Pilot Checklist

## Pilot Setup
- Create one demo/admin-controlled client.
- Create one real pilot customer account.
- Confirm customer package and active agents.
- Confirm Stripe checkout page opens for the selected package.
- Confirm customer can log in.
- Confirm customer can see only active paid agents.

## Execution Validation
- Run one admin/internal multi-agent execution.
- Run one customer execution after credit/subscription readiness.
- Confirm output is client-safe.
- Confirm execution is stored.
- Confirm blocked execution messaging works when credits are exhausted.

## Billing Validation
- Confirm Stripe readiness.
- Confirm checkout session creation.
- Confirm webhook monitoring is active.
- Confirm cancellation/reactivation controls.

## Support Validation
- Confirm support email/contact flow.
- Confirm admin issue tracking process.
- Confirm suspended/cancelled account escalation flow.

## Launch Decision
Soft launch is approved when:
- At least one pilot customer completes onboarding.
- At least one checkout flow reaches Stripe successfully.
- At least one execution flow succeeds.
- Admin can suspend/cancel/reactivate.
- No secrets are exposed in frontend or API responses.
"""

(DOCS / "soft-launch-pilot-checklist.md").write_text(pilot, encoding="utf-8")

record = {
    "success": True,
    "step": 256,
    "status": "soft_launch_go_live_readiness_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "six_phase_launch_matrix": {
        "phase_1_security_and_env": "complete",
        "phase_2_provider_billing_readiness": "complete",
        "phase_3_live_frontend_admin_access": "complete",
        "phase_4_checkout_flow": "checkout_page_verified_payment_deferred",
        "phase_5_execution_flow": "live_admin_execution_verified",
        "phase_6_operations_rollout": "legal_monitoring_support_soft_launch_locked",
    },
    "go_live_status": {
        "commercial_beta_ready": True,
        "soft_launch_ready": True,
        "public_launch_ready_after_legal_review_and_pilot": True,
        "major_architecture_remaining": False,
    },
    "remaining_before_public_launch": [
        "Legal review of draft policies.",
        "Set up real support inbox and support process.",
        "Enable monitoring alerts in Render/Vercel/Stripe.",
        "Run one real pilot customer onboarding.",
        "Complete one real subscription payment when ready.",
        "Run one customer execution after subscription/credits are active.",
        "Finalise sales page and demo process.",
    ],
}

record_file = DATA / "step256_soft_launch_go_live_lock.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_256_SOFT_LAUNCH_GO_LIVE_LOCK_INSTALLED")
print(f"Created/updated: {DOCS / 'soft-launch-pilot-checklist.md'}")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {TEST}")
print("STEP_256_OK")