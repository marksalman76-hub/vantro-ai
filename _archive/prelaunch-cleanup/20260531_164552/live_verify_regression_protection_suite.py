import json
import os
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

TESTS = [
    {
        "name": "frontend_home",
        "url": FRONTEND + "/?row14=regression",
        "expected": [200],
        "must_contain": ["Ecommerce AI Agent Platform"],
    },
    {
        "name": "client_workspace",
        "url": FRONTEND + "/client?row14=regression",
        "expected": [200],
        "must_contain": [
            "ACTIVE",
            "INACTIVE",
            "Business Profile",
            "Integrations",
            "Support",
        ],
    },
    {
        "name": "signup",
        "url": FRONTEND + "/signup?row14=regression",
        "expected": [200],
        "must_contain": ["Ecommerce AI Agent Platform"],
    },
    {
        "name": "activate",
        "url": FRONTEND + "/activate?row14=regression",
        "expected": [200],
        "must_contain": ["activation"],
    },
    {
        "name": "billing",
        "url": FRONTEND + "/client/billing?row14=regression",
        "expected": [200],
        "must_contain": ["billing"],
    },
    {
        "name": "admin",
        "url": FRONTEND + "/admin?row14=regression",
        "expected": [200],
        "must_contain": ["Readiness"],
    },
    {
        "name": "backend_health",
        "url": BACKEND + "/health",
        "expected": [200],
        "must_contain": [],
    },
    {
        "name": "admin_runtime_protected",
        "url": FRONTEND + "/api/admin-runtime",
        "expected": [401, 403, 405],
        "must_contain": [],
    },
    {
        "name": "provider_summary_protected",
        "url": FRONTEND + "/api/admin-provider-execution/summary",
        "expected": [401, 403, 405],
        "must_contain": [],
    },
    {
        "name": "run_agent_protected",
        "url": FRONTEND + "/api/run-agent",
        "expected": [400, 401, 403, 405],
        "must_contain": [],
    },
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

for test in TESTS:
    req = urllib.request.Request(
        test["url"],
        headers={
            "User-Agent": "Row14RegressionVerifier/1.0",
            "Accept": "application/json,text/html,*/*",
        },
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
        results.append({
            "name": test["name"],
            "status": "ERROR",
            "error": str(exc),
        })
        continue

    lower = body.lower()

    missing = [
        item for item in test["must_contain"]
        if item.lower() not in lower
    ]

    forbidden_hits = [
        item for item in FORBIDDEN
        if item.lower() in lower
    ]

    results.append({
        "name": test["name"],
        "url": test["url"],
        "status": status,
        "expected": test["expected"],
        "status_ok": status in test["expected"],
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
    "row14_regression_protection_ready": (
        not status_failures
        and not missing_failures
        and not forbidden_failures
    ),
}

print(json.dumps(summary, indent=2))

if not summary["row14_regression_protection_ready"]:
    print("ROW14_REGRESSION_PROTECTION_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW14_REGRESSION_PROTECTION_VERIFY_PASSED")