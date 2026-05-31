import json
import os
import re
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"base": BACKEND, "path": "/health", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/api/run-agent", "method": "GET", "expected": [400, 401, 403, 405]},
    {"base": FRONTEND, "path": "/api/admin-global-provider-readiness", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/admin-provider-execution/status", "method": "GET", "expected": [200, 401, 403, 405]},
    {"base": FRONTEND, "path": "/api/admin-provider-execution/summary", "method": "GET", "expected": [401, 403, 405]},
    {"base": FRONTEND, "path": "/api/client-latest-deliverable", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/client-execution-matrix", "method": "GET", "expected": [200, 401, 403]},
]

FORBIDDEN_LITERAL = [
    "OPENAI_API_KEY",
    "sk_live_",
    "sk_test_",
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
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
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

PROVIDER_SIGNALS = [
    "openai",
    "provider",
    "execution",
    "quality",
    "ready",
    "gated",
    "approval",
    "owner",
    "credential_values_exposed",
    "customer_safe",
    "status",
]

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

def signal_hits(body):
    lower = body.lower()
    return sorted(set(signal for signal in PROVIDER_SIGNALS if signal in lower))

def fetch(check):
    url = check["base"] + check["path"] + "?row13=provider-openai-verification"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row13RealProviderOpenAIVerifier/1.0",
            "Accept": "application/json,text/html,*/*",
        },
        method=check["method"],
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
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
            "provider_signals": [],
        }

    return {
        "url": url,
        "path": check["path"],
        "method": check["method"],
        "status": status,
        "expected_status": check["expected"],
        "status_ok": status in check["expected"],
        "content_type": headers.get("Content-Type") or headers.get("content-type", ""),
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
        "body_sample": body[:1200],
        "forbidden_hits": forbidden_hits(body),
        "provider_signals": signal_hits(body),
    }

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]

provider_readiness = next((r for r in results if r["path"] == "/api/admin-global-provider-readiness"), {})
run_agent = next((r for r in results if r["path"] == "/api/run-agent"), {})
summary_route = next((r for r in results if r["path"] == "/api/admin-provider-execution/summary"), {})

provider_checks = {
    "backend_health_ok": any(r["path"] == "/health" and r["status"] == 200 for r in results),
    "run_agent_get_protected": run_agent.get("status") in [400, 401, 403, 405],
    "provider_readiness_surface_reachable_or_protected": provider_readiness.get("status") in [200, 401, 403],
    "admin_provider_summary_protected": summary_route.get("status") in [401, 403, 405],
    "no_provider_secret_exposure": not forbidden,
}

summary = {
    "frontend_base_url": FRONTEND,
    "backend_base_url": BACKEND,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "provider_checks": provider_checks,
    "provider_failures": [key for key, value in provider_checks.items() if not value],
    "row13_real_provider_openai_ready": not failed_status and not forbidden and all(provider_checks.values()),
}

print(json.dumps(summary, indent=2))

if not summary["row13_real_provider_openai_ready"]:
    print("ROW13_REAL_PROVIDER_OPENAI_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW13_REAL_PROVIDER_OPENAI_VERIFY_PASSED")