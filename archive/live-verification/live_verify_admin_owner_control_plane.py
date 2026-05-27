import os
import re
import json
import urllib.request
import urllib.error

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL") or "https://ecommerce-ai-agent-platform-d04qm32ds.vercel.app"

ROUTES = [
    "/admin",
    "/admin/provider-execution",
    "/api/admin-provider-execution/status",
    "/api/admin-provider-execution/summary",
]

REQUIRED_MARKERS = {
    "/admin": [
        "Admin Command Centre",
        "Owner Control Plane",
        "Provider Execution",
        "Readiness Panel",
        "Owner Governance Rules",
        "Credential exposure",
        "FALSE",
    ],
    "/admin/provider-execution": [
        "Provider Execution Dashboard",
        "Provider Job Detail",
        "Execution Timeline",
        "Governed Actions",
    ],
}

SECRET_PATTERNS = {
    "openai_secret_key": r"sk-[A-Za-z0-9_\-]{20,}",
    "anthropic_key": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "stripe_secret_key": r"sk_live_[A-Za-z0-9]{20,}|sk_test_[A-Za-z0-9]{20,}",
    "jwt_like_token": r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}",
    "admin_owner_token": r"\btf_own_[A-Za-z0-9_\-]{20,}\b",
}

FORBIDDEN_ENV_NAMES = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "ADMIN_PLATFORM_TOKEN",
    "ADMIN_AUTH_SECRET",
    "JWT_SECRET",
]

def fetch_text(route):
    url = FRONTEND_BASE_URL.rstrip("/") + route
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "live-admin-owner-control-plane-verify/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, str(exc)

results = {}
failures = []
confirmed_exposures = []

for route in ROUTES:
    status, text = fetch_text(route)
    route_result = {
        "status": status,
        "bytes": len(text),
        "required_markers_present": {},
        "secret_hits": [],
        "env_name_hits": [],
    }

    if status not in (200, 401, 403, 405):
        failures.append(f"{route} returned unexpected status {status}")

    for marker in REQUIRED_MARKERS.get(route, []):
        present = marker in text
        route_result["required_markers_present"][marker] = present
        if not present:
            failures.append(f"{route} missing marker: {marker}")

    for name, pattern in SECRET_PATTERNS.items():
        for match in re.finditer(pattern, text):
            hit = {
                "pattern": name,
                "preview": match.group(0)[:8] + "..." + match.group(0)[-6:],
            }
            route_result["secret_hits"].append(hit)
            confirmed_exposures.append({"route": route, **hit})

    for env_name in FORBIDDEN_ENV_NAMES:
        if env_name in text:
            route_result["env_name_hits"].append(env_name)
            confirmed_exposures.append({
                "route": route,
                "pattern": "env_name",
                "preview": env_name,
            })

    results[route] = route_result

print(json.dumps({
    "frontend_base_url": FRONTEND_BASE_URL,
    "results": results,
    "credential_values_exposed": bool(confirmed_exposures),
    "confirmed_exposures": confirmed_exposures,
}, indent=2))

if confirmed_exposures:
    print("LIVE_ADMIN_OWNER_CONTROL_PLANE_VERIFY_FAILED")
    print("credential_values_exposed", True)
    raise SystemExit(1)

if failures:
    print("LIVE_ADMIN_OWNER_CONTROL_PLANE_VERIFY_FAILED")
    for failure in failures:
        print("-", failure)
    raise SystemExit(1)

print("LIVE_ADMIN_OWNER_CONTROL_PLANE_VERIFY_PASSED")
print("admin_command_centre_live", True)
print("provider_execution_link_live", True)
print("readiness_panel_live", True)
print("credential_values_exposed", False)