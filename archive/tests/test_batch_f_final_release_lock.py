import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FRONTEND = ROOT / "frontend"
BACKEND_APP = ROOT / "backend" / "app"
REPORTS = ROOT / "release_reports"
REPORTS.mkdir(exist_ok=True)

results = []

def add(name, ok, detail=""):
    item = {"check": name, "ok": bool(ok), "detail": str(detail)}
    results.append(item)
    print(f"{name}: {'OK' if ok else 'FAILED'} {detail}")

def run_cmd(name, cmd, cwd=ROOT, timeout=120):
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True, timeout=timeout)
        add(name, p.returncode == 0, (p.stdout + p.stderr)[-700:].replace("\n", " "))
    except Exception as e:
        add(name, False, e)

def exists(name, path):
    add(name, Path(path).exists(), path)

def contains_any(name, root, terms):
    hits = []
    for path in Path(root).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".ts", ".tsx", ".json"}:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue
            if any(term.lower() in text for term in terms):
                hits.append(str(path.relative_to(ROOT)))
    add(name, bool(hits), hits[:15])

print("BATCH_F_FINAL_RELEASE_LOCK")

# Core files/directories
exists("frontend_client_page_exists", FRONTEND / "src" / "app" / "client" / "page.tsx")
exists("frontend_api_exists", FRONTEND / "src" / "app" / "api")
exists("backend_main_exists", BACKEND_APP / "main.py")
exists("backend_media_store_exists", BACKEND_APP / "media" / "durable_media_store.py")
exists("backend_media_routes_exists", BACKEND_APP / "api" / "media_routes.py")
exists("backend_data_exists", BACKEND_APP / "data")
exists("backups_exists", ROOT / "backups")

# Compile/build
run_cmd("frontend_build", "npm run build", FRONTEND, timeout=180)
run_cmd("backend_main_compile", "python -m py_compile backend\\app\\main.py")
run_cmd("durable_media_compile", "python -m py_compile backend\\app\\media\\durable_media_store.py")
run_cmd("media_routes_compile", "python -m py_compile backend\\app\\api\\media_routes.py")

# Regression scripts
run_cmd("batch_d_media_regression", "python test_batch_d_durable_media_persistence.py")
run_cmd("batch_e_commercial_controls_regression", "python test_batch_e_commercial_controls_qa.py", timeout=180)

# Launch-critical capabilities present
contains_any("governance_owner_approval_present", BACKEND_APP, ["owner approval", "owner_only", "approval_required", "owner_approval"])
contains_any("billing_stripe_present", BACKEND_APP, ["stripe", "subscription", "invoice.payment_succeeded", "payment_failed"])
contains_any("entitlement_present", BACKEND_APP, ["entitlement", "active_agents", "package_status", "tenant"])
contains_any("media_persistence_present", BACKEND_APP, ["durable_media_registry", "persist_deliverable", "register_media_asset"])
contains_any("client_safe_review_present", FRONTEND / "src" / "app" / "client", ["view full deliverable", "approve", "request revision", "copy summary"])

failures = [r for r in results if not r["ok"]]

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "release_profile": "pre_launch_candidate",
    "project": "ecommerce-ai-agent-platform",
    "summary": {
        "total_checks": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "release_lock_passed": len(failures) == 0,
    },
    "known_non_blocking_warnings": [
        "Next.js middleware convention warning: migrate middleware to proxy later.",
        "Local durable media registry is ready; production object storage adapter still recommended before high-volume public launch.",
        "Stripe live mode still requires final production-key and webhook verification.",
    ],
    "remaining_launch_items": [
        "Connect Supabase/R2/S3 production media storage.",
        "Verify Stripe live subscription webhooks with production keys.",
        "Run real customer onboarding walkthrough.",
        "Confirm deployment monitoring and backups.",
        "Create final demo/sales environment.",
    ],
    "results": results,
}

report_path = REPORTS / "batch_f_final_release_lock_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\nBATCH_F_RESULTS")
print(json.dumps(report["summary"], indent=2))
print(f"REPORT_WRITTEN: {report_path}")

if failures:
    print(json.dumps({"failures": failures}, indent=2))
    raise SystemExit("BATCH_F_FINAL_RELEASE_LOCK_FAILED")

print("BATCH_F_FINAL_RELEASE_LOCK_OK")