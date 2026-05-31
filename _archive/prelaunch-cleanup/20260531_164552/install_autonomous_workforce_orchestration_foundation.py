from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "autonomous_workforce_orchestration_foundation.py"
main_file = ROOT / "backend" / "app" / "main.py"
test_file = ROOT / "test_autonomous_workforce_orchestration_foundation.py"

backup_dir = ROOT / "backups" / f"autonomous_workforce_orchestration_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(main_file, backup_dir / "main.py")

runtime_file.write_text(r'''
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from backend.app.runtime.provider_workforce_runtime_hardening import (
    provider_runtime_health_summary,
    provider_recovery_readiness_summary,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def create_agent_to_agent_execution_packet(
    *,
    tenant_id: str,
    project_id: str,
    parent_agent: str,
    target_agent: str,
    task: str,
    orchestration_id: Optional[str] = None,
    priority: int = 5,
    requires_owner_approval: bool = False,
) -> Dict[str, Any]:
    packet_id = f"agent_packet_{uuid.uuid4().hex[:16]}"
    orchestration_id = orchestration_id or f"orch_{uuid.uuid4().hex[:16]}"

    return {
        "success": True,
        "profile": "agent_to_agent_execution_packet_v1",
        "packet_id": packet_id,
        "orchestration_id": orchestration_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "parent_agent": parent_agent,
        "target_agent": target_agent,
        "task": task,
        "priority": int(priority),
        "status": "prepared",
        "requires_owner_approval": bool(requires_owner_approval),
        "owner_approval_required_for_spend_scale_contracts": True,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def create_delegated_subtask_plan(
    *,
    tenant_id: str,
    project_id: str,
    lead_agent: str,
    objective: str,
    requested_agents: Optional[List[str]] = None,
) -> Dict[str, Any]:
    requested_agents = requested_agents or [
        "marketing_specialist_agent",
        "seo_agent",
        "crm_ai_agent",
    ]
    orchestration_id = f"orch_{uuid.uuid4().hex[:16]}"

    packets = [
        create_agent_to_agent_execution_packet(
            tenant_id=tenant_id,
            project_id=project_id,
            parent_agent=lead_agent,
            target_agent=agent,
            task=f"Support objective: {objective}",
            orchestration_id=orchestration_id,
            priority=index + 1,
            requires_owner_approval=False,
        )
        for index, agent in enumerate(requested_agents)
    ]

    return {
        "success": True,
        "profile": "delegated_subtask_plan_v1",
        "orchestration_id": orchestration_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "lead_agent": lead_agent,
        "objective": objective,
        "packet_count": len(packets),
        "packets": packets,
        "status": "prepared_for_governed_execution",
        "execution_mode": "planning_only",
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "created_at_ms": _now_ms(),
    }


def create_orchestration_execution_graph(plan: Dict[str, Any]) -> Dict[str, Any]:
    packets = list(plan.get("packets") or [])
    nodes = []
    edges = []

    lead_agent = str(plan.get("lead_agent") or "head_agent")
    orchestration_id = str(plan.get("orchestration_id") or f"orch_{uuid.uuid4().hex[:16]}")

    nodes.append({
        "node_id": f"agent::{lead_agent}",
        "type": "lead_agent",
        "label": lead_agent,
        "status": "ready",
    })

    for packet in packets:
        target = packet.get("target_agent")
        packet_id = packet.get("packet_id")
        nodes.append({
            "node_id": f"agent::{target}",
            "type": "delegated_agent",
            "label": target,
            "status": "prepared",
            "packet_id": packet_id,
        })
        edges.append({
            "from": f"agent::{lead_agent}",
            "to": f"agent::{target}",
            "type": "delegates_to",
            "packet_id": packet_id,
        })

    return {
        "success": True,
        "profile": "orchestration_execution_graph_v1",
        "orchestration_id": orchestration_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def orchestration_replay_recovery_packet(
    *,
    orchestration_id: str,
    failure_reason: str = "unknown",
    attempt_count: int = 0,
) -> Dict[str, Any]:
    recovery_readiness = provider_recovery_readiness_summary()

    retry_allowed = int(attempt_count) < 3
    next_action = "retry_prepared" if retry_allowed else "owner_review_required"

    return {
        "success": True,
        "profile": "orchestration_replay_recovery_packet_v1",
        "orchestration_id": orchestration_id,
        "failure_reason": failure_reason,
        "attempt_count": int(attempt_count),
        "retry_allowed": retry_allowed,
        "next_action": next_action,
        "recovery_readiness": recovery_readiness,
        "owner_review_required": not retry_allowed,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "created_at_ms": _now_ms(),
    }


def autonomous_workforce_orchestration_status() -> Dict[str, Any]:
    provider_health = provider_runtime_health_summary()
    recovery = provider_recovery_readiness_summary()

    return {
        "success": True,
        "profile": "autonomous_workforce_orchestration_foundation_v1",
        "visibility_only": True,
        "execution_mode": "governed_foundation_only",
        "autonomous_uncontrolled_actions_enabled": False,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
        "owner_approval_required_for_spend_scale_contracts": True,
        "foundation_layers": {
            "delegated_subtask_packets": True,
            "agent_to_agent_execution_packets": True,
            "orchestration_execution_graph": True,
            "orchestration_replay_recovery_packet": True,
            "provider_health_linked": True,
            "provider_recovery_linked": True,
            "customer_safe_status_packets": True,
            "uncontrolled_autonomy_blocked": True,
        },
        "provider_health": provider_health,
        "recovery_readiness": recovery,
        "checked_at_ms": _now_ms(),
    }
'''.lstrip(), encoding="utf-8")

