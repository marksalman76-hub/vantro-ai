from fastapi import APIRouter, Header, HTTPException
from backend.app.core.admin_commercial_operations_visibility import admin_commercial_operations_status

router = APIRouter()

def _guard(role: str | None):
    if (role or "").lower() not in {"owner", "admin", "owner_admin", "system"}:
        raise HTTPException(status_code=403, detail="admin_required")

@router.get("/admin/commercial-operations/status")
def get_admin_commercial_operations_status(x_actor_role: str | None = Header(default=None)):
    _guard(x_actor_role)
    return admin_commercial_operations_status()
