import os

from backend.app.core import execution_event_runtime
from backend.app.core.execution_event_ledger import execution_event_ledger
from backend.app.runtime import durable_execution_history_evidence_runtime as evidence_runtime
from backend.app.runtime import durable_external_action_records
from backend.app.runtime import global_execution_evidence_layer
from backend.app.runtime import persistent_action_execution_history


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
evidence_runtime.reset_dev_execution_history_evidence_for_tests()

ready = evidence_runtime.ensure_execution_history_evidence_tables()
assert_true(ready["success"], "dev execution history evidence store should be ready")
assert_true(ready["storage_mode"] == "dev_memory", "dev fallback should use memory")
assert_true(ready["dev_only"] is True, "dev fallback should be marked dev_only")
assert_true(ready["not_production_durable"] is True, "dev fallback should be marked not production durable")
assert_true(ready["credential_values_exposed"] is False, "readiness must not expose credentials")

history = evidence_runtime.record_execution_history(
    tenant_id="tenant_exec_001",
    project_id="project_exec_001",
    execution_id="exec_001",
    agent_id="agent_001",
    workflow_id="workflow_001",
    orchestration_id="orch_001",
    provider_execution_id="provider_exec_001",
    queue_job_id="queue_001",
    action_type="test_action",
    status="completed",
    summary="Execution completed.",
    payload={"safe": True, "api_key": "must_not_persist"},
    completed=True,
)
assert_true(history["success"], "history record should create")
assert_true(history["history_id"], "history id should be returned")
assert_true("api_key" not in history["history"]["payload"], "history payload should be scrubbed")

listed_history = evidence_runtime.list_execution_history(tenant_id="tenant_exec_001")
assert_true(listed_history["count"] == 1, "history list should include canonical record")

event = evidence_runtime.record_execution_event(
    tenant_id="tenant_exec_001",
    project_id="project_exec_001",
    execution_id="exec_001",
    event_type="execution_completed",
    source_type="test",
    source_id="source_001",
    payload={"secret_token": "must_not_persist", "safe": True},
)
assert_true(event["success"], "execution event should create")
assert_true("secret_token" not in event["event"]["payload"], "event payload should be scrubbed")

events = evidence_runtime.list_execution_events(tenant_id="tenant_exec_001", project_id="project_exec_001")
assert_true(events["count"] == 1, "execution event list should include canonical event")

evidence = evidence_runtime.record_execution_evidence(
    tenant_id="tenant_exec_001",
    project_id="project_exec_001",
    execution_id="exec_001",
    evidence_type="client_visible_output",
    title="Client output",
    summary="Client output persisted.",
    source_type="test",
    source_id="evidence_source_001",
    status="ready",
    payload={"output": "deliverable", "password": "must_not_persist"},
)
assert_true(evidence["success"], "execution evidence should create")
assert_true("password" not in evidence["evidence"]["payload"], "evidence payload should be scrubbed")

latest = evidence_runtime.record_latest_deliverable(
    tenant_id="tenant_exec_001",
    project_id="project_exec_001",
    execution_id="exec_001",
    agent_id="agent_001",
    title="Latest deliverable",
    summary="Latest deliverable persisted.",
    deliverable_type="agent_output",
    status="ready",
    payload={"output": "deliverable", "credential": "must_not_persist"},
)
assert_true(latest["success"], "latest deliverable should create")
loaded_latest = evidence_runtime.get_latest_deliverable(
    tenant_id="tenant_exec_001",
    project_id="project_exec_001",
)
assert_true(loaded_latest["success"], "latest deliverable should load")
assert_true(loaded_latest["latest_deliverable"]["title"] == "Latest deliverable", "latest deliverable should match")
assert_true("credential" not in loaded_latest["latest_deliverable"]["payload"], "latest payload should be scrubbed")

approval_audit = evidence_runtime.record_approval_action_audit(
    tenant_id="tenant_exec_001",
    project_id="project_exec_001",
    execution_id="exec_001",
    action_id="action_001",
    action_type="owner_approval",
    decision="approved",
    actor_role="owner_admin",
    payload={"safe": True, "token": "must_not_persist"},
)
assert_true(approval_audit["success"], "approval action audit should create")
assert_true("token" not in approval_audit["audit"]["payload"], "approval audit payload should be scrubbed")

summary = evidence_runtime.get_execution_evidence_summary(tenant_id="tenant_exec_001")
assert_true(summary["success"], "execution evidence summary should load")
assert_true(summary["history_count"] >= 1, "summary should include history count")
assert_true(summary["event_count"] >= 1, "summary should include event count")
assert_true(summary["evidence_count"] >= 1, "summary should include evidence count")

