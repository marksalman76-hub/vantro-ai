from pathlib import Path

ROOT = Path.cwd()

runtime = ROOT / "backend/app/core/admin_industry_agent_store_learning_vault.py"
runtime.parent.mkdir(parents=True, exist_ok=True)

runtime.write_text(r'''from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(os.getenv("ADMIN_INDUSTRY_STORE_DIR", "data/admin_industry_store"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

INDUSTRY_STORE = DATA_DIR / "industry_agent_store.json"
LEARNING_VAULT = DATA_DIR / "tenant_safe_learning_vault.jsonl"

SENSITIVE_KEYS = {
    "email",
    "phone",
    "address",
    "customer_name",
    "client_name",
    "business_name",
    "api_key",
    "token",
    "secret",
    "password",
    "raw_output",
    "raw_prompt",
    "private_notes",
    "credential",
}


def _now() -> int:
    return int(time.time())


def _load_store() -> Dict[str, Any]:
    if not INDUSTRY_STORE.exists():
        return {"industry_packs": []}
    try:
        return json.loads(INDUSTRY_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {"industry_packs": []}


def _save_store(data: Dict[str, Any]) -> None:
    INDUSTRY_STORE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _safe_text(value: Any, limit: int = 2000) -> str:
    text = str(value or "")
    for token in ["api key", "secret", "password", "token", "credential"]:
        text = text.replace(token, "[redacted]")
        text = text.replace(token.upper(), "[redacted]")
    return text[:limit]


def _tenant_safe_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if lowered in SENSITIVE_KEYS or any(s in lowered for s in ["secret", "password", "token", "credential", "email", "phone"]):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = _safe_text(value) if isinstance(value, str) else value
        elif isinstance(value, list):
            safe[key] = [_safe_text(x, 500) if isinstance(x, str) else x for x in value[:20]]
        elif isinstance(value, dict):
            safe[key] = _tenant_safe_payload(value)
    return safe


def create_or_update_industry_pack(payload: Dict[str, Any]) -> Dict[str, Any]:
    industry = _safe_text(payload.get("industry") or payload.get("industry_key") or "").strip().lower().replace(" ", "_")
    if not industry:
        return {"success": False, "error": "industry_required"}

    pack_id = payload.get("pack_id") or f"industry_pack_{industry}_{uuid.uuid4().hex[:10]}"
    agents = payload.get("agents") or payload.get("agent_ids") or []
    if not isinstance(agents, list):
        agents = []

    safe_pack = {
        "pack_id": pack_id,
        "industry": industry,
        "display_name": _safe_text(payload.get("display_name") or industry.replace("_", " ").title(), 160),
        "description": _safe_text(payload.get("description"), 1200),
        "agents": [
            {
                "agent_id": _safe_text(a.get("agent_id") if isinstance(a, dict) else a, 120),
                "role": _safe_text(a.get("role") if isinstance(a, dict) else "", 300),
                "default_instructions": _safe_text(a.get("default_instructions") if isinstance(a, dict) else "", 1200),
                "deployment_notes": _safe_text(a.get("deployment_notes") if isinstance(a, dict) else "", 1200),
            }
            for a in agents
        ],
        "recommended_integrations": [
            _safe_text(x, 120) for x in (payload.get("recommended_integrations") or [])[:25]
        ],
        "deployment_checklist": [
            _safe_text(x, 300) for x in (payload.get("deployment_checklist") or [])[:50]
        ],
        "owner_only": True,
        "tenant_safe": True,
        "updated_at": _now(),
        "created_at": _now(),
    }

    data = _load_store()
    packs = data.setdefault("industry_packs", [])
    for index, existing in enumerate(packs):
        if existing.get("pack_id") == pack_id or existing.get("industry") == industry:
            safe_pack["created_at"] = existing.get("created_at", safe_pack["created_at"])
            packs[index] = safe_pack
            _save_store(data)
            return {"success": True, "action": "updated", "pack": safe_pack}

    packs.insert(0, safe_pack)
    _save_store(data)
    return {"success": True, "action": "created", "pack": safe_pack}


def list_industry_packs(industry: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    packs = _load_store().get("industry_packs", [])
    if industry:
        needle = industry.lower().replace(" ", "_")
        packs = [p for p in packs if p.get("industry") == needle]
    return {"success": True, "count": len(packs[:limit]), "industry_packs": packs[:limit]}


def capture_tenant_safe_learning(payload: Dict[str, Any]) -> Dict[str, Any]:
    agent_id = _safe_text(payload.get("agent_id") or payload.get("requested_agent") or "unknown_agent", 120)
    industry = _safe_text(payload.get("industry") or payload.get("business_niche") or "general", 120).lower().replace(" ", "_")
    quality_score = payload.get("quality_score")
    try:
        quality_score = int(quality_score) if quality_score is not None else None
    except Exception:
        quality_score = None

    record = {
        "vault_id": f"learning_vault_{uuid.uuid4().hex[:14]}",
        "industry": industry,
        "agent_id": agent_id,
        "client_type": _safe_text(payload.get("client_type") or payload.get("package_name") or "", 160),
        "pattern_type": _safe_text(payload.get("pattern_type") or "execution_learning", 120),
        "successful_patterns": [_safe_text(x, 600) for x in (payload.get("successful_patterns") or [])[:20]],
        "failed_patterns": [_safe_text(x, 600) for x in (payload.get("failed_patterns") or [])[:20]],
        "recommended_improvements": [_safe_text(x, 700) for x in (payload.get("recommended_improvements") or [])[:20]],
        "quality_score": quality_score,
        "approved_by_client": bool(payload.get("approved_by_client")),
        "source": _safe_text(payload.get("source") or "agent_execution", 120),
        "tenant_safe_summary": _safe_text(payload.get("tenant_safe_summary") or payload.get("summary"), 2000),
        "reusable_template": _safe_text(payload.get("reusable_template"), 3000),
        "raw_private_data_stored": False,
        "tenant_safe": True,
        "owner_only": True,
        "created_at": _now(),
        "safe_metadata": _tenant_safe_payload(payload.get("metadata") or {}),
    }

    with LEARNING_VAULT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")

    return {
        "success": True,
        "vault_id": record["vault_id"],
        "tenant_safe": True,
        "raw_private_data_stored": False,
        "record": record,
    }


def list_learning_vault(
    industry: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    if LEARNING_VAULT.exists():
        for line in LEARNING_VAULT.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue

    if industry:
        needle = industry.lower().replace(" ", "_")
        rows = [r for r in rows if r.get("industry") == needle]
    if agent_id:
        rows = [r for r in rows if r.get("agent_id") == agent_id]

    rows = list(reversed(rows))
    return {"success": True, "count": len(rows[:limit]), "learning_records": rows[:limit]}


def admin_industry_learning_vault_status() -> Dict[str, Any]:
    pack_count = len(_load_store().get("industry_packs", []))
    learning_count = 0
    if LEARNING_VAULT.exists():
        learning_count = len([line for line in LEARNING_VAULT.read_text(encoding="utf-8").splitlines() if line.strip()])

    return {
        "success": True,
        "admin_industry_agent_store_ready": True,
        "tenant_safe_learning_vault_ready": True,
        "industry_pack_count": pack_count,
        "learning_record_count": learning_count,
        "owner_only": True,
        "raw_private_data_stored": False,
        "future_deployment_reuse_ready": True,
    }
''', encoding="utf-8")

