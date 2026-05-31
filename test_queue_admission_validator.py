from backend.app.runtime.queue_admission_validator import (
    QueueAdmissionRequest,
    evaluate_queue_admission,
    queue_admission_changes_live_runtime,
    queue_admission_enqueues_jobs,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    client_ok = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="tenant_1",
            agent_key="seo_agent",
            actor_role="client",
            client_has_entitlement=True,
            customer_safe=True,
        )
    )
    assert_equal(client_ok.admitted, True, "entitled client admitted")
    assert_equal(client_ok.queue_target, "client_agent_execution_queue", "client queue target")

    client_no_entitlement = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="tenant_1",
            agent_key="seo_agent",
            actor_role="client",
            client_has_entitlement=False,
        )
    )
    assert_equal(client_no_entitlement.admitted, False, "client no entitlement blocked")
    if "client_entitlement_missing" not in client_no_entitlement.blocked_reasons:
        raise AssertionError("Missing entitlement block reason")

    provider_no_approval = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="openai_live_generation",
            tenant_id="tenant_1",
            agent_key="product_image_agent",
            actor_role="client",
            client_has_entitlement=True,
            live_external_requested=True,
            live_external_enabled=True,
            owner_approved=False,
        )
    )
    assert_equal(provider_no_approval.admitted, False, "provider no approval blocked")
    if "owner_approval_required" not in provider_no_approval.blocked_reasons:
        raise AssertionError("Missing owner approval block")

    provider_approved = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="openai_live_generation",
            tenant_id="tenant_1",
            agent_key="product_image_agent",
            actor_role="client",
            client_has_entitlement=True,
            live_external_requested=True,
            live_external_enabled=True,
            owner_approved=True,
        )
    )
    assert_equal(provider_approved.admitted, True, "approved provider admitted")
    assert_equal(provider_approved.live_external_allowed, True, "approved live external allowed")
    assert_equal(provider_approved.queue_target, "provider_generation_queue", "provider queue target")

    owner_admin = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="admin_audit",
            actor_role="owner_admin",
            client_has_entitlement=False,
            customer_safe=True,
        )
    )
    assert_equal(owner_admin.admitted, True, "owner admin bypasses client entitlement")
    if "client_entitlement_bypass_allowed_for_owner_admin" not in owner_admin.reasons:
        raise AssertionError("Owner/admin bypass reason missing")

    unsafe = evaluate_queue_admission(
        QueueAdmissionRequest(
            action_type="run_agent",
            tenant_id="tenant_1",
            actor_role="client",
            client_has_entitlement=True,
            customer_safe=False,
        )
    )
    assert_equal(unsafe.admitted, False, "customer unsafe blocked")
    if "customer_safe_false" not in unsafe.blocked_reasons:
        raise AssertionError("Missing customer safety block")

    assert_equal(queue_admission_changes_live_runtime(), False, "live runtime unchanged")
    assert_equal(queue_admission_enqueues_jobs(), False, "does not enqueue jobs")

    print("QUEUE_ADMISSION_VALIDATOR_TEST_PASSED")


if __name__ == "__main__":
    main()
