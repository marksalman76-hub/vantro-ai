from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.runtime.governed_activation_persistence import persist_activation_packet

client = TestClient(app)

tenant_id = "test-run-agent-runtime-entitlement-regression-001"


def call_run_agent(actor_role: str, agent: str):
    return client.post(
        "/run-agent",
        json={
            "tenant_id": tenant_id,
            "project_id": "test-project-runtime-entitlement",
            "actor_role": actor_role,
            "requested_agent": agent,
            "task": "Create a concise test output for regression validation.",
            "workflow_stage": "test",
            "action_type": "draft_only",
            "owner_approved": True,
            "requested_credits": 0,
            "region": "AU",
            "language": "en-AU",
            "currency": "AUD",
        },
    )


owner = call_run_agent("owner", "head_agent")
assert owner.status_code == 200
owner_json = owner.json()
assert owner_json.get("success") is not False or owner_json.get("error") != "runtime_entitlement_denied"

missing_activation = call_run_agent("client", "seo_agent")
assert missing_activation.status_code == 200
missing_activation_json = missing_activation.json()
assert missing_activation_json["success"] is False
assert missing_activation_json["status"] == "runtime_entitlement_blocked"
assert missing_activation_json["error"] == "activation_state_not_found"

seed = persist_activation_packet(
    {
        "tenant_id": tenant_id,
        "package_id": "business",
        "selected_agents": ["seo_agent"],
    },
    actor_role="system",
)
assert seed["success"] is True

approved = call_run_agent("client", "seo_agent")
assert approved.status_code == 200
approved_json = approved.json()
assert approved_json.get("status") != "runtime_entitlement_blocked"
assert approved_json.get("error") != "activation_state_not_found"

blocked = call_run_agent("client", "head_agent")
assert blocked.status_code == 200
blocked_json = blocked.json()
assert blocked_json["success"] is False
assert blocked_json["status"] == "runtime_entitlement_blocked"
assert blocked_json["error"] == "requested_agent_not_activated"
assert blocked_json["next_stage"] == "owner_admin_review_required"
assert blocked_json["credential_values_exposed"] is False
assert blocked_json["customer_safe"] is True

print("RUN_AGENT_RUNTIME_ENTITLEMENT_REGRESSION_TESTS_PASSED")
print("owner_status", owner_json.get("status") or owner_json.get("workflow_status") or owner_json.get("error"))
print("missing_activation_error", missing_activation_json["error"])
print("seed_status", seed["status"])
print("approved_status", approved_json.get("status") or approved_json.get("workflow_status") or approved_json.get("error"))
print("blocked_error", blocked_json["error"])