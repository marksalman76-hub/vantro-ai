import json
import os
import re
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"base": FRONTEND, "path": "/", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/client", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/signup", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/activate", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/login", "method": "GET", "expected": [200, 404]},
    {"base": FRONTEND, "path": "/admin", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/client/billing", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/run-agent", "method": "GET", "expected": [400, 401, 403, 405]},
    {"base": FRONTEND, "path": "/api/client-integrations", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/client-execution-matrix", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/admin-runtime", "method": "GET", "expected": [401, 403, 405]},
    {"base": FRONTEND, "path": "/api/admin-provider-execution/summary", "method": "GET", "expected": [401, 403, 405]},
    {"base": BACKEND, "path": "/health", "method": "GET", "expected": [200]},
]

FORBIDDEN_LITERAL = [
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
    "JWT_SECRET",
    "access_token",
    "refresh_token",
    "client_secret",
    "api_secret",
    "private_key",
    "bearer ",
    "internal prompt",
    "system prompt",
    "developer message",
    "backend architecture",
    "raw json",
    "traceback",
    "stack trace",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bwhsec_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
]

SAFE_EXCEPTIONS = [
    "client_demo_001",
    "credential_hint",
    "credential_values_exposed",
    "customer_safe",
    "request_details_protected",
    "system_details_protected",
]

REQUIRED_ROUTE_SIGNALS = {
    "/client": ["ACTIVE", "INACTIVE", "Agent selections are locked after activation", "owner/admin approval"],
    "/signup": ["Ecommerce AI Agent Platform"],
    "/activate": ["Ecommerce AI Agent Platform"],
}

def forbidden_hits(body):
    hits = []
    lower = body.lower()

    for item in FORBIDDEN_LITERAL:
        if item.lower() in lower and item.lower() not in [x.lower() for x in SAFE_EXCEPTIONS]:
            hits.append(item)

    for pattern in FORBIDDEN_PATTERNS:
        match = pattern.search(body)
        if match:
            value = match.group(0)
            if value not in SAFE_EXCEPTIONS:
                hits.append(value)

    return sorted(set(hits))

def marker_hits(path, body):
    required = REQUIRED_ROUTE_SIGNALS.get(path, [])
    return {marker: marker in body for marker in required}

def fetch(check):
    url = check["base"] + check["path"] + "?row11=production-readiness"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row11ProductionReadinessVerifier/1.0",
            "Accept": "application/json,text/html,*/*",
        },
        method=check["method"],
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
        return {
            "url": url,
            "path": check["path"],
            "status": "ERROR",
            "error": str(exc),
            "status_ok": False,
            "forbidden_hits": [],
        }

    route_markers = marker_hits(check["path"], body)

    return {
        "url": url,
        "path": check["path"],
        "method": check["method"],
        "status": status,
        "expected_status": check["expected"],
        "status_ok": status in check["expected"],
        "content_type": headers.get("Content-Type") or headers.get("content-type", ""),
        "server": headers.get("Server") or headers.get("server", ""),
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
        "vercel_id": headers.get("X-Vercel-Id") or headers.get("x-vercel-id", ""),
        "body_sample": body[:900],
        "forbidden_hits": forbidden_hits(body),
        "route_markers": route_markers,
        "route_markers_ok": all(route_markers.values()) if route_markers else True,
    }

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]
marker_failures = [r for r in results if not r.get("route_markers_ok", True)]

frontend_results = [r for r in results if r["url"].startswith(FRONTEND)]
backend_results = [r for r in results if r["url"].startswith(BACKEND)]

deployment_checks = {
    "frontend_served_by_vercel": all("Vercel" in str(r.get("server", "")) for r in frontend_results),
    "backend_health_ok": any(r["path"] == "/health" and r["status"] == 200 for r in backend_results),
    "admin_runtime_protected": any(r["path"] == "/api/admin-runtime" and r["status"] in [401, 403, 405] for r in results),
    "admin_provider_summary_protected": any(r["path"] == "/api/admin-provider-execution/summary" and r["status"] in [401, 403, 405] for r in results),
    "client_lock_markers_live": any(r["path"] == "/client" and r.get("route_markers_ok") for r in results),
}

summary = {
    "frontend_base_url": FRONTEND,
    "backend_base_url": BACKEND,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "marker_failures": marker_failures,
    "deployment_checks": deployment_checks,
    "deployment_failures": [key for key, value in deployment_checks.items() if not value],
    "row11_live_deployment_ready": not failed_status and not forbidden and not marker_failures and all(deployment_checks.values()),
}

print(json.dumps(summary, indent=2))

if not summary["row11_live_deployment_ready"]:
    print("ROW11_LIVE_DEPLOYMENT_PRODUCTION_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW11_LIVE_DEPLOYMENT_PRODUCTION_VERIFY_PASSED")