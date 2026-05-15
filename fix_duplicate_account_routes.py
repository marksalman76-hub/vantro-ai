from pathlib import Path

MAIN = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform\backend\app\main.py")
text = MAIN.read_text(encoding="utf-8")

marker = "# Step 157 tenant-aware client account routes"

if marker not in text:
    raise SystemExit("Marker not found. Stop and send current main.py tail.")

prefix = text.split(marker)[0].rstrip()

clean_routes = r'''

# Durable Postgres account routes
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


@app.post("/admin/client-credits/assign")
async def durable_assign_client_credits(payload: dict):
    return pg_assign_client_credits(payload)


@app.get("/admin/database-readiness")
async def durable_database_readiness():
    return pg_database_readiness()


@app.get("/admin/client-account/lookup")
async def durable_lookup_client_account(identifier: str):
    return pg_lookup_client_account(identifier)
'''

MAIN.write_text(prefix + clean_routes + "\n", encoding="utf-8")
print("DUPLICATE_ACCOUNT_ROUTES_CLEANED")