
from backend.app.runtime.real_action_execution_bridge import execute_real_action_packet, execute_real_action_packets

safe_packet = {
    "packet_id": "packet_safe_001",
    "assigned_agent": "marketing specialist agent",
    "implementation_action": "Create a healthcare technology positioning strategy document for client review",
    "risk": "medium",
}

blocked_packet = {
    "packet_id": "packet_risky_001",
    "assigned_agent": "marketing specialist agent",
    "implementation_action": "Launch paid campaign and increase advertising budget",
    "risk": "high",
}

safe_result = execute_real_action_packet(safe_packet)
assert safe_result["success"] is True
assert safe_result["performed_actual_action"] is True
assert safe_result["execution_status"] == "executed_internal_action"
assert safe_result["deliverable"]["asset_status"] == "created"

blocked_result = execute_real_action_packet(blocked_packet, owner_approved=False)
assert blocked_result["success"] is False
assert blocked_result["performed_actual_action"] is False
assert blocked_result["execution_status"] == "blocked_owner_approval_required"

approved_result = execute_real_action_packet(blocked_packet, owner_approved=True)
assert approved_result["success"] is True
assert approved_result["performed_actual_action"] is True

batch = execute_real_action_packets([safe_packet, blocked_packet], owner_approved=False)
assert batch["total_packets"] == 2
assert batch["executed_count"] == 1
assert batch["blocked_count"] == 1

print("REAL_ACTION_EXECUTION_BRIDGE_TEST_PASSED")