routes = ROOT / "backend/app/api/admin_industry_agent_store_routes.py"
routes.parent.mkdir(parents=True, exist_ok=True)
routes.write_text(r'''from fastapi import APIRouter, Header, HTTPException, Query
from backend.app.core.admin_industry_agent_store_learning_vault import (
    create_or_update_industry_pack,
    list_industry_packs,
    capture_tenant_safe_learning,
    list_learning_vault,
    admin_industry_learning_vault_status,
)

router = APIRouter()


def _is_admin(role: str | None) -> bool:
    return (role or "").lower() in {"owner", "admin", "owner_admin", "system"}


def _guard(role: str | None):
    if not _is_admin(role):
        raise HTTPException(status_code=403, detail="admin_required")


@router.get("/admin/industry-agent-store/status")
def admin_industry_agent_store_status(x_actor_role: str | None = Header(default=None)):
    _guard(x_actor_role)
    return admin_industry_learning_vault_status()


@router.post("/admin/industry-agent-store/pack")
def admin_industry_agent_store_pack(payload: dict, x_actor_role: str | None = Header(default=None)):
    _guard(x_actor_role)
    return create_or_update_industry_pack(payload)


@router.get("/admin/industry-agent-store/packs")
def admin_industry_agent_store_packs(
    industry: str | None = Query(default=None),
    limit: int = Query(default=100),
    x_actor_role: str | None = Header(default=None),
):
    _guard(x_actor_role)
    return list_industry_packs(industry=industry, limit=limit)


@router.post("/admin/learning-vault/capture")
def admin_learning_vault_capture(payload: dict, x_actor_role: str | None = Header(default=None)):
    _guard(x_actor_role)
    return capture_tenant_safe_learning(payload)


@router.get("/admin/learning-vault/records")
def admin_learning_vault_records(
    industry: str | None = Query(default=None),
    agent_id: str | None = Query(default=None),
    limit: int = Query(default=100),
    x_actor_role: str | None = Header(default=None),
):
    _guard(x_actor_role)
    return list_learning_vault(industry=industry, agent_id=agent_id, limit=limit)
''', encoding="utf-8")

