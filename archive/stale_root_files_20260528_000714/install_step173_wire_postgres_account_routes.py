from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

postgres_import = """
# Step 173 durable Postgres account runtime
from backend.app.core.postgres_account_runtime import (
    activate_account as pg_activate_account,
    create_activation_invite as pg_create_activation_invite,
    get_activation_invite as pg_get_activation_invite,
    get_session_account as pg_get_session_account,
    login as pg_login,
    recent_security_events as pg_recent_security_events,
)
"""

if "postgres_account_runtime" not in text:
    text = postgres_import + "\n" + text

routes_block = r'''

# Step 173 durable Postgres account routes
@app.post("/admin/client-activation-invite")
async def durable_create_client_activation_invite(payload: dict):
    return pg_create_activation_invite(payload)


@app.get("/client/activation-invite-status")
async def durable_get_invite_status(token: str):
    invite = pg_get_activation_invite(token)

    if not invite:
        return {"success": False, "error": "invite_not_found"}

    from datetime import datetime, timezone

    expired = invite["expires_at"] < datetime.now(timezone.utc)

    return {
        "success": True,
        "tenant_id": invite["tenant_id"],
        "email": invite["email"],
        "company_name": invite["company_name"],
        "package": invite["package"],
        "active_agents": invite["active_agents"],
        "status": "used" if invite["used"] else "pending",
        "expired": expired,
        "used": invite["used"],
    }


@app.post("/client/activate-account")
async def durable_activate_client_account(payload: dict):
    token = str(payload.get("token") or "")
    password = str(payload.get("password") or "")
    confirm_password = str(payload.get("confirm_password") or "")

    if len(password) < 10:
        return {"success": False, "error": "password_minimum_10_characters"}

    if password != confirm_password:
        return {"success": False, "error": "passwords_do_not_match"}

    return pg_activate_account(token, password)


@app.post("/client/login")
async def durable_login_client_account(payload: dict):
    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")
    return pg_login(email, password)


@app.get("/client/me")
async def durable_client_me(session_token: str):
    return pg_get_session_account(session_token)


@app.get("/admin/client-account-security-events")
async def durable_client_account_security_events(limit: int = 25):
    return pg_recent_security_events(limit)
'''

route_marker = "# Step 173 durable Postgres account routes"

if route_marker not in text:
    text = text.rstrip() + "\n" + routes_block + "\n"

MAIN.write_text(text, encoding="utf-8")

print("STEP_173_POSTGRES_ROUTES_WIRED")
print("main_file", MAIN)
print("STEP_173_OK")