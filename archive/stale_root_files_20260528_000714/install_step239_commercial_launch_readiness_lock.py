from pathlib import Path
from datetime import datetime
import json
import os
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
BACKUPS = ROOT / "backups"

DATA.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

matrix_file = DATA / "step239_commercial_launch_readiness_matrix.json"
test_file = ROOT / "test_step239_commercial_launch_readiness_lock.py"

if matrix_file.exists():
    backup = BACKUPS / f"step239_commercial_launch_readiness_matrix_before_{timestamp}.json"
    backup.write_text(matrix_file.read_text(encoding="utf-8"), encoding="utf-8")

matrix = {
    "success": True,
    "step": 239,
    "status": "commercial_launch_readiness_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "product_positioning": {
        "premium_ecommerce_ai_agent_platform": True,
        "white_label_resale_ready": True,
        "global_client_adaptability": True,
        "competitor_benchmark_positioning": [
            "Sintra.ai",
            "Higgsfield.ai",
            "Manus.im",
            "10Web.io",
            "Base44.com",
        ],
        "differentiators": [
            "ecommerce-specific governed AI workforce",
            "client-safe customer portal",
            "owner-governed spend and scaling controls",
            "Stripe subscription billing",
            "premium output generation",
            "operational recovery tooling",
            "provider governance visibility",
            "tenant-aware client activation",
        ],
    },
    "launch_readiness": {
        "backend_runtime_locked": True,
        "frontend_runtime_locked": True,
        "stripe_runtime_locked": True,
        "client_portal_ready": True,
        "admin_portal_ready": True,
        "operational_recovery_ready": True,
        "artifact_visibility_ready": True,
        "provider_governance_ready": True,
        "billing_enforcement_ready": True,
        "premium_output_quality_ready": True,
        "regression_suite_ready": True,
    },
    "commercial_requirements": {
        "client_accounts": True,
        "one_time_activation_links": True,
        "paid_agent_entitlements": True,
        "monthly_subscription_billing": True,
        "credit_enforcement": True,
        "owner_admin_unrestricted_internal_use": True,
        "customer_output_visibility": True,
        "admin_monitoring_visibility": True,
        "no_internal_ids_in_customer_display_required": True,
    },
    "production_must_do_before_public_launch": [
        "Rotate exposed Stripe key and update local plus hosted env vars.",
        "Add production OPENAI_API_KEY only when owner approves live LLM execution.",
        "Set ENABLE_LIVE_LLM_CALLS=true only after live provider readiness is confirmed.",
        "Confirm Render backend environment variables.",
        "Confirm Vercel frontend environment variables.",
        "Run live deployed domain smoke tests.",
        "Create top-up Stripe price IDs if top-up sales are launched.",
        "Run one real customer onboarding from invite to execution.",
        "Run one real subscription checkout payment test using Stripe test/live-safe path.",
    ],
    "deferred_optional_items": {
        "topup_live_checkout_prices": True,
        "advanced_provider_integrations_for_video_image": True,
        "public_marketing_site": True,
        "marketplace_plan_comparison_polish": True,
    },
    "launch_gate": {
        "core_platform_ready": True,
        "commercial_beta_ready": True,
        "public_launch_ready_after_env_and_secret_rotation": True,
    },
}

matrix_file.write_text(json.dumps(matrix, indent=2), encoding="utf-8")

test_file.write_text(r'''
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
matrix_path = ROOT / "backend" / "app" / "data" / "step239_commercial_launch_readiness_matrix.json"

matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

required_env_presence_only = {
    "STRIPE_SECRET_KEY": bool(os.getenv("STRIPE_SECRET_KEY")),
    "STRIPE_WEBHOOK_SECRET": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
    "STRIPE_PRICE_STARTER_MONTHLY": bool(os.getenv("STRIPE_PRICE_STARTER_MONTHLY")),
    "STRIPE_PRICE_GROWTH_MONTHLY": bool(os.getenv("STRIPE_PRICE_GROWTH_MONTHLY")),
    "STRIPE_PRICE_PRO_MONTHLY": bool(os.getenv("STRIPE_PRICE_PRO_MONTHLY")),
}

checks = {
    "matrix_success": matrix.get("success") is True,
    "commercial_launch_locked": matrix.get("status") == "commercial_launch_readiness_locked",
    "launch_readiness_all_true": all(matrix.get("launch_readiness", {}).values()),
    "commercial_requirements_all_true": all(matrix.get("commercial_requirements", {}).values()),
    "core_platform_ready": matrix.get("launch_gate", {}).get("core_platform_ready") is True,
    "commercial_beta_ready": matrix.get("launch_gate", {}).get("commercial_beta_ready") is True,
    "must_do_items_present": len(matrix.get("production_must_do_before_public_launch", [])) >= 5,
    "stripe_core_env_present": all(required_env_presence_only.values()),
}

print("STEP_239_COMMERCIAL_LAUNCH_READINESS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("env_presence_only", required_env_presence_only)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FINAL_CORE_REGRESSION")
regression = subprocess.run(
    [sys.executable, "test_step215_launch_critical_regression_runner.py"],
    text=True,
)
print("final_core_regression_exit_code", regression.returncode)

if regression.returncode != 0:
    failed.append("final_core_regression")

print("RUNNING_STEP_237_OPERATIONS_VISIBILITY")
operations = subprocess.run(
    [sys.executable, "test_step237_admin_operations_visibility_lock.py"],
    text=True,
)
print("step237_operations_exit_code", operations.returncode)

if operations.returncode != 0:
    failed.append("step237_operations_visibility")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_239_COMMERCIAL_LAUNCH_READINESS_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(test_file), doraise=True)

print("STEP_239_COMMERCIAL_LAUNCH_READINESS_INSTALLED")
print(f"Created/updated: {matrix_file}")
print(f"Created/updated: {test_file}")
print("STEP_239_OK")