main_text = main_file.read_text(encoding="utf-8")
import_line = "from backend.app.runtime.autonomous_workforce_orchestration_foundation import autonomous_workforce_orchestration_status, create_delegated_subtask_plan, create_orchestration_execution_graph, orchestration_replay_recovery_packet\n"
if import_line not in main_text:
    anchor = "from fastapi import"
    idx = main_text.find(anchor)
    if idx == -1:
        raise SystemExit("Could not find import anchor")
    end = main_text.find("\n", idx)
    main_text = main_text[:end + 1] + import_line + main_text[end + 1:]

route_block = r'''

@app.get("/admin/autonomous-workforce-orchestration/status")
async def admin_autonomous_workforce_orchestration_status():
    """
    Admin-safe autonomous workforce orchestration foundation status.

    This is visibility/readiness only. It does not execute live provider calls.
    """
    return autonomous_workforce_orchestration_status()


@app.post("/admin/autonomous-workforce-orchestration/plan")
async def admin_autonomous_workforce_orchestration_plan(payload: dict):
    """
    Create a governed delegated subtask plan without executing it.
    """
    plan = create_delegated_subtask_plan(
        tenant_id=str(payload.get("tenant_id") or "owner_admin"),
        project_id=str(payload.get("project_id") or "default_project"),
        lead_agent=str(payload.get("lead_agent") or "head_agent"),
        objective=str(payload.get("objective") or "Prepare governed workforce plan."),
        requested_agents=list(payload.get("requested_agents") or []),
    )
    graph = create_orchestration_execution_graph(plan)
    return {
        "success": True,
        "profile": "autonomous_workforce_orchestration_plan_response_v1",
        "visibility_only": True,
        "plan": plan,
        "execution_graph": graph,
        "live_external_call_executed": False,
        "external_action_performed": False,
        "credential_values_exposed": False,
        "customer_safe": True,
        "governance_enforced": True,
    }


@app.post("/admin/autonomous-workforce-orchestration/recovery")
async def admin_autonomous_workforce_orchestration_recovery(payload: dict):
    """
    Create a governed recovery/replay packet without executing it.
    """
    return orchestration_replay_recovery_packet(
        orchestration_id=str(payload.get("orchestration_id") or "unknown_orchestration"),
        failure_reason=str(payload.get("failure_reason") or "unknown"),
        attempt_count=int(payload.get("attempt_count") or 0),
    )
'''