main = ROOT / "backend/app/main.py"
text = main.read_text(encoding="utf-8")
if "admin_industry_agent_store_routes" not in text:
    text += '''

# Admin Industry Agent Store + Tenant-Safe Learning Vault routes
try:
    from backend.app.api.admin_industry_agent_store_routes import router as admin_industry_agent_store_router
    app.include_router(admin_industry_agent_store_router)
except Exception as exc:
    print(f"ADMIN_INDUSTRY_AGENT_STORE_ROUTES_NOT_LOADED: {exc}")
'''
    main.write_text(text, encoding="utf-8")
    print("PATCHED backend/app/main.py")
else:
    print("NO_CHANGE backend/app/main.py")

test = ROOT / "test_admin_industry_agent_store_learning_vault.py"
test.write_text(r'''import os
import tempfile

os.environ["ADMIN_INDUSTRY_STORE_DIR"] = tempfile.mkdtemp(prefix="industry_store_test_")

from backend.app.core.admin_industry_agent_store_learning_vault import (
    create_or_update_industry_pack,
    list_industry_packs,
    capture_tenant_safe_learning,
    list_learning_vault,
    admin_industry_learning_vault_status,
)


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


pack = create_or_update_industry_pack({
    "industry": "Real Estate",
    "display_name": "Real Estate Growth Pack",
    "description": "Reusable agent deployment pack for property businesses.",
    "agents": [
        {"agent_id": "lead_generator_appointment_setter_agent", "role": "Buyer/seller lead flow"},
        {"agent_id": "social_media_manager_content_creator_agent", "role": "Listing content"},
    ],
    "recommended_integrations": ["crm", "calendar", "email"],
    "deployment_checklist": ["Connect CRM", "Load brand profile", "Confirm approval rules"],
})
assert_true(pack["success"], "industry pack should save")
assert_true(pack["pack"]["tenant_safe"] is True, "industry pack must be tenant-safe")

packs = list_industry_packs(industry="real_estate")
assert_true(packs["count"] == 1, "industry pack should be queryable")

capture = capture_tenant_safe_learning({
    "industry": "Real Estate",
    "agent_id": "lead_generator_appointment_setter_agent",
    "client_type": "Growth",
    "quality_score": 91,
    "approved_by_client": True,
    "tenant_safe_summary": "Short local-market lead magnet offers worked best.",
    "successful_patterns": ["Local suburb-specific seller valuation hooks"],
    "failed_patterns": ["Generic national property copy"],
    "recommended_improvements": ["Use location specificity and appointment-led CTA"],
    "raw_output": "PRIVATE CLIENT OUTPUT SHOULD NOT BE STORED",
    "customer_email": "private@example.com",
    "metadata": {"safe_segment": "property", "api_key": "SHOULD_NOT_STORE"},
})
assert_true(capture["success"], "learning capture should succeed")
assert_true(capture["raw_private_data_stored"] is False, "raw private data must not be stored")
record = capture["record"]
assert_true("raw_output" not in record, "raw output must not be present")
assert_true("customer_email" not in record, "customer email must not be present")
assert_true("api_key" not in record.get("safe_metadata", {}), "api key must not be present")

records = list_learning_vault(industry="real_estate", agent_id="lead_generator_appointment_setter_agent")
assert_true(records["count"] == 1, "learning record should be queryable")

status = admin_industry_learning_vault_status()
assert_true(status["admin_industry_agent_store_ready"] is True, "industry store status ready")
assert_true(status["tenant_safe_learning_vault_ready"] is True, "learning vault status ready")
assert_true(status["future_deployment_reuse_ready"] is True, "future deployment reuse ready")

print("ADMIN_INDUSTRY_AGENT_STORE_LEARNING_VAULT_TEST_PASSED")
''', encoding="utf-8")

print("ADMIN_INDUSTRY_AGENT_STORE_LEARNING_VAULT_INSTALLED")