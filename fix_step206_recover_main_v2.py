from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
CORE = BACKEND / "core"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)
CORE.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

main_file = BACKEND / "main.py"
guard_file = CORE / "billing_execution_guard.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

backup = BACKUPS / f"main_before_step206_recovery_v2_{timestamp}.py"
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


def extract_tenant_id_from_request(header_tenant_id: Optional[str], payload: Optional[Dict[str, Any]]) -> Optional[str]:
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


def check_billing_execution_allowed(tenant_id: Optional[str], actor_role: Optional[str]) -> Dict[str, Any]:
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

# Remove any broken billing guard import lines wherever they were injected.
lines = [
    line for line in text.splitlines()
    if "backend.app.core.billing_execution_guard import" not in line
]
text = "\n".join(lines)

# Remove any previous Step 206 middleware blocks.
start_marker = "# Step 206 billing execution guard for client /run-agent requests"

while start_marker in text:
    start = text.find(start_marker)
    decorator_start = text.rfind("@app.middleware", 0, start)
    block_start = decorator_start if decorator_start != -1 else start

    end_candidates = []
    for marker in [
        "\n@app.",
        "\n@router.",
        "\napp.include_router",
        "\nif __name__",
        "\nasync def ",
        "\ndef ",
    ]:
        idx = text.find(marker, start + len(start_marker))
        if idx != -1:
            end_candidates.append(idx)

    block_end = min(end_candidates) if end_candidates else len(text)
    text = text[:block_start].rstrip() + "\n\n" + text[block_end:].lstrip()

import_line = (
    "from backend.app.core.billing_execution_guard import "
    "check_billing_execution_allowed, extract_tenant_id_from_request, parse_json_body_safely"
)

# Insert import safely near top, after future import only.
top_lines = text.splitlines()
insert_at = 0

if top_lines and top_lines[0].startswith("#!"):
    insert_at = 1

for i, line in enumerate(top_lines[:10]):
    if line.startswith("from __future__ import"):
        insert_at = i + 1

top_lines.insert(insert_at, import_line)
text = "\n".join(top_lines)

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

app_index = text.find("app = FastAPI(")

if app_index == -1:
    raise RuntimeError("app = FastAPI(...) declaration not found")

paren_start = text.find("(", app_index)
depth = 0
insert_pos = None
in_string = False
string_char = ""
escape = False

for i in range(paren_start, len(text)):
    char = text[i]

    if in_string:
        if escape:
            escape = False
        elif char == "\\":
            escape = True
        elif char == string_char:
            in_string = False
        continue

    if char in {"'", '"'}:
        in_string = True
        string_char = char
        continue

    if char == "(":
        depth += 1
    elif char == ")":
        depth -= 1
        if depth == 0:
            insert_pos = text.find("\n", i)
            if insert_pos == -1:
                insert_pos = i + 1
            break

if insert_pos is None:
    raise RuntimeError("Could not find end of app = FastAPI(...) declaration")

text = text[:insert_pos + 1] + middleware_block + text[insert_pos + 1:]

main_file.write_text(text, encoding="utf-8")

print("STEP_206_MAIN_RECOVERY_V2_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print(f"Updated: {guard_file}")
print("STEP_206_RECOVERY_V2_OK")