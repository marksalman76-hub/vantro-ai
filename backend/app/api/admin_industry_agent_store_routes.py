from fastapi import APIRouter, Header, HTTPException, Query
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