wrapper_history = persistent_action_execution_history.record_action_execution(
    tenant_id="tenant_exec_002",
    packet_id="packet_001",
    assigned_agent="agent_002",
    execution_payload={
        "project_id": "project_exec_002",
        "execution_id": "exec_002",
        "execution_status": "completed",
        "completed_output": "Completed output.",
        "deliverable": {
            "deliverable_id": "deliverable_exec_002",
            "title": "Wrapper deliverable",
            "summary": "Wrapper deliverable summary.",
            "type": "wrapper_output",
        },
    },
)
assert_true(wrapper_history["history_id"], "action history wrapper should return history id")

wrapper_list = persistent_action_execution_history.list_action_execution_history(tenant_id="tenant_exec_002")
assert_true(wrapper_list["count"] >= 1, "action history wrapper should read canonical history")
assert_true(wrapper_list["canonical_runtime"] == "durable_execution_history_evidence_runtime", "history wrapper should declare canonical runtime")

external = durable_external_action_records.record_external_actions(
    tenant_id="tenant_exec_003",
    execution_id="exec_003",
    packet_id="packet_003",
    assigned_agent="agent_003",
    deliverable={
        "project_id": "project_exec_003",
        "actions_performed": [
            {
                "type": "external_publish",
                "status": "recorded",
                "record_id": "external_record_003",
            }
        ],
    },
)
assert_true(external["success"], "external action wrapper should record")
assert_true(external["persistence_mode"] == "canonical_durable_runtime", "external wrapper should prefer canonical runtime")

external_list = durable_external_action_records.list_external_action_records(tenant_id="tenant_exec_003")
assert_true(external_list["count"] >= 1, "external action wrapper should read canonical records")

runtime_event = execution_event_runtime.add_execution_event(
    tenant_id="tenant_exec_004",
    project_id="project_exec_004",
    event_type="agent_execution_completed",
    title="Agent completed",
    agent_id="agent_004",
    payload={"execution_id": "exec_004"},
)
assert_true(runtime_event["success"], "execution event runtime wrapper should write canonical event")

runtime_events = execution_event_runtime.list_execution_events(
    tenant_id="tenant_exec_004",
    project_id="project_exec_004",
)
assert_true(runtime_events["count"] >= 1, "execution event runtime wrapper should read canonical events")

ledger_event = execution_event_ledger.record(
    tenant_id="tenant_exec_005",
    project_id="project_exec_005",
    agent_id="agent_005",
    actor_role="owner_admin",
    workflow_stage="specialist_execution",
    action_type="run_agent",
    execution_action="run_agent",
    event_type="approval_gate_passed",
    event_status="approved",
    title="Approved action",
    summary="Approved action persisted.",
    approval={"status": "approved"},
    execution={"execution_id": "exec_005"},
    owner_approved=True,
)
assert_true(ledger_event["success"], "execution event ledger should write canonical event")
assert_true(execution_event_ledger.latest(tenant_id="tenant_exec_005", project_id="project_exec_005"), "ledger latest should read canonical events")

admin_packet = global_execution_evidence_layer.build_execution_evidence_packet(
    tenant_id="tenant_exec_001",
    actor_role="owner_admin",
)
assert_true(admin_packet["success"], "admin evidence packet should load")
assert_true(admin_packet["canonical_runtime"] == "durable_execution_history_evidence_runtime", "admin evidence packet should use canonical runtime")

client_packet = global_execution_evidence_layer.build_execution_evidence_packet(
    tenant_id="tenant_exec_001",
    actor_role="client",
)
assert_true(client_packet["success"], "client evidence packet should load")
assert_true(client_packet["admin_view"] is False, "client evidence packet should hide admin-only view")

evidence_runtime.reset_dev_execution_history_evidence_for_tests()
_clear_env()
os.environ["ENVIRONMENT"] = "production"
prod = evidence_runtime.ensure_execution_history_evidence_tables()
assert_true(prod["success"] is False, "production without DB should fail closed")
assert_true(prod["status"] == "execution_history_evidence_store_unavailable", "production status should be unavailable")
assert_true(prod["production_fail_closed"] is True, "production fail-closed flag should be true")
assert_true(prod["credential_values_exposed"] is False, "fail-closed response must not expose credentials")

_clear_env()
evidence_runtime.reset_dev_execution_history_evidence_for_tests()

print("DURABLE_EXECUTION_HISTORY_EVIDENCE_RUNTIME_PASSED")
