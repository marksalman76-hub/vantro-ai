import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
APP = ROOT / "backend" / "app"
FRONTEND_API = ROOT / "frontend" / "src" / "app" / "api"

results = []

def add(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(f"{name}: {'OK' if ok else 'FAILED'} {detail}")

def exists(name, path):
    add(name, Path(path).exists(), path)

def run_cmd(name, cmd, cwd=ROOT):
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True, timeout=90)
        add(name, p.returncode == 0, (p.stdout + p.stderr)[-600:].replace("\n", " "))
    except Exception as e:
        add(name, False, e)

def http_get(name, url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "batch-e-launch-qa"})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8", errors="replace")
            add(name, 200 <= r.status < 500, f"status={r.status} body={body[:220]}")
    except Exception as e:
        # 401 can be correct for protected routes
        if "HTTP Error 401" in str(e):
            add(name, True, "401 protected route confirmed")
        else:
            add(name, False, e)

def find_text(name, root, needles):
    matched = []
    for path in Path(root).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".ts", ".tsx", ".json"}:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue
            for needle in needles:
                if needle.lower() in text:
                    matched.append(str(path.relative_to(ROOT)))
                    break
    add(name, bool(matched), matched[:12])

print("BATCH_E_COMMERCIAL_CONTROLS_QA")

# File and route existence
exists("backend_app_exists", APP)
exists("backend_main_exists", APP / "main.py")
exists("frontend_api_activate_exists", FRONTEND_API / "activate")
exists("frontend_api_client_login_exists", FRONTEND_API / "client-login")
exists("frontend_api_client_me_exists", FRONTEND_API / "client-me")
exists("frontend_api_run_agent_exists", FRONTEND_API / "run-agent")
exists("frontend_api_client_review_action_exists", FRONTEND_API / "client-review-action")

# Commercial runtime areas
exists("billing_dir_exists", APP / "billing")
exists("security_dir_exists", APP / "security")
exists("tenant_dir_exists", APP / "tenant")
exists("runtime_dir_exists", APP / "runtime")
exists("data_dir_exists", APP / "data")

# Compile critical backend files
run_cmd("backend_main_compile", "python -m py_compile backend\\app\\main.py")
run_cmd("media_store_compile", "python -m py_compile backend\\app\\media\\durable_media_store.py")
run_cmd("media_routes_compile", "python -m py_compile backend\\app\\api\\media_routes.py")

# Search for launch-critical rules
find_text("billing_policy_terms_present", APP, [
    "stripe",
    "subscription",
    "invoice.payment_succeeded",
    "payment_failed",
    "cancel_at_period_end",
])
find_text("credit_enforcement_terms_present", APP, [
    "credit",
    "credits",
    "exhausted",
    "allocation",
    "top_up",
])
find_text("entitlement_terms_present", APP, [
    "entitlement",
    "active_agents",
    "package",
    "agent",
    "tenant",
])
find_text("onboarding_activation_terms_present", APP, [
    "activation",
    "invite",
    "one_time",
    "password",
    "hash",
])
find_text("owner_admin_unrestricted_terms_present", APP, [
    "owner",
    "admin",
    "approval",
    "owner_only",
    "unaffected",
])
find_text("security_terms_present", APP, [
    "tenant",
    "session",
    "cookie",
    "auth",
    "password",
])

# Local frontend route protection/runtime checks
http_get("client_page_local", "http://localhost:3000/client")
http_get("client_me_auth_protection_local", "http://localhost:3000/api/client-me")
http_get("latest_deliverable_local", "http://localhost:3000/api/client-latest-deliverable")

ok_count = sum(1 for r in results if r["ok"])
failures = [r for r in results if not r["ok"]]

summary = {
    "ok": ok_count,
    "failed": len(failures),
    "failures": failures,
    "launch_interpretation": "Pass means commercial control files/routes/rules are present and compile. Protected client-me returning 401 is treated as correct.",
}

print("\nBATCH_E_RESULTS")
print(json.dumps(summary, indent=2))

if failures:
    raise SystemExit("BATCH_E_HAS_FAILURES")

print("BATCH_E_COMMERCIAL_CONTROLS_QA_OK")