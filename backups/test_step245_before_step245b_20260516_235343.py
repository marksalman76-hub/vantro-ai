import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://127.0.0.1:8000"
ROOT = Path.cwd()

record_path = ROOT / "backend" / "app" / "data" / "step245_customer_onboarding_smoke_lock.json"
record = json.loads(record_path.read_text(encoding="utf-8"))


def post_json(path, payload, headers=None):
    req_headers = {
        "Content-Type": "application/json",
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
    }

    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body}
        return exc.code, data


def get_json(path, headers=None):
    req_headers = {
        "x-actor-role": "owner",
        "x-tenant-id": "owner",
    }

    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(
        BASE + path,
        headers=req_headers,
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body}
        return exc.code, data


invite_payload = {
    "company_name": "Step 245 Smoke Test Store",
    "contact_name": "Step 245 Owner",
    "contact_email": "step245-smoke@example.com",
    "contact_phone": "0400000245",
    "selected_package": "Growth",
    "billing_cycle": "monthly",
    "paid_agents": [
        "product_copywriting_agent",
        "ugc_creative_agent",
        "analytics_optimisation_agent",
    ],
    "owner_admin_user_id": "owner_admin",
}

invite_status, invite = post_json("/admin/create-client-invite", invite_payload)

activation_token = (
    invite.get("activation_token")
    or invite.get("invite", {}).get("activation_token")
    or invite.get("token")
    or invite.get("invite_token")
)

tenant_id = (
    invite.get("tenant_id")
    or invite.get("client", {}).get("tenant_id")
    or invite.get("invite", {}).get("tenant_id")
)

activation_payload = {
    "activation_token": activation_token,
    "password": "Step245StrongPassword!245",
    "company_name": "Step 245 Smoke Test Store",
    "contact_name": "Step 245 Owner",
}

activation_status, activation = post_json("/client/complete-onboarding", activation_payload)

login_payload = {
    "email": "step245-smoke@example.com",
    "password": "Step245StrongPassword!245",
}

login_status, login = post_json("/client/login", login_payload)

session_token = (
    login.get("session_token")
    or login.get("session", {}).get("session_token")
    or login.get("token")
)

me_status, me = get_json(f"/client/me?session_token={session_token}") if session_token else (0, {})

combined = json.dumps({
    "record": record,
    "invite": invite,
    "activation": activation,
    "login": login,
    "me": me,
}).lower()

account = me.get("account") or {}
active_agents = account.get("active_agents") or []

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "customer_onboarding_smoke_requirements_locked",
    "invite_route_controlled": invite_status in {200, 201, 400, 409, 422},
    "invite_success": invite.get("success") is True,
    "activation_token_present": bool(activation_token),
    "tenant_created": bool(tenant_id),
    "activation_route_controlled": activation_status in {200, 201, 400, 409, 422},
    "activation_success": activation.get("success") is True,
    "login_route_controlled": login_status in {200, 201, 400, 401, 422},
    "login_success": login.get("success") is True,
    "session_token_present": bool(session_token),
    "client_me_success": me_status == 200 and me.get("success") is True,
    "active_agents_present": isinstance(active_agents, list) and len(active_agents) >= 1,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_245_CUSTOMER_ONBOARDING_SMOKE_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("invite_status", invite_status)
print("activation_status", activation_status)
print("login_status", login_status)
print("me_status", me_status)
print("tenant_created", bool(tenant_id))
print("active_agent_count", len(active_agents) if isinstance(active_agents, list) else 0)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "invite": invite,
        "activation": activation,
        "login": login,
        "me": me,
    }, indent=2))
    raise SystemExit(1)

print("STEP_245_CUSTOMER_ONBOARDING_SMOKE_LOCK_OK")
