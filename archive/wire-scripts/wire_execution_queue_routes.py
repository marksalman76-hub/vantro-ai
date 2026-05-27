from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"main_before_execution_queue_routes_{timestamp}.py"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

import_line = "from backend.app.core.execution_queue_runtime import enqueue_execution, list_execution_queue, mark_execution_failed, queue_readiness"

if import_line not in text:
    text = text.replace(
        "from backend.app.core.execution_event_runtime import add_execution_event, list_execution_events",
        "from backend.app.core.execution_event_runtime import add_execution_event, list_execution_events\n" + import_line,
    )

routes = r'''

@app.get("/admin/execution-queue/readiness")
async def admin_execution_queue_readiness():
    return queue_readiness()


@app.get("/admin/execution-queue")
async def admin_execution_queue(tenant_id: str = "", status: str = "", limit: int = 50):
    return list_execution_queue(tenant_id=tenant_id, status=status, limit=limit)


@app.post("/admin/execution-queue/enqueue")
async def admin_execution_queue_enqueue(payload: dict):
    return enqueue_execution(payload)


@app.post("/admin/execution-queue/mark-failed")
async def admin_execution_queue_mark_failed(payload: dict):
    return mark_execution_failed(
        int(payload.get("queue_id") or 0),
        str(payload.get("error") or "manual_failure_test"),
    )
'''

if "/admin/execution-queue/readiness" not in text:
    marker = '\n@app.get("/admin/provider-execution-audit")'
    text = text.replace(marker, routes + "\n" + marker)

path.write_text(text, encoding="utf-8")

print("EXECUTION_QUEUE_ROUTES_WIRED")
print(f"Backup: {backup}")