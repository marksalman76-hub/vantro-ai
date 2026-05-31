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
    "NEXT_PUBLIC_ADMIN_PLATFORM_TOKEN",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "XAI_API_KEY",
    "sk_live_",
    "sk_test_",
    "whsec_",
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
    "secret",
    "password hash",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bwhsec_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b"),
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
]

SAFE_EXCEPTIONS = [
    "client_demo_001",
    "credential_hint",
    "credential_values_exposed",
    "secret protection",
    "secret_protection",
    "customer_safe",
    "request_details_protected",
    "system_details_protected",
]

SECURITY_SIGNALS = [
    "customer_safe",
    "credential_values_exposed",
    "request_details_protected",
    "system_details_protected",
    "owner",
    "approval",
    "protected",
    "secure",
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
    return sorted(set(signal for signal in SECURITY_SIGNALS if signal in lower))

def fetch(check):
    url = check["base"] + check["path"]
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row9SecurityGovernanceVerifier/1.0",
            "Accept": "text/html,application/json,*/*",
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
            "security_signals": [],
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
        "body_sample": body[:1000],
        "forbidden_hits": forbidden_hits(body),
        "security_signals": signal_hits(body),
    }

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]

summary = {
    "frontend_base_url": FRONTEND,
    "backend_base_url": BACKEND,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "row9_security_governance_ready": not failed_status and not forbidden,
}

print(json.dumps(summary, indent=2))

if not summary["row9_security_governance_ready"]:
    print("ROW9_SECURITY_GOVERNANCE_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW9_SECURITY_GOVERNANCE_VERIFY_PASSED")