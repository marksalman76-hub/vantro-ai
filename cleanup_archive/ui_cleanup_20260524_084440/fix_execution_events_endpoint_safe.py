from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"main_before_safe_execution_events_endpoint_{timestamp}.py"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

lines = path.read_text(encoding="utf-8").splitlines()

start = None
end = None

for index, line in enumerate(lines):
    if line.strip() == '@app.get("/client/execution-events")':
        start = index
        break

if start is None:
    raise RuntimeError("execution events endpoint not found")

for index in range(start + 1, len(lines)):
    if lines[index].startswith("@app.") and index > start:
        end = index
        break

if end is None:
    raise RuntimeError("next FastAPI endpoint not found")

replacement = '''
@app.get("/client/execution-events")
def client_execution_events(
    tenant_id: str = "client_demo_001",
    project_id: str = "",
    limit: int = 25,
) -> Dict[str, object]:
    try:
        safe_limit = max(1, min(int(limit or 25), 100))
        safe_tenant_id = str(tenant_id or "client_demo_001")
        safe_project_id = str(project_id or "")

        events = execution_event_ledger.latest(
            tenant_id=safe_tenant_id,
            project_id=safe_project_id or None,
            limit=safe_limit,
            client_visible_only=True,
        )

        return {
            "success": True,
            "tenant_id": safe_tenant_id,
            "project_id": safe_project_id or None,
            "count": len(events),
            "events": events,
        }
    except Exception as error:
        return {
            "success": False,
            "error": "execution_event_ledger_unavailable",
            "message": str(error),
            "tenant_id": str(tenant_id or "client_demo_001"),
            "project_id": str(project_id or "") or None,
            "count": 0,
            "events": [],
        }

'''.strip("\n").splitlines()

updated = lines[:start] + replacement + [""] + lines[end:]
path.write_text("\n".join(updated) + "\n", encoding="utf-8")

print("SAFE_EXECUTION_EVENTS_ENDPOINT_FIXED")
print(f"Backup: {backup}")