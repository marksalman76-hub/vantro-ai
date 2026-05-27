from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"main_before_async_provider_job_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(MAIN, backup)

s = MAIN.read_text(encoding="utf-8")

import_block = (
    "from backend.app.runtime.async_provider_job_runtime import "
    "create_async_provider_job, get_async_provider_job, list_async_provider_jobs, "
    "update_async_provider_job_status, mark_async_provider_job_retry\n"
)

if import_block not in s:
    marker = "from backend.app.runtime.real_provider_activation_registry import"
    idx = s.find(marker)
    if idx != -1:
        line_end = s.find("\n", idx)
        s = s[:line_end+1] + import_block + s[line_end+1:]
    else:
        fastapi_idx = s.find("from fastapi import")
        line_end = s.find("\n", fastapi_idx)
        s = s[:line_end+1] + import_block + s[line_end+1:]

route_block = r'''

@app.post("/admin/provider-jobs/create")
def admin_provider_jobs_create(payload: dict):
    return create_async_provider_job(
        tenant_id=str(payload.get("tenant_id", "admin-internal")),
        actor_role=str(payload.get("actor_role", "owner")),
        provider_key=str(payload.get("provider_key", "openai")),
        capability=str(payload.get("capability", "text")),
        request_payload=dict(payload.get("request_payload", {})),
        owner_approval_required=bool(payload.get("owner_approval_required", True)),
    )


@app.get("/admin/provider-jobs/list")
def admin_provider_jobs_list(tenant_id: str = None, status: str = None):
    return list_async_provider_jobs(tenant_id=tenant_id, status=status)


@app.get("/admin/provider-jobs/{job_id}")
def admin_provider_jobs_get(job_id: str):
    return get_async_provider_job(job_id)


@app.post("/admin/provider-jobs/{job_id}/status")
def admin_provider_jobs_update_status(job_id: str, payload: dict):
    return update_async_provider_job_status(
        job_id=job_id,
        status=str(payload.get("status", "queued")),
        provider_job_id=payload.get("provider_job_id"),
        provider_status=payload.get("provider_status"),
        failure_reason=payload.get("failure_reason"),
        asset_delivery_packet=payload.get("asset_delivery_packet"),
    )


@app.post("/admin/provider-jobs/{job_id}/retry")
def admin_provider_jobs_retry(job_id: str, payload: dict):
    return mark_async_provider_job_retry(
        job_id=job_id,
        reason=str(payload.get("reason", "manual_retry_requested")),
    )
'''

if '"/admin/provider-jobs/create"' not in s:
    s += route_block

MAIN.write_text(s, encoding="utf-8")

test = ROOT / "test_async_provider_job_admin_routes.py"
test.write_text(r'''from backend.app.main import app

routes = sorted([getattr(route, "path", "") for route in app.routes])

required = [
    "/admin/provider-jobs/create",
    "/admin/provider-jobs/list",
    "/admin/provider-jobs/{job_id}",
    "/admin/provider-jobs/{job_id}/status",
    "/admin/provider-jobs/{job_id}/retry",
]

missing = [route for route in required if route not in routes]
assert not missing, f"Missing routes: {missing}"

print("ASYNC_PROVIDER_JOB_ADMIN_ROUTES_TEST_PASSED")
for route in required:
    print(route)
''', encoding="utf-8")

print("ASYNC_PROVIDER_JOB_ADMIN_ROUTES_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test}")