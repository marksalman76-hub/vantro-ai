import json
import os
import re
import urllib.request
import urllib.error

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"base": BASE, "path": "/api/run-agent", "method": "GET", "expected": [400, 401, 403, 405]},
    {"base": BASE, "path": "/api/client-latest-deliverable", "method": "GET", "expected": [200, 401, 403]},
    {"base": BASE, "path": "/api/client-review-action", "method": "GET", "expected": [400, 401, 403, 405]},
    {"base": BASE, "path": "/api/client-execution-matrix", "method": "GET", "expected": [200, 401, 403]},
    {"base": BACKEND, "path": "/health", "method": "GET", "expected": [200]},
]

FORBIDDEN_LITERAL = [
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
    "JWT_SECRET",
    "raw json",
    "traceback",
    "internal prompt",
    "system prompt",
    "developer message",
    "provider secret",
    "webhook secret",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bwhsec_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
]

QUALITY_SIGNALS = [
    "quality",
    "review",
    "approved",
    "rejected",
    "delivery",
    "execution",
    "status",
    "customer",
    "safe",
]

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

def signal_hits(body):
    lower = body.lower()
    return sorted(set(signal for signal in QUALITY_SIGNALS if signal in lower))

def fetch(check):
    url = check["base"] + check["path"]
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row6AgentExecutionQualityVerifier/1.0",
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
            "quality_signals": [],
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
        "quality_signals": signal_hits(body),
    }

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]

summary = {
    "frontend_base_url": BASE,
    "backend_base_url": BACKEND,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "row6_basic_quality_surface_ready": not failed_status and not forbidden,
}

print(json.dumps(summary, indent=2))

if not summary["row6_basic_quality_surface_ready"]:
    print("ROW6_AGENT_EXECUTION_QUALITY_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW6_AGENT_EXECUTION_QUALITY_VERIFY_PASSED")