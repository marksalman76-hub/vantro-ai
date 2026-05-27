from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_persistent_workflow_admin_endpoints_import.py"

if not main_file.exists():
    raise FileNotFoundError(f"Missing backend main file: {main_file}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"main_before_persistent_workflow_admin_endpoints_{timestamp}.py"

source = main_file.read_text(encoding="utf-8")
backup.write_text(source, encoding="utf-8")

marker = "# --- Persistent workflow admin diagnostic endpoints ---"

endpoint_block = r'''

# --- Persistent workflow admin diagnostic endpoints ---
# Admin/runtime diagnostics only. Customer-facing UI remains untouched.

@app.get("/admin/workflows/readiness")
async def admin_persistent_workflows_readiness():
    from backend.app.runtime.persistent_workflow_runtime import readiness

    return readiness()


@app.post("/admin/workflows/create-test")
async def admin_persistent_workflows_create_test(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import create_workflow

    payload = payload or {}
    return create_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        workflow_type=payload.get("workflow_type", "marketing_campaign_execution"),
        payload=payload.get("payload", {"test": "admin persistent workflow test"}),
        tenant_id=payload.get("tenant_id", "owner_admin_test"),
        actor_role=payload.get("actor_role", "owner_admin"),
        max_retries=int(payload.get("max_retries", 3)),
    )


@app.post("/admin/workflows/advance")
async def admin_persistent_workflows_advance(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import advance_workflow

    payload = payload or {}
    return advance_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        step_result=payload.get("step_result", {"admin_test": "advanced"}),
    )


@app.post("/admin/workflows/fail")
async def admin_persistent_workflows_fail(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import fail_workflow

    payload = payload or {}
    return fail_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        error=payload.get("error", {"admin_test": "temporary failure"}),
    )


@app.post("/admin/workflows/complete")
async def admin_persistent_workflows_complete(payload: dict | None = None):
    from backend.app.runtime.persistent_workflow_runtime import complete_workflow

    payload = payload or {}
    return complete_workflow(
        workflow_id=payload.get("workflow_id", "admin_test_workflow_001"),
        result=payload.get("result", {"admin_test": "completed"}),
    )


@app.get("/admin/workflows/{workflow_id}")
async def admin_persistent_workflows_get(workflow_id: str):
    from backend.app.runtime.persistent_workflow_runtime import get_workflow

    return get_workflow(workflow_id)
'''

if marker not in source:
    source = source.rstrip() + endpoint_block + "\n"
    main_file.write_text(source, encoding="utf-8")
    changed = True
else:
    changed = False

test_file.write_text(r'''
from backend.app.main import app


def main():
    routes = sorted([getattr(route, "path", "") for route in app.routes])

    required = [
        "/admin/workflows/readiness",
        "/admin/workflows/create-test",
        "/admin/workflows/advance",
        "/admin/workflows/fail",
        "/admin/workflows/complete",
        "/admin/workflows/{workflow_id}",
    ]

    print("PERSISTENT_WORKFLOW_ADMIN_ENDPOINT_IMPORT_TEST")
    for route in required:
        print(route, route in routes)
        assert route in routes

    print("PERSISTENT_WORKFLOW_ADMIN_ENDPOINT_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("PERSISTENT_WORKFLOW_ADMIN_ENDPOINTS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")
print(f"Changed: {changed}")
print("Admin/runtime diagnostics only. Governance preserved.")