from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ORCHESTRATION_STATE_PROFILE = "priority6_orchestration_state_runtime_v1"

ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "orchestration"
DATA_DIR.mkdir(parents=True, exist_ok=True)

STATE_LOG = DATA_DIR / "orchestration_state_events.jsonl"
RESULT_MEMORY = DATA_DIR / "orchestration_result_memory.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 100) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def record_orchestration_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan_id = str(payload.get("plan_id") or payload.get("project_id") or f"orch_{uuid.uuid4().hex[:16]}")
    event_type = str(payload.get("event_type") or "orchestration_state_recorded")

    event = {
        "event_id": f"orch_state_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "profile": ORCHESTRATION_STATE_PROFILE,
        "plan_id": plan_id,
        "tenant_id": str(payload.get("tenant_id") or "unknown"),
        "event_type": event_type,
        "status": str(payload.get("status") or "recorded"),
        "step_id": payload.get("step_id"),
        "agent_id": payload.get("agent_id"),
        "dependency_status": payload.get("dependency_status") or {},
        "parallel_group": payload.get("parallel_group"),
        "head_agent_review_required": bool(payload.get("head_agent_review_required", False)),
        "recovery_marker": payload.get("recovery_marker") or f"recover_{plan_id}",
        "data": payload.get("data") or {},
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    _append_jsonl(STATE_LOG, event)

    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "event": event,
        "state_persisted": True,
    }


def record_orchestration_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan_id = str(payload.get("plan_id") or f"orch_{uuid.uuid4().hex[:16]}")
    step_id = str(payload.get("step_id") or "")
    agent_id = str(payload.get("agent_id") or "")

    memory = {
        "memory_id": f"orch_result_{uuid.uuid4().hex[:16]}",
        "timestamp": _now_iso(),
        "profile": ORCHESTRATION_STATE_PROFILE,
        "plan_id": plan_id,
        "tenant_id": str(payload.get("tenant_id") or "unknown"),
        "step_id": step_id,
        "agent_id": agent_id,
        "result_type": str(payload.get("result_type") or "agent_output"),
        "result_summary": str(payload.get("result_summary") or "")[:2000],
        "result_payload": payload.get("result_payload") or {},
        "available_for_next_steps": True,
        "cross_agent_result_passing_enabled": True,
        "head_agent_review_required": bool(payload.get("head_agent_review_required", False)),
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    _append_jsonl(RESULT_MEMORY, memory)

    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "memory": memory,
        "result_memory_persisted": True,
    }


def get_orchestration_context(plan_id: str, limit: int = 50) -> Dict[str, Any]:
    plan_id = str(plan_id or "").strip()

    state_events = [
        event for event in _read_jsonl(STATE_LOG, limit=500)
        if str(event.get("plan_id")) == plan_id
    ][-limit:]

    result_memory = [
        memory for memory in _read_jsonl(RESULT_MEMORY, limit=500)
        if str(memory.get("plan_id")) == plan_id
    ][-limit:]

    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "plan_id": plan_id,
        "state_event_count": len(state_events),
        "result_memory_count": len(result_memory),
        "state_events": state_events,
        "result_memory": result_memory,
        "cross_agent_context_available": len(result_memory) > 0,
        "recovery_context_available": len(state_events) > 0,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def orchestration_recovery_packet(plan_id: str) -> Dict[str, Any]:
    context = get_orchestration_context(plan_id, limit=100)
    state_events = context.get("state_events", [])
    result_memory = context.get("result_memory", [])

    completed_steps = [
        event.get("step_id")
        for event in state_events
        if event.get("status") in {"completed", "processed", "worker_foundation_processed"}
    ]

    last_event = state_events[-1] if state_events else None

    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "plan_id": plan_id,
        "recovery_ready": True,
        "last_event": last_event,
        "completed_steps": completed_steps,
        "result_memory_count": len(result_memory),
        "next_step_selection_ready": True,
        "head_agent_review_ready": any(m.get("head_agent_review_required") for m in result_memory),
        "parallel_safe_resume_ready": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def orchestration_state_readiness() -> Dict[str, Any]:
    state_count = len(_read_jsonl(STATE_LOG, limit=1000))
    result_count = len(_read_jsonl(RESULT_MEMORY, limit=1000))

    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_STATE_PROFILE,
        "orchestration_state_persistence_enabled": True,
        "orchestration_result_memory_enabled": True,
        "cross_agent_output_passing_enabled": True,
        "orchestration_recovery_continuation_enabled": True,
        "parallel_execution_scheduling_foundation": True,
        "head_agent_review_runtime_foundation": True,
        "orchestration_telemetry_enabled": True,
        "orchestration_replay_recovery_tooling_enabled": True,
        "state_log_path": str(STATE_LOG),
        "result_memory_path": str(RESULT_MEMORY),
        "state_log_exists": STATE_LOG.exists(),
        "result_memory_exists": RESULT_MEMORY.exists(),
        "state_event_count": state_count,
        "result_memory_count": result_count,
        "customer_safe_response_mode": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }
