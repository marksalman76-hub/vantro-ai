import json
import os
import re
import urllib.request
import urllib.error

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"path": "/client", "method": "GET", "expected": [200]},
    {"path": "/api/client-integrations", "method": "GET", "expected": [200, 401, 403]},
    {"path": "/api/client-integrations-connect", "method": "GET", "expected": [400, 401, 403, 405]},
    {"path": "/api/client-integrations-disconnect", "method": "GET", "expected": [400, 401, 403, 405]},
    {"path": "/api/client-integrations-test", "method": "GET", "expected": [400, 401, 403, 405]},
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
    "api_key",
    "private_key",
    "bearer ",
    "raw json",
    "traceback",
    "internal prompt",
    "system prompt",
    "developer message",
    "webhook secret",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bwhsec_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
]

REQUIRED_CLIENT_MARKERS = [
    "Integrations",
    "Billing",
    "Support",
]

INTEGRATION_SIGNALS = [
    "shopify",
    "stripe",
    "email",
    "crm",
    "analytics",
    "connect",
    "disconnect",
    "test",
    "status",
    "credential",
    "secure",
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

def marker_hits(body, markers):
    lower = body.lower()
    return {marker: marker.lower() in lower for marker in markers}

def signal_hits(body):
    lower = body.lower()
    return sorted(set(signal for signal in INTEGRATION_SIGNALS if signal in lower))

def fetch(check):
    url = BASE + check["path"]
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row8IntegrationsVerifier/1.0",
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
            "path": check["path"],
            "method": check["method"],
            "status": "ERROR",
            "error": str(exc),
            "status_ok": False,
            "forbidden_hits": [],
        }

    result = {
        "path": check["path"],
        "method": check["method"],
        "status": status,
        "expected_status": check["expected"],
        "status_ok": status in check["expected"],
        "content_type": headers.get("Content-Type") or headers.get("content-type", ""),
        "cache": headers.get("X-Vercel-Cache") or headers.get("x-vercel-cache", ""),
        "matched_path": headers.get("X-Matched-Path") or headers.get("x-matched-path", ""),
        "body_sample": body[:900],
        "forbidden_hits": forbidden_hits(body),
        "integration_signals": signal_hits(body),
    }

    if check["path"] == "/client":
        result["client_markers"] = marker_hits(body, REQUIRED_CLIENT_MARKERS)
        result["client_markers_ok"] = all(result["client_markers"].values())

    if check["path"] == "/api/client-integrations" and status == 200:
        try:
            data = json.loads(body)
            result["json_ok"] = True
            result["integration_status_fields"] = sorted(data.keys()) if isinstance(data, dict) else []
            if isinstance(data, dict):
                result["credential_values_exposed"] = data.get("credential_values_exposed")
                result["customer_safe"] = data.get("customer_safe")
        except Exception as exc:
            result["json_ok"] = False
            result["json_error"] = str(exc)

    return result

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]
client_marker_failures = [
    r for r in results
    if r["path"] == "/client" and not r.get("client_markers_ok")
]

summary = {
    "frontend_base_url": BASE,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "client_marker_failures": client_marker_failures,
    "row8_integrations_ready": not failed_status and not forbidden and not client_marker_failures,
}

print(json.dumps(summary, indent=2))

if not summary["row8_integrations_ready"]:
    print("ROW8_INTEGRATIONS_CLIENT_CONNECTIONS_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW8_INTEGRATIONS_CLIENT_CONNECTIONS_VERIFY_PASSED")