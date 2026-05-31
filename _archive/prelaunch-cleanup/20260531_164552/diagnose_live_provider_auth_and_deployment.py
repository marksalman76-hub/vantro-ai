import os
import json
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path.cwd()

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL") or os.getenv("NEXT_PUBLIC_BACKEND_URL") or "https://api.trance-formation.com.au"
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL") or "https://trance-formation.com.au"

ENV_FILE = ROOT / ".env.local"

def read_env_values():
    values = {}
    if ENV_FILE.exists():
        for raw in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    for key, value in os.environ.items():
        values.setdefault(key, value)
    return values

env = read_env_values()

candidate_tokens = {
    "ADMIN_PLATFORM_TOKEN": env.get("ADMIN_PLATFORM_TOKEN", ""),
    "ADMIN_TOKEN": env.get("ADMIN_TOKEN", ""),
    "OWNER_ADMIN_TOKEN": env.get("OWNER_ADMIN_TOKEN", ""),
    "ADMIN_AUTH_SECRET": env.get("ADMIN_AUTH_SECRET", ""),
    "JWT_SECRET": env.get("JWT_SECRET", ""),
}

candidate_tokens = {k: v for k, v in candidate_tokens.items() if v}

def safe_token_info(value):
    return {
        "present": bool(value),
        "length": len(value or ""),
        "prefix": (value[:6] + "...") if value else "",
        "suffix": ("..." + value[-6:]) if value else "",
    }

def request(url, method="GET", token=None, header_mode="authorization_bearer", body=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "live-provider-auth-diagnostic/1.0",
    }

    if token:
        if header_mode == "authorization_bearer":
            headers["Authorization"] = f"Bearer {token}"
        elif header_mode == "x_admin_token":
            headers["x-admin-token"] = token
        elif header_mode == "x_platform_token":
            headers["x-platform-token"] = token
        elif header_mode == "x_admin_auth":
            headers["x-admin-auth"] = token
        elif header_mode == "x_owner_token":
            headers["x-owner-token"] = token

    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            text = response.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(text)
            except Exception:
                data = {"raw": text[:800]}
            return response.status, data
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(text)
        except Exception:
            data = {"raw": text[:800]}
        return exc.code, data
    except Exception as exc:
        return 0, {"error": str(exc)}

