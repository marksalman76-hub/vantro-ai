from pathlib import Path
from datetime import datetime
import py_compile
import shutil

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"
guard_file = CORE / "billing_execution_guard.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)
CORE.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

broken_backup = BACKUPS / f"main_broken_before_step206_recovery_v3_{timestamp}.py"
broken_backup.write_text(main_file.read_text(encoding="utf-8"), encoding="utf-8")

candidate_backups = sorted(
    [
        p for p in BACKUPS.glob("main_before_step206*.py")
        if "recovery" not in p.name.lower()
    ],
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

if not candidate_backups:
    raise RuntimeError("No pre-Step-206 main backup found. Need to inspect backups folder.")

restored = None
errors = []

for candidate in candidate_backups:
    temp_file = BACKUPS / f"_compile_test_{candidate.name}"
    temp_file.write_text(candidate.read_text(encoding="utf-8"), encoding="utf-8")

    try:
        py_compile.compile(str(temp_file), doraise=True)
        restored = candidate
        temp_file.unlink(missing_ok=True)
        break
    except Exception as exc:
        errors.append(f"{candidate.name}: {type(exc).__name__}: {exc}")
        temp_file.unlink(missing_ok=True)

if restored is None:
    raise RuntimeError("No compile-passing pre-Step-206 main backup found:\n" + "\n".join(errors))

shutil.copyfile(restored, main_file)

guard_file.write_text(r'''
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from backend.app.core.durable_billing_state_store import get_billing_runtime_state


OWNER_ADMIN_ROLES = {"owner", "admin", "system"}


def _normalise_role(actor_role: Optional[str]) -> str:
    return (actor_role or "").strip().lower()


def owner_admin_bypasses_client_billing(actor_role: Optional[str]) -> bool:
    return _normalise_role(actor_role) in OWNER_ADMIN_ROLES


def extract_tenant_id_from_request(
    header_tenant_id: Optional[str],
    payload: Optional[Dict[str, Any]],
) -> Optional[str]:
    if header_tenant_id:
        return header_tenant_id

    if not isinstance(payload, dict):
        return None

    for key in ("tenant_id", "client_id", "workspace_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    nested = payload.get("payload")
    if isinstance(nested, dict):
        for key in ("tenant_id", "client_id", "workspace_id"):
            value = nested.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def check_billing_execution_allowed(
    tenant_id: Optional[str],
    actor_role: Optional[str],
) -> Dict[str, Any]:
    if owner_admin_bypasses_client_billing(actor_role):
        return {
            "allowed": True,
            "reason": "owner_admin_billing_bypass",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "owner_admin_access_unaffected": True,
        }

    if not tenant_id:
        return {
            "allowed": False,
            "reason": "tenant_id_required_for_client_execution",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
        }

    state_result = get_billing_runtime_state(tenant_id=tenant_id)
    state = state_result.get("state")

    if not state:
        return {
            "allowed": True,
            "reason": "no_durable_billing_block_found",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
        }

    subscription_status = state.get("subscription_status")
    client_execution_allowed = state.get("client_execution_allowed")
    credit_state = state.get("credit_state")
    execution_block_reason = state.get("execution_block_reason")

    if (
        client_execution_allowed is False
        or subscription_status in {"past_due", "cancelled", "canceled", "unpaid"}
        or credit_state == "blocked"
    ):
        return {
            "allowed": False,
            "reason": execution_block_reason or subscription_status or "billing_execution_blocked",
            "tenant_id": tenant_id,
            "actor_role": actor_role,
            "billing_guard_applied": True,
            "subscription_status": subscription_status,
            "credit_state": credit_state,
            "client_execution_allowed": client_execution_allowed,
            "state": state,
        }

    return {
        "allowed": True,
        "reason": "billing_state_allows_execution",
        "tenant_id": tenant_id,
        "actor_role": actor_role,
        "billing_guard_applied": True,
        "subscription_status": subscription_status,
        "credit_state": credit_state,
        "client_execution_allowed": client_execution_allowed,
    }


def parse_json_body_safely(body: bytes) -> Dict[str, Any]:
    if not body:
        return {}

    try:
        parsed = json.loads(body.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
'''.lstrip(), encoding="utf-8")

main_text = main_file.read_text(encoding="utf-8")

# Remove any leftover bad Step 206 snippets from restored file just in case.
main_text = "\n".join(
    line for line in main_text.splitlines()
    if "backend.app.core.billing_execution_guard import" not in line
)

if "billing_execution_guard_middleware" in main_text:
    raise RuntimeError("Restored main still contains Step 206 middleware. Refusing unsafe recovery.")

import_line = (
    "from backend.app.core.billing_execution_guard import "
    "check_billing_execution_allowed, extract_tenant_id_from_request, parse_json_body_safely"
)

# Safe top-level import after future/import block.
lines = main_text.splitlines()
insert_at = 0

for i, line in enumerate(lines):
    if line.startswith("from __future__ import"):
        insert_at = i + 1

if insert_at == 0:
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1

lines.insert(insert_at, import_line)
main_text = "\n".join(lines)

middleware_block = r'''

# Step 206 billing execution guard for client /run-agent requests
@app.middleware("http")
async def billing_execution_guard_middleware(request, call_next):
    if request.url.path.rstrip("/") != "/run-agent":
        return await call_next(request)

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
        from fastapi.responses import JSONResponse

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

    return await call_next(request)
'''

# Append at EOF so it cannot land inside FastAPI(...) or any route definition.
main_text = main_text.rstrip() + middleware_block + "\n"

main_file.write_text(main_text, encoding="utf-8")

py_compile.compile(str(guard_file), doraise=True)
py_compile.compile(str(main_file), doraise=True)

print("STEP_206_RECOVERY_V3_OK")
print(f"Broken backup saved: {broken_backup}")
print(f"Restored clean main from: {restored}")
print(f"Updated guard: {guard_file}")
print(f"Updated main: {main_file}")