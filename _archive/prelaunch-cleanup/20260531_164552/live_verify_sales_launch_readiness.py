import json
import os
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"name": "homepage", "url": FRONTEND + "/", "expected": [200], "must": ["Ecommerce AI Agent Platform"]},
    {"name": "signup", "url": FRONTEND + "/signup", "expected": [200], "must": ["Ecommerce AI Agent Platform"]},
    {"name": "activate", "url": FRONTEND + "/activate", "expected": [200], "must": ["activation"]},
    {"name": "login", "url": FRONTEND + "/login", "expected": [200], "must": ["Ecommerce AI Agent Platform"]},
    {"name": "client", "url": FRONTEND + "/client", "expected": [200], "must": ["ACTIVE", "INACTIVE", "Business Profile", "Integrations", "Support"]},
    {"name": "billing", "url": FRONTEND + "/client/billing", "expected": [200], "must": ["billing"]},
    {"name": "support", "url": FRONTEND + "/support-request", "expected": [200], "must": ["Ecommerce AI Agent Platform"]},
    {"name": "backend_health", "url": BACKEND + "/health", "expected": [200], "must": []},
    {"name": "admin_runtime_protected", "url": FRONTEND + "/api/admin-runtime", "expected": [401, 403, 405], "must": []},
    {"name": "run_agent_protected", "url": FRONTEND + "/api/run-agent", "expected": [400, 401, 403, 405], "must": []},
]

FORBIDDEN = [
    "traceback",
    "stack trace",
    "internal prompt",
    "system prompt",
    "developer message",
    "raw json",
    "[object Object]",
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
]

results = []

for check in CHECKS:
    req = urllib.request.Request(
        check["url"] + "?row15=sales-launch-readiness",
        headers={"User-Agent": "Row15SalesLaunchVerifier/1.0", "Accept": "text/html,application/json,*/*"},
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            body = response.read().decode("utf-8", errors="ignore")
            status = response.status
            headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        status = exc.code
        headers = dict(exc.headers)
    except Exception as exc:
        results.append({"name": check["name"], "status": "ERROR", "error": str(exc)})
        continue

    lower = body.lower()
    missing = [m for m in check["must"] if m.lower() not in lower]
    forbidden_hits = [f for f in FORBIDDEN if f.lower() in lower]

    results.append({
        "name": check["name"],
        "url": check["url"],
        "status": status,
        "expected": check["expected"],
        "status_ok": status in check["expected"],
        "missing": missing,
        "forbidden_hits": forbidden_hits,
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
    })

status_failures = [r for r in results if not r.get("status_ok")]
missing_failures = [r for r in results if r.get("missing")]
forbidden_failures = [r for r in results if r.get("forbidden_hits")]

summary = {
    "frontend_base_url": FRONTEND,
    "backend_base_url": BACKEND,
    "results": results,
    "status_failures": status_failures,
    "missing_failures": missing_failures,
    "forbidden_failures": forbidden_failures,
    "row15_sales_launch_ready": not status_failures and not missing_failures and not forbidden_failures,
}

print(json.dumps(summary, indent=2))

if not summary["row15_sales_launch_ready"]:
    print("ROW15_SALES_LAUNCH_READINESS_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW15_SALES_LAUNCH_READINESS_VERIFY_PASSED")