from pathlib import Path
from datetime import datetime

root = Path(".")
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

ledger_path = root / "backend/app/core/execution_event_ledger.py"
main_path = root / "backend/app/main.py"

main_backup = backup_dir / f"main_before_execution_event_ledger_{timestamp}.py"
if main_path.exists():
    main_backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

ledger_content = r'''from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


DATA_DIR = Path("backend/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LEDGER_FILE = DATA_DIR / "execution_event_ledger.jsonl"


SAFE_EVENT_FIELDS = {
    "event_id",
    "created_at",
    "tenant_id",
    "project_id",
    "agent_id",
    "actor_role",
    "workflow_stage",
    "action_type",
    "execution_action",
    "event_type",
    "event_status",
    "title",
    "summary",
    "workflow_status",
    "approval_status",
    "quality_status",
    "execution_status",
    "owner_approval_required",
    "owner_approved",
    "client_visible",
    "metadata",
}


class ExecutionEventLedger:
    def __init__(self, path: Path = LEDGER_FILE) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _event_id(self, tenant_id: str, agent_id: str, event_type: str) -> str:
        safe_tenant = str(tenant_id or "tenant").replace(" ", "_")
        safe_agent = str(agent_id or "agent").replace(" ", "_")
        safe_type = str(event_type or "event").replace(" ", "_")
        return f"evt_{safe_tenant}_{safe_agent}_{safe_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    def record(
        self,
        *,
        tenant_id: str,
        project_id: str,
        agent_id: str,
        actor_role: str,
        workflow_stage: str,
        action_type: str,
        execution_action: Optional[str],
        event_type: str,
        event_status: str,
        title: str,
        summary: str,
        workflow: Optional[Dict[str, object]] = None,
        approval: Optional[Dict[str, object]] = None,
        quality: Optional[Dict[str, object]] = None,
        execution: Optional[Dict[str, object]] = None,
        owner_approved: bool = False,
        client_visible: bool = True,
        metadata: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        workflow = workflow or {}
        approval = approval or {}
        quality = quality or {}
        execution = execution or {}
        metadata = metadata or {}

        approval_status = (
            approval.get("status")
            or approval.get("approval_status")
            or approval.get("decision")
            or "not_required"
        )

        quality_status = (
            quality.get("status")
            or quality.get("quality_status")
            or ("passed" if quality.get("passed") is True else "not_reviewed")
        )

        execution_status = (
            execution.get("execution_status")
            or execution.get("status")
            or "not_executed"
        )

        event = {
            "event_id": self._event_id(tenant_id, agent_id, event_type),
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": project_id,
            "agent_id": agent_id,
            "actor_role": actor_role,
            "workflow_stage": workflow_stage,
            "action_type": action_type,
            "execution_action": execution_action,
            "event_type": event_type,
            "event_status": event_status,
            "title": title,
            "summary": summary,
            "workflow_status": workflow.get("status") or workflow.get("workflow_status") or "created",
            "approval_status": approval_status,
            "quality_status": quality_status,
            "execution_status": execution_status,
            "owner_approval_required": str(approval_status).lower() in {
                "awaiting_owner_approval",
                "blocked_pending_owner_approval",
                "pending_owner_approval",
            },
            "owner_approved": bool(owner_approved),
            "client_visible": bool(client_visible),
            "metadata": {
                "workflow": workflow,
                "approval": approval,
                "quality": quality,
                "execution": execution,
                **metadata,
            },
        }

        safe_event = {key: event.get(key) for key in SAFE_EVENT_FIELDS}
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(safe_event, ensure_ascii=False) + "\n")

        return {
            "success": True,
            "event": safe_event,
        }

    def latest(
        self,
        *,
        tenant_id: str,
        project_id: Optional[str] = None,
        limit: int = 25,
        client_visible_only: bool = True,
    ) -> List[Dict[str, object]]:
        if not self.path.exists():
            return []

        rows: List[Dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except Exception:
                    continue

                if str(event.get("tenant_id")) != str(tenant_id):
                    continue

                if project_id and str(event.get("project_id")) != str(project_id):
                    continue

                if client_visible_only and event.get("client_visible") is not True:
                    continue

                rows.append(event)

        rows.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return rows[: max(1, min(int(limit or 25), 100))]


execution_event_ledger = ExecutionEventLedger()
'''

ledger_path.write_text(ledger_content, encoding="utf-8")

main_text = main_path.read_text(encoding="utf-8")

if "from backend.app.core.execution_event_ledger import execution_event_ledger" not in main_text:
    main_text = main_text.replace(
        "from backend.app.runtime.execution_stack import ExecutionRequest, ExecutionStack, execution_summary",
        "from backend.app.runtime.execution_stack import ExecutionRequest, ExecutionStack, execution_summary\nfrom backend.app.core.execution_event_ledger import execution_event_ledger",
    )

