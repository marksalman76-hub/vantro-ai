import os
import json
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path.cwd()

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL") or os.getenv("NEXT_PUBLIC_BACKEND_URL") or "https://api.trance-formation.com.au"
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL") or "https://trance-formation.com.au"

env_file = ROOT / ".env.local"
admin_token = os.getenv("ADMIN_PLATFORM_TOKEN", "").strip()

if env_file.exists() and not admin_token:
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("ADMIN_PLATFORM_TOKEN="):
            admin_token = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not admin_token:
    print("LIVE_PROVIDER_EXECUTION_RUNTIME_FINAL_VERIFY_FAILED")
    print("Reason: ADMIN_PLATFORM_TOKEN not found in environment or .env.local")
    raise SystemExit(1)

def request_json(url, method="GET", token=None, body=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "provider-execution-final-live-verify/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(url, data=payload, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(text)
            except Exception:
                data = {"raw": text[:500]}
            return response.status, data
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(text)
        except Exception:
            data = {"raw": text[:500]}
        return exc.code, data
    except Exception as exc:
        return 0, {"error": str(exc)}

def request_text(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "provider-execution-final-live-verify/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return 0, str(exc)

backend_routes = [
    "/provider-job-persistence/status",
    "/async-provider-worker/status",
    "/provider-retry-timeout/status",
    "/provider-asset-delivery/status",
    "/provider-execution-admin-visibility/status",
    "/provider-execution-admin-visibility/summary",
]

action_routes = [
    ("retry", "/provider-execution-admin-visibility/actions/retry"),
    ("requeue", "/provider-execution-admin-visibility/actions/requeue"),
    ("cancel", "/provider-execution-admin-visibility/actions/cancel"),
]

frontend_routes = [
    "/admin/provider-execution",
    "/api/admin-provider-execution/status",
    "/api/admin-provider-execution/summary",
    "/api/admin-provider-execution/retry",
    "/api/admin-provider-execution/requeue",
    "/api/admin-provider-execution/cancel",
]

results = {
    "backend_protected_routes": {},
    "backend_authorised_routes": {},
    "backend_action_routes": {},
    "frontend_routes": {},
    "credential_values_exposed": False,
}

failures = []

for route in backend_routes:
    url = BACKEND_BASE_URL.rstrip("/") + route

    public_status, public_data = request_json(url)
    results["backend_protected_routes"][route] = {
        "status": public_status,
        "blocked": public_status in (401, 403),
    }
    if public_status not in (401, 403):
        failures.append(f"Backend route should block unauthorised access: {route} returned {public_status}")

    auth_status, auth_data = request_json(url, token=admin_token)
    results["backend_authorised_routes"][route] = {
        "status": auth_status,
        "ready": auth_data.get("ready"),
        "credential_values_exposed": auth_data.get("credential_values_exposed", False),
    }
    if auth_status != 200:
        failures.append(f"Backend authorised route failed: {route} returned {auth_status}")
    if auth_data.get("credential_values_exposed") is True:
        failures.append(f"Credential exposure true on backend route: {route}")
        results["credential_values_exposed"] = True

for action, route in action_routes:
    url = BACKEND_BASE_URL.rstrip("/") + route

    public_status, public_data = request_json(url, method="POST", body={"job_id": "live_verify_job_001"})
    authorised_status, authorised_data = request_json(
        url,
        method="POST",
        token=admin_token,
        body={"job_id": "live_verify_job_001", "reason": "Final provider execution runtime live verification."},
    )

    results["backend_action_routes"][action] = {
        "public_status": public_status,
        "public_blocked": public_status in (401, 403),
        "authorised_status": authorised_status,
        "accepted": authorised_data.get("accepted"),
        "governed": authorised_data.get("governed"),
        "credential_values_exposed": authorised_data.get("credential_values_exposed", False),
    }

    if public_status not in (401, 403):
        failures.append(f"Action route should block unauthorised access: {route} returned {public_status}")
    if authorised_status != 200:
        failures.append(f"Authorised action route failed: {route} returned {authorised_status}")
    if authorised_data.get("accepted") is not True or authorised_data.get("governed") is not True:
        failures.append(f"Authorised action route did not return governed acceptance: {route}")
    if authorised_data.get("credential_values_exposed") is True:
        failures.append(f"Credential exposure true on action route: {route}")
        results["credential_values_exposed"] = True

for route in frontend_routes:
    url = FRONTEND_BASE_URL.rstrip("/") + route
    status, text = request_text(url)
    lower = text.lower()

    results["frontend_routes"][route] = {
        "status": status,
        "reachable_or_protected": status in (200, 401, 403, 405),
        "contains_provider_execution_marker": "provider execution" in lower or "provider" in lower,
        "secret_marker_detected": any(marker in text for marker in ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY"]),
    }

    if status not in (200, 401, 403, 405):
        failures.append(f"Frontend route unexpected status: {route} returned {status}")
    if results["frontend_routes"][route]["secret_marker_detected"]:
        failures.append(f"Secret marker detected in frontend route output: {route}")
        results["credential_values_exposed"] = True

print(json.dumps(results, indent=2))

if failures:
    print("LIVE_PROVIDER_EXECUTION_RUNTIME_FINAL_VERIFY_FAILED")
    for failure in failures:
        print("-", failure)
    raise SystemExit(1)

print("LIVE_PROVIDER_EXECUTION_RUNTIME_FINAL_VERIFY_PASSED")
print("provider_execution_runtime_live_verified", True)
print("backend_routes_auth_protected", True)
print("governed_actions_live_verified", True)
print("frontend_provider_dashboard_live_verified", True)
print("credential_values_exposed", False)