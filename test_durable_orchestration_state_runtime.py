import os

from backend.app.runtime import durable_orchestration_state_runtime as orchestration
from backend.app.runtime import persistent_workflow_runtime as workflow


def _clear_env():
    for key in (
        "DATABASE_URL",
        "POSTGRES_URL",
        "ENVIRONMENT",
        "APP_ENV",
        "FASTAPI_ENV",
        "NODE_ENV",
        "RENDER",
        "VERCEL_ENV",
        "PRODUCTION",
    ):
        os.environ.pop(key, None)


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


_clear_env()
orchestration.reset_dev_orchestration_state_for_tests()

ready = orchestration.ensure_orchestration_tables()
assert_true(ready["success"], "dev fallback should be available")
assert_true(ready["storage_mode"] == "dev_memory", "dev fallback should use dev memory")
assert_true(ready["dev_only"] is True, "dev fallback should be marked dev_only")
assert_true(ready["not_production_durable"] is True, "dev fallback should be marked not production durable")

plan = orchestration.create_orchestration_plan(
    orchestration_id="orch_test_001",
    tenant_id="tenant_001",
    project_id="project_001",
    root_agent_id="head_agent",
    status="planned",
    plan_type="test_plan",
    payload={"objective": "test durable orchestration"},
)
assert_true(plan["success"], "create orchestration plan should succeed")
assert_true(plan["orchestration_id"] == "orch_test_001", "plan id should round trip")

step_one = orchestration.create_orchestration_step(
    step_id="step_001",
    orchestration_id="orch_test_001",
    tenant_id="tenant_001",
    agent_id="agent_a",
    action_type="draft",
    status="pending",
)
assert_true(step_one["success"], "first step should persist")

step_two = orchestration.create_orchestration_step(
    step_id="step_002",
    orchestration_id="orch_test_001",
    tenant_id="tenant_001",
    agent_id="agent_b",
    action_type="review",
    status="pending",
    dependency_step_ids=["step_001"],
)
assert_true(step_two["success"], "dependent step should persist")
assert_true(step_two["step"]["dependency_step_ids"] == ["step_001"], "dependency ids should persist")

updated = orchestration.update_orchestration_step_status(
    step_id="step_001",
    orchestration_id="orch_test_001",
    tenant_id="tenant_001",
    status="completed",
)
assert_true(updated["success"], "step update should succeed")
assert_true(updated["step"]["status"] == "completed", "step should be completed")

event = orchestration.record_orchestration_event(
    orchestration_id="orch_test_001",
    step_id="step_001",
    tenant_id="tenant_001",
    event_type="test_event",
    payload={"ok": True},
)
assert_true(event["success"], "event should persist")

memory = orchestration.record_orchestration_result_memory(
    orchestration_id="orch_test_001",
    step_id="step_001",
    tenant_id="tenant_001",
    agent_id="agent_a",
    result_type="test_result",
    result_summary="summary",
    payload={"answer": 42},
)
assert_true(memory["success"], "result memory should persist")

checkpoint = orchestration.create_recovery_checkpoint(
    orchestration_id="orch_test_001",
    tenant_id="tenant_001",
    checkpoint_type="test_checkpoint",
    recoverable_status="recoverable",
    payload={"resume": "step_002"},
)
assert_true(checkpoint["success"], "recovery checkpoint should persist")

context = orchestration.get_orchestration_context("orch_test_001")
assert_true(context["success"], "context should load")
assert_true(context["result_memory_count"] >= 1, "context should include result memory")
assert_true(context["recovery_checkpoint_count"] >= 1, "context should include recovery checkpoints")

recovery = orchestration.get_orchestration_recovery_packet("orch_test_001")
assert_true(recovery["success"], "recovery packet should load")
assert_true("step_001" in recovery["completed_steps"], "recovery should list completed step")

status = orchestration.get_orchestration_status("orch_test_001")
assert_true(status["success"], "status should load")
assert_true(status["step_count"] == 2, "status should count steps")

events = orchestration.list_orchestration_events(orchestration_id="orch_test_001")
assert_true(events["success"], "events should list")
assert_true(events["count"] >= 1, "events should include at least one event")

workflow_result = workflow.create_workflow(
    workflow_id="workflow_test_001",
    workflow_type="safe_test_workflow",
    payload={"task": "compatibility"},
    tenant_id="tenant_001",
)
assert_true(workflow_result["success"], "workflow compatibility wrapper should create")
assert_true(workflow_result["workflow_id"] == "workflow_test_001", "workflow id should round trip")

_clear_env()
orchestration.reset_dev_orchestration_state_for_tests()
os.environ["ENVIRONMENT"] = "production"
prod_status = orchestration.ensure_orchestration_tables()
assert_true(prod_status["success"] is False, "production without DB should fail closed")
assert_true(prod_status["status"] == "orchestration_store_unavailable", "production status should be unavailable")
assert_true(prod_status["production_fail_closed"] is True, "production fail-closed flag should be true")
assert_true(prod_status["credential_values_exposed"] is False, "fail-closed response must not expose credentials")

_clear_env()
orchestration.reset_dev_orchestration_state_for_tests()

print("DURABLE_ORCHESTRATION_STATE_RUNTIME_PASSED")
