from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
ORCH = ROOT / "backend" / "app" / "core" / "multi_agent_orchestration_runtime.py"
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

orch_backup = BACKUPS / f"multi_agent_orchestration_runtime_before_queue_integration_{timestamp}.py"
main_backup = BACKUPS / f"main_before_orchestration_queue_integration_{timestamp}.py"

orch_backup.write_text(ORCH.read_text(encoding="utf-8"), encoding="utf-8")
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

orch_text = ORCH.read_text(encoding="utf-8")

if "from backend.app.core.execution_queue_runtime import enqueue_execution" not in orch_text:
    orch_text = orch_text.replace(
        "from backend.app.agents.agent_registry import AGENT_CATALOGUE, agent_exists, normalize_agent_id, get_agent_role, get_agent_display_name",
        "from backend.app.agents.agent_registry import AGENT_CATALOGUE, agent_exists, normalize_agent_id, get_agent_role, get_agent_display_name\nfrom backend.app.core.execution_queue_runtime import enqueue_execution",
    )

append_code = r'''

def create_delegated_execution_packets(plan: Dict[str, Any]) -> Dict[str, Any]:
    graph = plan.get("dependency_graph", [])
    tenant_id = str(plan.get("tenant_id") or "unknown")
    plan_id = str(plan.get("plan_id") or f"orch_{uuid.uuid4().hex[:16]}")
    objective = str(plan.get("objective") or "")

    packets = []

    for step in graph:
        agent_id = str(step.get("agent_id") or "")
        step_id = str(step.get("step_id") or "")

        packet = {
            "tenant_id": tenant_id,
            "project_id": plan_id,
            "agent_id": agent_id,
            "action_type": "orchestrated_agent_execution",
            "payload": {
                "orchestration_profile": ORCHESTRATION_PROFILE,
                "plan_id": plan_id,
                "step_id": step_id,
                "objective": objective,
                "agent_id": agent_id,
                "agent_name": step.get("agent_name"),
                "agent_role": step.get("agent_role"),
                "dependencies": step.get("dependencies", []),
                "delegation_mode": step.get("delegation_mode"),
                "cross_agent_context": {
                    "previous_results_required": bool(step.get("dependencies")),
                    "result_passing_enabled": True,
                    "head_agent_review_required": plan.get("owner_approval_required") is True,
                },
                "governance": {
                    "owner_approval_required": plan.get("owner_approval_required") is True,
                    "owner_approval_reason": plan.get("owner_approval_reason"),
                    "governance_bypass": False,
                    "entitlement_bypass": False,
                },
            },
            "priority": int(step.get("sequence") or 5),
            "max_retries": 3,
        }

        packets.append(packet)

    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_PROFILE,
        "plan_id": plan_id,
        "packet_count": len(packets),
        "delegated_execution_packets": packets,
        "queue_compatible": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def enqueue_orchestration_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan = create_orchestration_plan(payload)
    packet_result = create_delegated_execution_packets(plan)

    queued = []
    failed = []

    for packet in packet_result.get("delegated_execution_packets", []):
        try:
            enqueue_result = enqueue_execution(packet)
            queued.append({
                "agent_id": packet.get("agent_id"),
                "step_id": packet.get("payload", {}).get("step_id"),
                "queue_result": enqueue_result,
            })
        except Exception as exc:
            failed.append({
                "agent_id": packet.get("agent_id"),
                "step_id": packet.get("payload", {}).get("step_id"),
                "error": str(exc),
            })

    return {
        "success": len(failed) == 0,
        "orchestration_profile": ORCHESTRATION_PROFILE,
        "plan": plan,
        "packet_count": packet_result.get("packet_count", 0),
        "queued_count": len(queued),
        "failed_count": len(failed),
        "queued": queued,
        "failed": failed,
        "orchestration_queue_integration_enabled": True,
        "cross_agent_result_passing_foundation": True,
        "recovery_safe_execution_state": True,
        "provider_direct_execution_enabled": False,
        "governed_execution_required": True,
        "owner_approval_controls_preserved": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }


def orchestration_execution_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "orchestration_profile": ORCHESTRATION_PROFILE,
        "delegated_execution_packets_enabled": True,
        "orchestration_queue_integration_enabled": True,
        "cross_agent_result_passing_foundation": True,
        "orchestration_recovery_state_enabled": True,
        "parallel_safe_execution_groups_foundation": True,
        "head_agent_review_coordination_foundation": True,
        "queue_worker_compatible": True,
        "provider_direct_execution_enabled": False,
        "governed_execution_required": True,
        "owner_approval_controls_preserved": True,
        "customer_safe_response_mode": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }
'''

if "def enqueue_orchestration_plan(" not in orch_text:
    orch_text = orch_text.rstrip() + "\n" + append_code + "\n"

ORCH.write_text(orch_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

old_import = "from backend.app.core.multi_agent_orchestration_runtime import orchestration_readiness, create_orchestration_plan\n"
new_import = "from backend.app.core.multi_agent_orchestration_runtime import orchestration_readiness, create_orchestration_plan, orchestration_execution_readiness, enqueue_orchestration_plan\n"

if old_import in main_text and new_import not in main_text:
    main_text = main_text.replace(old_import, new_import)

routes = '''
@app.get("/admin/orchestration/execution-readiness")
async def admin_orchestration_execution_readiness():
    return orchestration_execution_readiness()


@app.post("/admin/orchestration/enqueue-plan")
async def admin_orchestration_enqueue_plan(payload: dict):
    return enqueue_orchestration_plan(payload)
'''

if "/admin/orchestration/execution-readiness" not in main_text:
    main_text = main_text.rstrip() + "\n\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("PRIORITY6_ORCHESTRATION_QUEUE_INTEGRATION_INSTALLED")
print(f"Orchestration backup: {orch_backup}")
print(f"Main backup: {main_backup}")
print("Routes:")
print("/admin/orchestration/execution-readiness")
print("/admin/orchestration/enqueue-plan")