blocked_old = '''        return {
            "success": False,
            "status": approval_decision.status,
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_summary(approval_decision),
            "message": "Action paused or rejected by owner approval gateway.",
        }'''

blocked_new = '''        execution_event_ledger.record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            agent_id=requested_agent,
            actor_role=request.actor_role,
            workflow_stage=request.workflow_stage,
            action_type=request.action_type,
            execution_action=None,
            event_type="approval_gate_blocked",
            event_status=approval_decision.status,
            title=f"{requested_agent} action paused by approval gateway",
            summary="Action paused or rejected by owner approval gateway.",
            workflow=workflow_summary(workflow_packet),
            approval=approval_summary(approval_decision),
            owner_approved=request.owner_approved,
            client_visible=True,
        )

        return {
            "success": False,
            "status": approval_decision.status,
            "workflow": workflow_summary(workflow_packet),
            "approval": approval_summary(approval_decision),
            "message": "Action paused or rejected by owner approval gateway.",
        }'''

if blocked_old in main_text and "approval_gate_blocked" not in main_text:
    main_text = main_text.replace(blocked_old, blocked_new)

quality_old = '''        return {
            "success": False,
            "status": "quality_gate_failed",
            "workflow": workflow_summary(workflow_packet),
            "quality": quality_summary(quality_result),
            "message": "Output rejected by premium quality gate.",
        }'''

quality_new = '''        execution_event_ledger.record(
            tenant_id=request.tenant_id,
            project_id=request.project_id,
            agent_id=requested_agent,
            actor_role=request.actor_role,
            workflow_stage=request.workflow_stage,
            action_type=request.action_type,
            execution_action=None,
            event_type="quality_gate_failed",
            event_status="quality_gate_failed",
            title=f"{requested_agent} output rejected by premium quality gate",
            summary="Output rejected by premium quality gate.",
            workflow=workflow_summary(workflow_packet),
            quality=quality_summary(quality_result),
            owner_approved=request.owner_approved,
            client_visible=True,
        )

        return {
            "success": False,
            "status": "quality_gate_failed",
            "workflow": workflow_summary(workflow_packet),
            "quality": quality_summary(quality_result),
            "message": "Output rejected by premium quality gate.",
        }'''

if quality_old in main_text and "event_type=\"quality_gate_failed\"" not in main_text:
    main_text = main_text.replace(quality_old, quality_new)

success_old = '''    latest_sqlite_record = sqlite_store.latest_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
    )'''

success_new = '''    execution_event_ledger.record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        agent_id=requested_agent,
        actor_role=request.actor_role,
        workflow_stage=request.workflow_stage,
        action_type=request.action_type,
        execution_action=execution_action,
        event_type="agent_execution_completed",
        event_status="agent_execution_completed",
        title=f"{requested_agent} execution completed",
        summary="Agent output passed workflow, approval, quality, and governed execution handling.",
        workflow=workflow_summary(workflow_packet),
        approval=approval_summary(approval_decision),
        quality=quality_summary(quality_result),
        execution=execution_summary(execution_result) if execution_result else None,
        owner_approved=request.owner_approved,
        client_visible=True,
    )

    latest_sqlite_record = sqlite_store.latest_record(
        tenant_id=request.tenant_id,
        project_id=request.project_id,
        record_type="successful_execution",
    )'''

if success_old in main_text and "event_type=\"agent_execution_completed\"" not in main_text:
    main_text = main_text.replace(success_old, success_new)

if "@app.get(\"/client/execution-events\")" not in main_text:
    insert_marker = "\n\n@app.post(\"/run-agent\")\ndef run_agent"
    endpoint = r'''

@app.get("/client/execution-events")
def client_execution_events(
    tenant_id: str = "client_demo_001",
    project_id: str = "",
    limit: int = 25,
) -> Dict[str, object]:
    safe_limit = max(1, min(int(limit or 25), 100))
    events = execution_event_ledger.latest(
        tenant_id=tenant_id,
        project_id=project_id or None,
        limit=safe_limit,
        client_visible_only=True,
    )
    return {
        "success": True,
        "tenant_id": tenant_id,
        "project_id": project_id or None,
        "count": len(events),
        "events": events,
    }
'''
    main_text = main_text.replace(insert_marker, endpoint + insert_marker)

main_path.write_text(main_text, encoding="utf-8")

print("EXECUTION_EVENT_LEDGER_INSTALLED")
print(f"Created: {ledger_path}")
print(f"Updated: {main_path}")
print(f"Backup: {main_backup}")