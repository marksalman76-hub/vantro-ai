from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_cross_agent_orchestration_admin_endpoints_import.py"

if not main_file.exists():
    raise FileNotFoundError(f"Missing backend main file: {main_file}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"main_before_cross_agent_orchestration_admin_endpoints_{timestamp}.py"

source = main_file.read_text(encoding="utf-8")
backup.write_text(source, encoding="utf-8")

marker = "# --- Cross-agent orchestration admin diagnostic endpoints ---"

endpoint_block = r'''

# --- Cross-agent orchestration admin diagnostic endpoints ---
# Admin/runtime diagnostics only. Customer-facing UI remains untouched.

@app.get("/admin/orchestration/readiness")
async def admin_cross_agent_orchestration_readiness():
    from backend.app.runtime.cross_agent_workflow_orchestration import readiness

    return readiness()


@app.post("/admin/orchestration/create-test")
async def admin_cross_agent_orchestration_create_test(payload: dict | None = None):
    from backend.app.runtime.cross_agent_workflow_orchestration import create_cross_agent_orchestration

    payload = payload or {}
    return create_cross_agent_orchestration(
        orchestration_id=payload.get("orchestration_id", "admin_orchestration_test_001"),
        workflow_id=payload.get("workflow_id", "admin_orchestration_workflow_001"),
        tenant_id=payload.get("tenant_id", "owner_admin_test"),
        head_agent_id=payload.get("head_agent_id", "head_agent"),
        active_agent_count=int(payload.get("active_agent_count", 3)),
        objective=payload.get(
            "objective",
            {
                "workflow_type": "marketing_campaign_execution",
                "goal": "Admin cross-agent orchestration test",
            },
        ),
        tasks=payload.get(
            "tasks",
            [
                {
                    "task_id": "admin_task_marketing_001",
                    "assigned_agent_id": "marketing_specialist_agent",
                    "task_type": "content_generation",
                    "payload": {"brief": "Campaign angle"},
                },
                {
                    "task_id": "admin_task_email_001",
                    "assigned_agent_id": "email_reply_agent",
                    "task_type": "email_copy_generation",
                    "payload": {"brief": "Launch email"},
                },
                {
                    "task_id": "admin_task_spend_001",
                    "assigned_agent_id": "marketing_specialist_agent",
                    "task_type": "scale_campaign",
                    "payload": {"budget_increase": 1000},
                },
            ],
        ),
    )


@app.post("/admin/orchestration/task-complete")
async def admin_cross_agent_orchestration_task_complete(payload: dict | None = None):
    from backend.app.runtime.cross_agent_workflow_orchestration import complete_cross_agent_task

    payload = payload or {}
    return complete_cross_agent_task(
        orchestration_id=payload.get("orchestration_id", "admin_orchestration_test_001"),
        task_id=payload.get("task_id", "admin_task_marketing_001"),
        result=payload.get("result", {"admin_test": "task completed"}),
    )


@app.post("/admin/orchestration/task-fail")
async def admin_cross_agent_orchestration_task_fail(payload: dict | None = None):
    from backend.app.runtime.cross_agent_workflow_orchestration import fail_cross_agent_task

    payload = payload or {}
    return fail_cross_agent_task(
        orchestration_id=payload.get("orchestration_id", "admin_orchestration_test_001"),
        task_id=payload.get("task_id", "admin_task_email_001"),
        error=payload.get("error", {"admin_test": "temporary failure"}),
    )


@app.get("/admin/orchestration/{orchestration_id}")
async def admin_cross_agent_orchestration_get(orchestration_id: str):
    from backend.app.runtime.cross_agent_workflow_orchestration import get_cross_agent_orchestration

    return get_cross_agent_orchestration(orchestration_id)
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
        "/admin/orchestration/readiness",
        "/admin/orchestration/create-test",
        "/admin/orchestration/task-complete",
        "/admin/orchestration/task-fail",
        "/admin/orchestration/{orchestration_id}",
    ]

    print("CROSS_AGENT_ORCHESTRATION_ADMIN_ENDPOINT_IMPORT_TEST")
    for route in required:
        print(route, route in routes)
        assert route in routes

    print("CROSS_AGENT_ORCHESTRATION_ADMIN_ENDPOINT_IMPORT_OK")


if __name__ == "__main__":
    main()
'''.lstrip(), encoding="utf-8")

print("CROSS_AGENT_ORCHESTRATION_ADMIN_ENDPOINTS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")
print(f"Changed: {changed}")
print("Admin/runtime diagnostics only. Governance preserved.")
