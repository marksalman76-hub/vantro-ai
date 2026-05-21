from __future__ import annotations

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
