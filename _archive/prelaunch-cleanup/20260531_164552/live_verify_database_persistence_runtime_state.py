import json
import os
import re
import urllib.request
import urllib.error

FRONTEND = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")
BACKEND = os.environ.get("BACKEND_BASE_URL", "https://api.trance-formation.com.au").rstrip("/")

CHECKS = [
    {"base": BACKEND, "path": "/health", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/api/client-integrations", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/client-execution-matrix", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/client-latest-deliverable", "method": "GET", "expected": [200, 401, 403]},
    {"base": FRONTEND, "path": "/api/signup-locked-activation/status", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/api/signup-agent-selection/options/starter", "method": "GET", "expected": [200]},
    {"base": FRONTEND, "path": "/api/billing-checkout", "method": "GET", "expected": [400, 401, 403, 405]},
    {"base": FRONTEND, "path": "/api/admin-runtime", "method": "GET", "expected": [401, 403, 405]},
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
    "password hash",
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

PERSISTENCE_SIGNALS = [
    "postgres",
    "database",
    "storage_mode",
    "execution",
    "events",
    "activation",
    "billing",
    "credential_values_exposed",
    "customer_safe",
    "status",
    "ready",
    "persist",
    "state",
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
    return sorted(set(signal for signal in PERSISTENCE_SIGNALS if signal in lower))

def fetch(check):
    url = check["base"] + check["path"]
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row10DatabasePersistenceVerifier/1.0",
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
            "persistence_signals": [],
        }

    parsed_json = None
    json_ok = False
    if "application/json" in (headers.get("Content-Type") or headers.get("content-type", "")).lower():
        try:
            parsed_json = json.loads(body)
            json_ok = True
        except Exception:
            pass

    result = {
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
        "json_ok": json_ok,
        "forbidden_hits": forbidden_hits(body),
        "persistence_signals": signal_hits(body),
    }

    if parsed_json is not None:
        result["json_keys"] = sorted(parsed_json.keys()) if isinstance(parsed_json, dict) else []
        if isinstance(parsed_json, dict):
            result["storage_mode"] = parsed_json.get("storage_mode")
            result["credential_values_exposed"] = parsed_json.get("credential_values_exposed")
            result["customer_safe"] = parsed_json.get("customer_safe")

    return result

results = [fetch(check) for check in CHECKS]

failed_status = [r for r in results if not r.get("status_ok")]
forbidden = [{"path": r["path"], "hits": r["forbidden_hits"]} for r in results if r.get("forbidden_hits")]

integration_result = next((r for r in results if r["path"] == "/api/client-integrations"), {})
execution_matrix_result = next((r for r in results if r["path"] == "/api/client-execution-matrix"), {})
latest_deliverable_result = next((r for r in results if r["path"] == "/api/client-latest-deliverable"), {})
activation_result = next((r for r in results if r["path"] == "/api/signup-locked-activation/status"), {})

persistence_checks = {
    "integration_storage_postgres": integration_result.get("storage_mode") == "postgres",
    "execution_matrix_has_events": "events" in str(execution_matrix_result.get("body_sample", "")).lower(),
    "latest_deliverable_has_execution": "execution" in str(latest_deliverable_result.get("body_sample", "")).lower(),
    "activation_lock_state_ready": "one_time_activation_lock_enabled" in str(activation_result.get("body_sample", "")),
}

summary = {
    "frontend_base_url": FRONTEND,
    "backend_base_url": BACKEND,
    "results": results,
    "failed_status": failed_status,
    "forbidden_hits": forbidden,
    "persistence_checks": persistence_checks,
    "persistence_failures": [key for key, value in persistence_checks.items() if not value],
    "row10_database_persistence_ready": not failed_status and not forbidden and all(persistence_checks.values()),
}

print(json.dumps(summary, indent=2))

if not summary["row10_database_persistence_ready"]:
    print("ROW10_DATABASE_PERSISTENCE_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW10_DATABASE_PERSISTENCE_VERIFY_PASSED")