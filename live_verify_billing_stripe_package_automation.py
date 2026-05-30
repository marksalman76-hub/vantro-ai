import json
import os
import re
import urllib.request
import urllib.error

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"path": "/client/billing", "method": "GET", "expected": [200, 401, 403]},
    {"path": "/client/billing/success", "method": "GET", "expected": [200, 401, 403]},
    {"path": "/client/billing/cancel", "method": "GET", "expected": [200, 401, 403]},
    {"path": "/client/billing/cancelled", "method": "GET", "expected": [200, 401, 403]},
    {"path": "/api/billing-checkout", "method": "GET", "expected": [400, 401, 403, 405]},
    {"path": "/api/signup-agent-selection/options/starter", "method": "GET", "expected": [200]},
    {"path": "/api/signup-agent-selection/options/growth", "method": "GET", "expected": [200]},
    {"path": "/api/signup-agent-selection/options/business", "method": "GET", "expected": [200]},
    {"path": "/api/signup-agent-selection/options/enterprise", "method": "GET", "expected": [200]},
]

FORBIDDEN_LITERAL = [
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "sk_live_",
    "sk_test_",
    "whsec_",
    "OPENAI_API_KEY",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
    "JWT_SECRET",
    "raw json",
    "traceback",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bwhsec_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
]

PACKAGE_EXPECTATIONS = {
    "/api/signup-agent-selection/options/starter": {
        "plan": "starter",
        "max_selectable_agents": 3,
        "head_agent_available": False,
    },
    "/api/signup-agent-selection/options/growth": {
        "plan": "growth",
        "max_selectable_agents": 6,
        "head_agent_available": False,
    },
    "/api/signup-agent-selection/options/business": {
        "plan": "business",
        "max_selectable_agents": 12,
        "head_agent_available": False,
    },
    "/api/signup-agent-selection/options/enterprise": {
        "plan": "enterprise",
        "max_selectable_agents": 27,
        "head_agent_available": True,
    },
}

def forbidden_hits(body):
    hits = []
    lower = body.lower()

    for item in FORBIDDEN_LITERAL:
        if item.lower() in lower:
            hits.append(item)

    for pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(body)
        if match:
            hits.append(match.group(0))

    return sorted(set(hits))

def fetch(check):
    path = check["path"]
    url = BASE + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row5BillingStripeVerifier/1.0",
            "Accept": "text/html,application/json,*/*",
        },
        method=check["method"],
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8", errors="ignore")
            status = response.status
            headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        status = exc.code
        headers = dict(exc.headers)
    except Exception as exc:
        return {
            "path": path,
            "method": check["method"],
            "status": "ERROR",
            "error": str(exc),
            "expected_status": check["expected"],
            "status_ok": False,
            "forbidden_hits": [],
        }

    result = {
        "path": path,
        "method": check["method"],
        "status": status,
        "expected_status": check["expected"],
        "status_ok": status in check["expected"],
        "content_type": headers.get("Content-Type") or headers.get("content-type", ""),
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
        "body_sample": body[:800],
        "forbidden_hits": forbidden_hits(body),
    }

    if path in PACKAGE_EXPECTATIONS and status == 200:
        try:
            data = json.loads(body)
        except Exception as exc:
            result["package_check"] = {"ok": False, "error": f"Invalid JSON: {exc}"}
            return result

        expected = PACKAGE_EXPECTATIONS[path]
        package_errors = []

        for key, value in expected.items():
            if data.get(key) != value:
                package_errors.append({
                    "field": key,
                    "expected": value,
                    "actual": data.get(key),
                })

        if data.get("credential_values_exposed") is not False:
            package_errors.append({
                "field": "credential_values_exposed",
                "expected": False,
                "actual": data.get("credential_values_exposed"),
            })

        if data.get("customer_safe") is not True:
            package_errors.append({
                "field": "customer_safe",
                "expected": True,
                "actual": data.get("customer_safe"),
            })

        result["package_check"] = {
            "ok": not package_errors,
            "errors": package_errors,
            "available_count": data.get("available_count"),
            "selection_required": data.get("selection_required"),
        }

    return result

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]
package_failures = [
    {"path": r["path"], "package_check": r["package_check"]}
    for r in results
    if r.get("package_check") and not r["package_check"].get("ok")
]

summary = {
    "frontend_base_url": BASE,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "package_failures": package_failures,
    "row5_ready": not failed_status and not forbidden and not package_failures,
}

print(json.dumps(summary, indent=2))

if not summary["row5_ready"]:
    print("ROW5_BILLING_STRIPE_PACKAGE_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW5_BILLING_STRIPE_PACKAGE_VERIFY_PASSED")