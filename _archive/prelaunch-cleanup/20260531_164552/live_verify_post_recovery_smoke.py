import json
import os
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

CHECKS = [
    ("backend_health", BACKEND + "/health", [200], ["status", "control-api"]),
    ("homepage", FRONTEND + "/", [200], ["Ecommerce AI Agent Platform"]),
    ("admin_login", FRONTEND + "/admin-login", [200], ["Admin control centre"]),
    ("admin_page", FRONTEND + "/admin", [200], ["Owner Command Centre", "AI Workforce Platform"]),
    ("client_page", FRONTEND + "/client", [200], ["Business Profile", "Integrations"]),
    ("signup_page", FRONTEND + "/signup", [200], ["Ecommerce AI Agent Platform"]),
    ("activate_page", FRONTEND + "/activate", [200], ["activation"]),
    ("billing_page", FRONTEND + "/client/billing", [200], ["billing"]),
    ("run_agent_get_protected", FRONTEND + "/api/run-agent", [400, 401, 403, 405], []),
    ("admin_runtime_protected_or_available", FRONTEND + "/api/admin-runtime", [200, 401, 403], []),
]

FORBIDDEN = [
    "Traceback",
    "ModuleNotFoundError",
    "backend.app.system",
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
    "[object Object]",
]

results = []

for name, url, expected, markers in CHECKS:
    req = urllib.request.Request(
        url + ("?post_recovery=1" if "?" not in url else "&post_recovery=1"),
        headers={"User-Agent": "PostRecoverySmokeVerifier/1.0", "Accept": "text/html,application/json,*/*"},
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
        results.append({"name": name, "url": url, "status": "ERROR", "error": str(exc)})
        continue

    missing = [m for m in markers if m.lower() not in body.lower()]
    forbidden_hits = [f for f in FORBIDDEN if f.lower() in body.lower()]

    results.append({
        "name": name,
        "url": url,
        "status": status,
        "expected": expected,
        "status_ok": status in expected,
        "missing": missing,
        "forbidden_hits": forbidden_hits,
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
    })

failures = [
    r for r in results
    if not r.get("status_ok") or r.get("missing") or r.get("forbidden_hits")
]

summary = {
    "frontend_base_url": FRONTEND,
    "backend_base_url": BACKEND,
    "results": results,
    "failures": failures,
    "post_recovery_smoke_passed": not failures,
}

print(json.dumps(summary, indent=2))

if failures:
    print("POST_RECOVERY_SMOKE_VERIFY_FAILED")
    raise SystemExit(1)

print("POST_RECOVERY_SMOKE_VERIFY_PASSED")