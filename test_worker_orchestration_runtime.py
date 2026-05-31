from backend.app.runtime.queue_adapter import InMemoryQueueAdapter
from backend.app.runtime.worker_orchestration_runtime import (
    WorkerPlanRequest,
    build_worker_plan,
    export_worker_plan,
    worker_orchestration_executes_jobs,
    worker_orchestration_changes_live_routes,
    worker_orchestration_requires_redis,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    adapter = InMemoryQueueAdapter()

    client_plan = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="run_agent",
                tenant_id="tenant_1",
                agent_key="seo_agent",
                actor_role="client",
                client_has_entitlement=True,
                payload={"prompt": "test"},
            ),
            adapter=adapter,
        )
    )

    assert_equal(client_plan["admitted"], True, "client admitted")
    assert_equal(client_plan["queue_target"], "client_agent_execution_queue", "client queue")
    assert_equal(client_plan["planned_only"], True, "planned only")
    assert_equal(client_plan["would_enqueue"], True, "would enqueue")
    assert_equal(client_plan["would_execute_now"], False, "does not execute now")
    assert_equal(client_plan["governance"]["jobs_executed"], False, "jobs not executed")

    blocked_provider = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="openai_live_generation",
                tenant_id="tenant_1",
                agent_key="product_image_agent",
                actor_role="client",
                client_has_entitlement=True,
                live_external_requested=True,
                live_external_enabled=False,
                owner_approved=False,
            ),
            adapter=adapter,
        )
    )

    assert_equal(blocked_provider["admitted"], False, "blocked provider")
    if "owner_approval_required" not in blocked_provider["blocked_reasons"]:
        raise AssertionError("Missing owner approval block")
    if "live_external_execution_disabled" not in blocked_provider["blocked_reasons"]:
        raise AssertionError("Missing live external disabled block")

    approved_provider = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="openai_live_generation",
                tenant_id="tenant_1",
                agent_key="product_image_agent",
                actor_role="client",
                client_has_entitlement=True,
                live_external_requested=True,
                live_external_enabled=True,
                owner_approved=True,
            ),
            adapter=adapter,
        )
    )

    assert_equal(approved_provider["admitted"], True, "approved provider")
    assert_equal(approved_provider["queue_target"], "provider_generation_queue", "provider queue")
    assert_equal(approved_provider["governance"]["live_external_allowed"], True, "live external allowed after approval")
    assert_equal(approved_provider["would_execute_now"], False, "approved still does not execute now")

    owner_admin_plan = export_worker_plan(
        build_worker_plan(
            WorkerPlanRequest(
                action_type="admin_audit",
                actor_role="owner_admin",
                client_has_entitlement=False,
            ),
            adapter=adapter,
        )
    )

    assert_equal(owner_admin_plan["admitted"], True, "owner admin admitted")
    assert_equal(owner_admin_plan["queue_target"], "admin_internal_queue", "admin queue")
    if "client_entitlement_bypass_allowed_for_owner_admin" not in owner_admin_plan["reasons"]:
        raise AssertionError("Missing owner/admin bypass reason")

    assert_equal(worker_orchestration_executes_jobs(), False, "worker does not execute")
    assert_equal(worker_orchestration_changes_live_routes(), False, "routes unchanged")
    assert_equal(worker_orchestration_requires_redis(), False, "redis not required")

    print("WORKER_ORCHESTRATION_RUNTIME_TEST_PASSED")


if __name__ == "__main__":
    main()
