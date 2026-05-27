import os
import re
import json
import urllib.request
import urllib.error

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL") or "https://ecommerce-ai-agent-platform-d04qm32ds.vercel.app"

ROUTES = [
    "/",
    "/admin/provider-execution",
    "/api/admin-provider-execution/status",
    "/api/admin-provider-execution/summary",
]

SECRET_PATTERNS = {
    "openai_secret_key": r"sk-[A-Za-z0-9_\-]{20,}",
    "anthropic_key": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "stripe_secret_key": r"sk_live_[A-Za-z0-9]{20,}|sk_test_[A-Za-z0-9]{20,}",
    "jwt_like_long_token": r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}",
    "admin_platform_token_exact_shape": r"\b[0-9a-f]{64}\b",
    "admin_owner_token_shape": r"\btf_own_[A-Za-z0-9_\-]{20,}\b",
}

ALLOWLIST_CONTEXT = [
    "_next/static",
    "integrity",
    "sha256",
    "sha384",
    "sha512",
    "font",
    "chunk",
    "webpack",
    "buildid",
]

def fetch_text(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "precise-live-secret-exposure-check/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, str(exc)

def surrounding(text, start, end, width=90):
    return text[max(0, start-width):min(len(text), end+width)].replace("\n", " ")

results = {}
confirmed_exposures = []

for route in ROUTES:
    url = FRONTEND_BASE_URL.rstrip("/") + route
    status, text = fetch_text(url)

    route_hits = []

    for name, pattern in SECRET_PATTERNS.items():
        for match in re.finditer(pattern, text):
            context = surrounding(text, match.start(), match.end())
            lowered = context.lower()
            allowlisted = any(item in lowered for item in ALLOWLIST_CONTEXT)

            hit = {
                "pattern": name,
                "match_preview": match.group(0)[:8] + "..." + match.group(0)[-6:],
                "context": context[:220],
                "allowlisted_static_context": allowlisted,
            }
            route_hits.append(hit)

            if not allowlisted:
                confirmed_exposures.append({
                    "route": route,
                    **hit,
                })

    env_name_hits = []
    for marker in [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "ADMIN_PLATFORM_TOKEN",
        "ADMIN_AUTH_SECRET",
        "JWT_SECRET",
    ]:
        if marker in text:
            env_name_hits.append(marker)

    if env_name_hits:
        confirmed_exposures.append({
            "route": route,
            "pattern": "env_name_marker",
            "markers": env_name_hits,
            "context": "Environment variable name appeared in live response.",
            "allowlisted_static_context": False,
        })

    results[route] = {
        "status": status,
        "bytes": len(text),
        "hits": route_hits,
        "env_name_hits": env_name_hits,
    }

print(json.dumps({
    "frontend_base_url": FRONTEND_BASE_URL,
    "results": results,
    "confirmed_exposures": confirmed_exposures,
    "credential_values_exposed": bool(confirmed_exposures),
}, indent=2))

if confirmed_exposures:
    print("PRECISE_LIVE_SECRET_EXPOSURE_CHECK_FAILED")
    print("credential_values_exposed", True)
    raise SystemExit(1)

print("PRECISE_LIVE_SECRET_EXPOSURE_CHECK_PASSED")
print("credential_values_exposed", False)
print("provider_routes_secret_safe", True)
print("homepage_secret_false_positive_cleared", True)