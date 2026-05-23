from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step245_customer_onboarding_smoke_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = BACKUPS / f"test_step245_before_step245b_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

TEST.write_text(r'''
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


def get_json(path):
    req = urllib.request.Request(
        BASE + path,
        headers={
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
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
    "email": "step245-smoke@example.com",
    "package": "Growth",
    "active_agents": [
        "product_copywriting_agent",
        "ugc_creative_agent",
        "analytics_optimisation_agent",
    ],
}

invite_status, invite = post_json(
    "/admin/client-activation-invite",
    invite_payload,
)

activation_token = (
    invite.get("activation_token")
    or invite.get("token")
)

tenant_id = invite.get("tenant_id")

activate_payload = {
    "token": activation_token,
    "password": "Step245StrongPassword!245",
    "confirm_password": "Step245StrongPassword!245",
}

activation_status, activation = post_json(
    "/client/activate-account",
    activate_payload,
)

login_payload = {
    "email": "step245-smoke@example.com",
    "password": "Step245StrongPassword!245",
}

login_status, login = post_json(
    "/client/login",
    login_payload,
)

session_token = (
    login.get("session_token")
    or login.get("token")
)

me_status, me = (
    get_json(f"/client/me?session_token={session_token}")
    if session_token
    else (0, {})
)

combined = json.dumps({
    "invite": invite,
    "activation": activation,
    "login": login,
    "me": me,
}).lower()

account = me.get("account") or {}
active_agents = account.get("active_agents") or []

checks = {
    "invite_success": invite_status in {200, 201} and invite.get("success") is True,
    "activation_token_present": bool(activation_token),
    "tenant_created": bool(tenant_id),
    "activation_success": activation_status in {200, 201} and activation.get("success") is True,
    "login_success": login_status == 200 and login.get("success") is True,
    "session_token_present": bool(session_token),
    "client_me_success": me_status == 200 and me.get("success") is True,
    "active_agents_present": isinstance(active_agents, list) and len(active_agents) >= 1,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
    ]),
}

print("STEP_245B_CUSTOMER_ONBOARDING_SMOKE_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("invite_status", invite_status)
print("activation_status", activation_status)
print("login_status", login_status)
print("me_status", me_status)
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

print("STEP_245B_CUSTOMER_ONBOARDING_SMOKE_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_245B_CORRECT_ONBOARDING_SMOKE_TEST_OK")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")