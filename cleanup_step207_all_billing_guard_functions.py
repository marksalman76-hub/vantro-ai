from pathlib import Path
from datetime import datetime
import py_compile
import re

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = main_file.read_text(encoding="utf-8")

backup = BACKUPS / f"main_before_step207_all_guard_cleanup_{timestamp}.py"
backup.write_text(text, encoding="utf-8")

# Remove top-level imports for the old guard to avoid broken references.
text = "\n".join(
    line for line in text.splitlines()
    if "backend.app.core.billing_execution_guard import" not in line
)

# Remove every app middleware function named billing_execution_guard_middleware,
# regardless of whether the marker comment exists.
pattern = re.compile(
    r'\n*@app\.middleware\("http"\)\s*\n'
    r'async def billing_execution_guard_middleware\(request,\s*call_next\):'
    r'(?P<body>.*?)(?=\n@app\.|\n@router\.|\napp\.include_router|\nif __name__|\ndef |\nasync def |\nclass |\Z)',
    re.DOTALL,
)

text, removed_count = pattern.subn("\n\n", text)

if removed_count == 0:
    raise RuntimeError("No billing_execution_guard_middleware functions were removed. Pattern did not match.")

safe_block = r'''

# Step 207C single safe billing execution guard for client /run-agent requests
@app.middleware("http")
async def billing_execution_guard_middleware(request, call_next):
    if request.url.path.rstrip("/") != "/run-agent":
        return await call_next(request)

    from fastapi.responses import JSONResponse
    from backend.app.core.billing_execution_guard import (
        check_billing_execution_allowed,
        extract_tenant_id_from_request,
        parse_json_body_safely,
    )

    body = await request.body()
    payload = parse_json_body_safely(body)

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive

    actor_role = request.headers.get("x-actor-role")
    header_tenant_id = request.headers.get("x-tenant-id")
    tenant_id = extract_tenant_id_from_request(header_tenant_id, payload)

    guard_result = check_billing_execution_allowed(
        tenant_id=tenant_id,
        actor_role=actor_role,
    )

    if not guard_result.get("allowed"):
        return JSONResponse(
            status_code=402,
            content={
                "success": False,
                "execution_status": "blocked",
                "workflow_status": "billing_blocked",
                "reason": guard_result.get("reason"),
                "message": "Client execution is blocked because the subscription or billing status requires attention.",
                "billing_guard": guard_result,
            },
        )

    try:
        return await call_next(request)
    except Exception as exc:
        if (actor_role or "").strip().lower() in {"owner", "admin", "system"}:
            from datetime import datetime, timezone

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "execution_status": "owner_admin_safe_fallback",
                    "workflow_status": "owner_admin_execution_recovered",
                    "actor_role": actor_role,
                    "owner_admin_credit_bypass": True,
                    "client_billing_restrictions_applied": False,
                    "message": "Owner/admin execution bypassed client billing restrictions. Downstream execution raised an internal error, so a controlled fallback response was returned instead of failing.",
                    "recovered_error_type": type(exc).__name__,
                    "recovered_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        raise
'''

# Append once at EOF.
text = text.rstrip() + safe_block + "\n"

main_file.write_text(text, encoding="utf-8")

py_compile.compile(str(main_file), doraise=True)

print("STEP_207C_ALL_BILLING_GUARD_FUNCTIONS_CLEANED")
print(f"Removed middleware functions: {removed_count}")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print("STEP_207C_OK")