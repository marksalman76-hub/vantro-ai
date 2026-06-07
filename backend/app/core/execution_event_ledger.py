from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from backend.app.runtime.durable_execution_history_evidence_runtime import (
    list_execution_events,
    record_execution_event,
    record_approval_action_audit,
)


DATA_DIR = Path("backend/app/data")
LEDGER_FILE = DATA_DIR / "execution_event_ledger.jsonl"


class ExecutionEventLedger:
    def __init__(self, path: Path = LEDGER_FILE) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

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
        payload = {
            "agent_id": agent_id,
            "actor_role": actor_role,
            "workflow_stage": workflow_stage,
            "action_type": action_type,
            "execution_action": execution_action,
            "event_status": event_status,
            "title": title,
            "summary": summary,
            "workflow": workflow or {},
            "approval": approval or {},
            "quality": quality or {},
            "execution": execution or {},
            "owner_approved": bool(owner_approved),
            "client_visible": bool(client_visible),
            **(metadata or {}),
        }
        result = record_execution_event(
            tenant_id=tenant_id,
            project_id=project_id or "default_project",
            execution_id=str((execution or {}).get("execution_id") or ""),
            event_type=event_type,
            source_type="execution_event_ledger",
            source_id=str((metadata or {}).get("source_id") or ""),
            payload=payload,
        )
        if approval:
            record_approval_action_audit(
                tenant_id=tenant_id,
                project_id=project_id or "default_project",
                execution_id=str((execution or {}).get("execution_id") or ""),
                action_id=str(execution_action or action_type or ""),
                action_type=action_type,
                decision=str(approval.get("status") or approval.get("decision") or event_status),
                actor_role=actor_role,
                payload={"approval": approval, "owner_approved": owner_approved},
            )
        event = result.get("event") or {}
        safe_event = {
            "event_id": event.get("event_id") or result.get("event_id"),
            "created_at": event.get("created_at") or self._now(),
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
            "workflow_status": (workflow or {}).get("status") or (workflow or {}).get("workflow_status") or "created",
            "approval_status": (approval or {}).get("status") or (approval or {}).get("decision") or "not_required",
            "quality_status": (quality or {}).get("status") or ("passed" if (quality or {}).get("passed") is True else "not_reviewed"),
            "execution_status": (execution or {}).get("execution_status") or (execution or {}).get("status") or "not_executed",
            "owner_approval_required": str((approval or {}).get("status") or "").lower() in {"awaiting_owner_approval", "blocked_pending_owner_approval", "pending_owner_approval"},
            "owner_approved": bool(owner_approved),
            "client_visible": bool(client_visible),
            "metadata": payload,
            "credential_values_exposed": False,
        }
        return {"success": bool(result.get("success")), "event": safe_event}

    def latest(
        self,
        *,
        tenant_id: str,
        project_id: Optional[str] = None,
        limit: int = 25,
        client_visible_only: bool = True,
    ) -> List[Dict[str, object]]:
        result = list_execution_events(
            tenant_id=tenant_id,
            project_id=project_id or "",
            limit=limit,
        )
        events = result.get("events", []) if result.get("success") else []
        rows: List[Dict[str, object]] = []
        for event in events:
            payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
            if client_visible_only and payload.get("client_visible") is False:
                continue
            rows.append(
                {
                    "event_id": event.get("event_id"),
                    "created_at": event.get("created_at"),
                    "tenant_id": event.get("tenant_id"),
                    "project_id": event.get("project_id"),
                    "agent_id": payload.get("agent_id"),
                    "actor_role": payload.get("actor_role"),
                    "workflow_stage": payload.get("workflow_stage"),
                    "action_type": payload.get("action_type"),
                    "execution_action": payload.get("execution_action"),
                    "event_type": event.get("event_type"),
                    "event_status": payload.get("event_status"),
                    "title": payload.get("title"),
                    "summary": payload.get("summary"),
                    "workflow_status": (payload.get("workflow") or {}).get("status") if isinstance(payload.get("workflow"), dict) else None,
                    "approval_status": (payload.get("approval") or {}).get("status") if isinstance(payload.get("approval"), dict) else None,
                    "quality_status": (payload.get("quality") or {}).get("status") if isinstance(payload.get("quality"), dict) else None,
                    "execution_status": (payload.get("execution") or {}).get("execution_status") if isinstance(payload.get("execution"), dict) else None,
                    "owner_approval_required": False,
                    "owner_approved": bool(payload.get("owner_approved")),
                    "client_visible": payload.get("client_visible", True),
                    "metadata": payload,
                    "credential_values_exposed": False,
                }
            )
        return rows[: max(1, min(int(limit or 25), 100))]


execution_event_ledger = ExecutionEventLedger()