def request_text(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "live-provider-auth-diagnostic/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, str(exc)

backend_test_routes = [
    "/health",
    "/provider-execution-admin-visibility/status",
    "/provider-execution-admin-visibility/summary",
    "/provider-execution-admin-visibility/actions/retry",
]

frontend_test_routes = [
    "/",
    "/admin/provider-execution",
    "/api/admin-provider-execution/status",
    "/api/admin-provider-execution/summary",
    "/api/admin-provider-execution/retry",
    "/api/admin-provider-execution/requeue",
    "/api/admin-provider-execution/cancel",
]

header_modes = [
    "authorization_bearer",
    "x_admin_token",
    "x_platform_token",
    "x_admin_auth",
    "x_owner_token",
]

diagnostic = {
    "backend_base_url": BACKEND_BASE_URL,
    "frontend_base_url": FRONTEND_BASE_URL,
    "local_token_inventory_safe": {k: safe_token_info(v) for k, v in candidate_tokens.items()},
    "backend_route_auth_matrix": {},
    "frontend_route_matrix": {},
    "commit_route_markers": {},
    "recommendations": [],
    "credential_values_exposed": False,
}

for route in backend_test_routes:
    method = "POST" if "/actions/" in route else "GET"
    body = {"job_id": "diagnostic_live_job_001", "reason": "Live auth diagnostic"} if method == "POST" else None
    url = BACKEND_BASE_URL.rstrip("/") + route

    diagnostic["backend_route_auth_matrix"][route] = {}

    public_status, public_data = request(url, method=method, body=body)
    diagnostic["backend_route_auth_matrix"][route]["public_no_token"] = {
        "status": public_status,
        "blocked": public_status in (401, 403),
        "sample_keys": list(public_data.keys())[:8] if isinstance(public_data, dict) else [],
    }

    for token_name, token_value in candidate_tokens.items():
        for mode in header_modes:
            status, data = request(url, method=method, token=token_value, header_mode=mode, body=body)
            accepted = status == 200
            credential_exposed = isinstance(data, dict) and data.get("credential_values_exposed") is True

            if credential_exposed:
                diagnostic["credential_values_exposed"] = True

            diagnostic["backend_route_auth_matrix"][route][f"{token_name}::{mode}"] = {
                "status": status,
                "accepted": accepted,
                "ready": data.get("ready") if isinstance(data, dict) else None,
                "governed": data.get("governed") if isinstance(data, dict) else None,
                "credential_values_exposed": credential_exposed,
            }

for route in frontend_test_routes:
    status, text = request_text(FRONTEND_BASE_URL.rstrip("/") + route)
    lower = text.lower()

    diagnostic["frontend_route_matrix"][route] = {
        "status": status,
        "contains_provider_execution": "provider execution" in lower,
        "contains_retry_route_marker": "retry" in lower and "requeue" in lower and "cancel" in lower,
        "secret_marker_detected": any(marker in text for marker in ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY"]),
        "sample": text[:180].replace("\n", " "),
    }

    if diagnostic["frontend_route_matrix"][route]["secret_marker_detected"]:
        diagnostic["credential_values_exposed"] = True

# Check local committed files for expected route existence.
expected_local_files = {
    "frontend_retry_route": ROOT / "frontend/src/app/api/admin-provider-execution/retry/route.ts",
    "frontend_requeue_route": ROOT / "frontend/src/app/api/admin-provider-execution/requeue/route.ts",
    "frontend_cancel_route": ROOT / "frontend/src/app/api/admin-provider-execution/cancel/route.ts",
    "frontend_status_route": ROOT / "frontend/src/app/api/admin-provider-execution/status/route.ts",
    "frontend_summary_route": ROOT / "frontend/src/app/api/admin-provider-execution/summary/route.ts",
    "provider_dashboard_page": ROOT / "frontend/src/app/admin/provider-execution/page.tsx",
}

for name, path in expected_local_files.items():
    diagnostic["commit_route_markers"][name] = {
        "exists_local": path.exists(),
        "contains_expected_marker": False,
    }
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        diagnostic["commit_route_markers"][name]["contains_expected_marker"] = (
            "provider-execution-admin-visibility" in text
            or "Provider Execution Dashboard" in text
            or "runGovernedAction" in text
        )

# Recommendations from observed evidence.
any_backend_success = False
for route, checks in diagnostic["backend_route_auth_matrix"].items():
    for key, value in checks.items():
        if key != "public_no_token" and value.get("accepted"):
            any_backend_success = True

frontend_api_404 = any(
    route.startswith("/api/admin-provider-execution") and result["status"] == 404
    for route, result in diagnostic["frontend_route_matrix"].items()
)

if not any_backend_success:
    diagnostic["recommendations"].append(
        "No tested local token/header combination authenticated against the live backend. This suggests the live backend guard is using a different credential source or a session/cookie/JWT flow, not necessarily that Render tokens are incorrect."
    )

if frontend_api_404:
    diagnostic["recommendations"].append(
        "Frontend API provider-execution routes are returning 404. This indicates the Vercel deployment serving the live domain has not picked up the latest routes, or the live domain is pointed at a different Vercel project/deployment."
    )

if diagnostic["frontend_route_matrix"].get("/admin/provider-execution", {}).get("status") == 200:
    diagnostic["recommendations"].append(
        "The provider execution page is live, but API route 404s mean the static page and route handlers may be coming from different deployments or the live domain is not on the expected newest build."
    )

if diagnostic["credential_values_exposed"]:
    diagnostic["recommendations"].append("Credential exposure marker detected. Stop before further deployment.")
else:
    diagnostic["recommendations"].append("Credential exposure remained false during diagnostic.")

print(json.dumps(diagnostic, indent=2))

print("LIVE_PROVIDER_AUTH_AND_DEPLOYMENT_DIAGNOSTIC_COMPLETE")
print("credential_values_exposed", diagnostic["credential_values_exposed"])
print("backend_any_tested_auth_success", any_backend_success)
print("frontend_api_404_detected", frontend_api_404)