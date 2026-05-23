from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"
guard_file = CORE / "billing_execution_guard.py"

BACKUPS.mkdir(parents=True, exist_ok=True)
CORE.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_step206_recovery_v4_{timestamp}.py"
text = main_file.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

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

# Remove all broken Step 206 import lines.
lines = []
for line in text.splitlines():
    if "backend.app.core.billing_execution_guard import" in line:
        continue
    lines.append(line)

text = "\n".join(lines)

# Remove all prior Step 206 middleware blocks.
marker = "# Step 206 billing execution guard for client /run-agent requests"

while marker in text:
    marker_pos = text.find(marker)
    decorator_pos = text.rfind("@app.middleware", 0, marker_pos)
    block_start = decorator_pos if decorator_pos != -1 else marker_pos

    search_from = marker_pos + len(marker)
    end_candidates = []

    for candidate in [
        "\n@app.",
        "\n@router.",
        "\napp.include_router",
        "\nif __name__",
        "\ndef ",
        "\nasync def ",
        "\nclass ",
    ]:
        idx = text.find(candidate, search_from)
        if idx != -1:
            end_candidates.append(idx)

    block_end = min(end_candidates) if end_candidates else len(text)
    text = text[:block_start].rstrip() + "\n\n" + text[block_end:].lstrip()

middleware_block = r'''

# Step 206 billing execution guard for client /run-agent requests
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

    return await call_next(request)
'''

text = text.rstrip() + middleware_block + "\n"
main_file.write_text(text, encoding="utf-8")

py_compile.compile(str(guard_file), doraise=True)
py_compile.compile(str(main_file), doraise=True)

print("STEP_206_RECOVERY_V4_OK")
print(f"Backup: {backup}")
print(f"Updated: {guard_file}")
print(f"Updated: {main_file}")