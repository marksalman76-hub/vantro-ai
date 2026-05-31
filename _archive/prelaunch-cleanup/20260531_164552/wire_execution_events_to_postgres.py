from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")
backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"main_before_postgres_execution_events_{timestamp}.py"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

import_line = "from backend.app.core.execution_event_runtime import add_execution_event, list_execution_events"

if import_line not in text:
    text = text.replace(
        "from backend.app.core.execution_event_ledger import execution_event_ledger",
        "from backend.app.core.execution_event_ledger import execution_event_ledger\n" + import_line,
    )

text = text.replace(
'''        execution_event_ledger.record(
            tenant_id=request.tenant_id,''',
'''        add_execution_event(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            event_type="approval_gate_blocked",
            title=f"{requested_agent} action paused by approval gateway",
            agent_id=requested_agent,
            payload=blocked_payload,
        )

        execution_event_ledger.record(
            tenant_id=request.tenant_id,''',
    1,
)

text = text.replace(
'''        execution_event_ledger.record(
            tenant_id=request.tenant_id,''',
'''        add_execution_event(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            event_type="quality_gate_failed",
            title=f"{requested_agent} output rejected by premium quality gate",
            agent_id=requested_agent,
            payload=quality_failure_payload,
        )

        execution_event_ledger.record(
            tenant_id=request.tenant_id,''',
    1,
)

text = text.replace(
'''    execution_event_ledger.record(
        tenant_id=request.tenant_id,''',
'''    add_execution_event(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        event_type="agent_execution_completed",
        title=f"{requested_agent} execution completed",
        agent_id=requested_agent,
        payload=successful_payload,
    )

    execution_event_ledger.record(
        tenant_id=request.tenant_id,''',
    1,
)

old_endpoint_inner = '''        events = execution_event_ledger.latest(
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
        }'''

new_endpoint_inner = '''        durable_result = list_execution_events(
            tenant_id=safe_tenant_id,
            project_id=safe_project_id or "default_project",
            limit=safe_limit,
        )

        if durable_result.get("success"):
            return durable_result

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
            "storage_mode": "file_fallback",
        }'''

if old_endpoint_inner not in text:
    raise RuntimeError("execution events endpoint block not found")

text = text.replace(old_endpoint_inner, new_endpoint_inner)

path.write_text(text, encoding="utf-8")

print("EXECUTION_EVENTS_POSTGRES_WIRED")
print(f"Backup: {backup}")