import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
APP = ROOT / "backend" / "app"
DATA = APP / "data"
REPORTS = ROOT / "release_reports"
REPORTS.mkdir(exist_ok=True)

results = []

def add(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(f"{name}: {'OK' if ok else 'WARNING'} {detail}")

def run_cmd(name, cmd, timeout=120):
    try:
        p = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, capture_output=True, timeout=timeout)
        add(name, p.returncode == 0, (p.stdout + p.stderr)[-600:].replace("\n", " "))
    except Exception as e:
        add(name, False, e)

def find_text(name, root, terms):
    hits = []
    for path in Path(root).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".json", ".ts", ".tsx", ".md"}:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue
            if all(term.lower() in text for term in terms):
                hits.append(str(path.relative_to(ROOT)))
    add(name, bool(hits), hits[:15])

def exists(name, path):
    add(name, Path(path).exists(), path)

print("BATCH_H_STRIPE_DEPLOYMENT_READINESS")

# Compile integrity
run_cmd("backend_main_compile", "python -m py_compile backend\\app\\main.py")
run_cmd("storage_adapter_compile", "python -m py_compile backend\\app\\media\\production_storage_adapter.py")
run_cmd("media_store_compile", "python -m py_compile backend\\app\\media\\durable_media_store.py")

# Stripe/billing readiness evidence
find_text("stripe_runtime_present", APP, ["stripe"])
find_text("subscription_runtime_present", APP, ["subscription"])
find_text("webhook_hardening_present", APP, ["webhook"])
find_text("failed_payment_policy_present", APP, ["payment_failed"])
find_text("fixed_cycle_policy_present", APP, ["billing", "cycle"])
find_text("cancel_policy_present", APP, ["cancel_at_period_end"])
find_text("card_storage_safe_present", APP, ["stripe_tokenised_storage_only"])

# Deployment/release artifacts
exists("release_reports_dir_exists", REPORTS)
exists("batch_f_release_report_exists", REPORTS / "batch_f_final_release_lock_report.json")
exists("durable_media_registry_exists", DATA / "durable_media_registry.json")
exists("durable_billing_state_exists", DATA / "durable_billing_state.json")

# Production env readiness checks - warnings only, not failures
env_checks = {
    "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
    "STRIPE_WEBHOOK_SECRET": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
    "MEDIA_STORAGE_PROVIDER": os.getenv("MEDIA_STORAGE_PROVIDER", ""),
    "MEDIA_STORAGE_BUCKET": os.getenv("MEDIA_STORAGE_BUCKET", ""),
    "MEDIA_STORAGE_PUBLIC_BASE_URL": os.getenv("MEDIA_STORAGE_PUBLIC_BASE_URL", ""),
}

for key, value in env_checks.items():
    add(f"env_{key}_configured", bool(value), "configured" if value else "not configured locally")

# Regression locks
run_cmd("batch_d_media_regression", "python test_batch_d_durable_media_persistence.py")
run_cmd("batch_e_commercial_controls_regression", "python test_batch_e_commercial_controls_qa.py", timeout=180)
run_cmd("batch_g_storage_regression", "python test_batch_g_production_storage_adapter.py")

blocking_failures = [
    r for r in results
    if not r["ok"]
    and not r["check"].startswith("env_")
]

env_warnings = [
    r for r in results
    if not r["ok"]
    and r["check"].startswith("env_")
]

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "release_profile": "stripe_deployment_readiness_lock",
    "summary": {
        "total_checks": len(results),
        "passed": len([r for r in results if r["ok"]]),
        "warnings": len([r for r in results if not r["ok"]]),
        "blocking_failures": len(blocking_failures),
        "deployment_lock_passed": len(blocking_failures) == 0,
    },
    "blocking_failures": blocking_failures,
    "env_warnings": env_warnings,
    "interpretation": {
        "env_warnings": "Expected locally unless production secrets are already configured. Do not store secrets in code.",
        "deployment_lock": "Pass means Stripe/storage/deployment code paths and regression locks are present and compiling.",
    },
    "next_required_production_actions": [
        "Configure Stripe live secret key in production environment only.",
        "Configure Stripe webhook secret in production environment only.",
        "Configure MEDIA_STORAGE_PROVIDER, MEDIA_STORAGE_BUCKET, and MEDIA_STORAGE_PUBLIC_BASE_URL in production.",
        "Run one real Stripe subscription test with live-mode product/prices.",
        "Run one real client onboarding walkthrough.",
        "Verify production deployment rollback path after deployment.",
    ],
    "results": results,
}

report_path = REPORTS / "batch_h_stripe_deployment_readiness_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\nBATCH_H_RESULTS")
print(json.dumps(report["summary"], indent=2))
print(f"REPORT_WRITTEN: {report_path}")

if blocking_failures:
    print(json.dumps({"blocking_failures": blocking_failures}, indent=2))
    raise SystemExit("BATCH_H_HAS_BLOCKING_FAILURES")

print("BATCH_H_STRIPE_DEPLOYMENT_READINESS_OK")