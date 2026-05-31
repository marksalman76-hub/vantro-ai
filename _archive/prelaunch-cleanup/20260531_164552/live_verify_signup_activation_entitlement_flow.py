import json
import os
import re
import urllib.request
import urllib.error

BASE = os.environ.get("FRONTEND_BASE_URL", "https://app.trance-formation.com.au").rstrip("/")

CHECKS = [
    "/signup",
    "/activate",
    "/api/signup-agent-selection/options/starter",
    "/api/signup-agent-selection/options/growth",
    "/api/signup-agent-selection/options/business",
    "/api/signup-agent-selection/options/enterprise",
    "/api/signup-agent-selection/validate",
    "/api/signup-locked-activation/status",
]

FORBIDDEN_LITERAL = [
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "ADMIN_PLATFORM_TOKEN",
    "DATABASE_URL",
    "JWT_SECRET",
    "raw json",
    "debug",
    "traceback",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"\btenant_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bclient_[a-z0-9]{6,}\b", re.I),
    re.compile(r"\bsk_live_[a-z0-9_]{8,}\b", re.I),
    re.compile(r"\bsk_test_[a-z0-9_]{8,}\b", re.I),
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

    return hits

def fetch(path):
    url = BASE + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Row4SignupActivationVerifier/1.1",
            "Accept": "text/html,application/json,*/*",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8", errors="ignore")
            return {
                "path": path,
                "status": response.status,
                "content_type": response.headers.get("content-type", ""),
                "body_sample": body[:800],
                "forbidden_hits": forbidden_hits(body),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return {
            "path": path,
            "status": exc.code,
            "content_type": exc.headers.get("content-type", ""),
            "body_sample": body[:800],
            "forbidden_hits": forbidden_hits(body),
        }
    except Exception as exc:
        return {
            "path": path,
            "status": "ERROR",
            "error": str(exc),
            "forbidden_hits": [],
        }

results = [fetch(path) for path in CHECKS]

summary = {
    "frontend_base_url": BASE,
    "results": results,
    "failed": [
        r for r in results
        if r["status"] not in [200, 400, 401, 405]
    ],
    "forbidden_hits": [
        {"path": r["path"], "hits": r["forbidden_hits"]}
        for r in results
        if r.get("forbidden_hits")
    ],
}

print(json.dumps(summary, indent=2))

if summary["failed"] or summary["forbidden_hits"]:
    print("ROW4_SIGNUP_ACTIVATION_VERIFY_FAILED")
    raise SystemExit(1)

print("ROW4_SIGNUP_ACTIVATION_VERIFY_PASSED")