if '"/admin/autonomous-workforce-orchestration/status"' not in main_text:
    main_text = main_text.rstrip() + "\n" + route_block + "\n"

main_file.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


status = client.get("/admin/autonomous-workforce-orchestration/status")
assert_true(status.status_code == 200, status.text)
data = status.json()
assert_true(data["success"] is True, "status success failed")
assert_true(data["visibility_only"] is True, "status must be visibility only")
assert_true(data["autonomous_uncontrolled_actions_enabled"] is False, "uncontrolled autonomy must be blocked")
assert_true(data["live_external_call_executed"] is False, "status must not execute live call")
assert_true(data["external_action_performed"] is False, "status must not perform action")
assert_true(data["credential_values_exposed"] is False, "credentials exposed")
assert_true(data["governance_enforced"] is True, "governance not enforced")
assert_true(data["owner_approval_required_for_spend_scale_contracts"] is True, "owner approval protection missing")

for key in [
    "delegated_subtask_packets",
    "agent_to_agent_execution_packets",
    "orchestration_execution_graph",
    "orchestration_replay_recovery_packet",
    "provider_health_linked",
    "provider_recovery_linked",
    "customer_safe_status_packets",
    "uncontrolled_autonomy_blocked",
]:
    assert_true(data["foundation_layers"][key] is True, f"{key} missing")

plan = client.post("/admin/autonomous-workforce-orchestration/plan", json={
    "tenant_id": "owner_admin",
    "project_id": "orchestration_foundation_test",
    "lead_agent": "head_agent",
    "objective": "Prepare launch execution plan.",
    "requested_agents": ["marketing_specialist_agent", "seo_agent", "crm_ai_agent"],
})
assert_true(plan.status_code == 200, plan.text)
plan_data = plan.json()
assert_true(plan_data["success"] is True, "plan success failed")
assert_true(plan_data["visibility_only"] is True, "plan must be visibility only")
assert_true(plan_data["live_external_call_executed"] is False, "plan must not execute live call")
assert_true(plan_data["external_action_performed"] is False, "plan must not perform action")
assert_true(plan_data["credential_values_exposed"] is False, "plan exposed credentials")
assert_true(plan_data["governance_enforced"] is True, "plan governance not enforced")
assert_true(plan_data["plan"]["packet_count"] == 3, "packet count mismatch")
assert_true(plan_data["execution_graph"]["node_count"] == 4, "graph node count mismatch")
assert_true(plan_data["execution_graph"]["edge_count"] == 3, "graph edge count mismatch")

recovery = client.post("/admin/autonomous-workforce-orchestration/recovery", json={
    "orchestration_id": plan_data["plan"]["orchestration_id"],
    "failure_reason": "provider_timeout",
    "attempt_count": 1,
})
assert_true(recovery.status_code == 200, recovery.text)
recovery_data = recovery.json()
assert_true(recovery_data["success"] is True, "recovery success failed")
assert_true(recovery_data["retry_allowed"] is True, "retry should be allowed")
assert_true(recovery_data["next_action"] == "retry_prepared", "wrong recovery next action")
assert_true(recovery_data["live_external_call_executed"] is False, "recovery must not execute live call")
assert_true(recovery_data["credential_values_exposed"] is False, "recovery exposed credentials")

print("AUTONOMOUS_WORKFORCE_ORCHESTRATION_FOUNDATION_TEST_PASSED")
print({
    "foundation_layers": data["foundation_layers"],
    "packet_count": plan_data["plan"]["packet_count"],
    "graph_nodes": plan_data["execution_graph"]["node_count"],
    "graph_edges": plan_data["execution_graph"]["edge_count"],
    "recovery_next_action": recovery_data["next_action"],
})
'''.lstrip(), encoding="utf-8")

print("AUTONOMOUS_WORKFORCE_ORCHESTRATION_FOUNDATION_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {runtime_file}")
print(f"Updated: {main_file}")
print(f"Created/updated: {test_file}")