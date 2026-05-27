from backend.app.runtime.dead_letter_manual_review_runtime import (
    create_dead_letter_record,
    dead_letter_readiness,
    list_dead_letters,
    list_manual_review_queue,
    record_manual_review_decision,
)


def main():
    readiness = dead_letter_readiness()
    assert readiness["status"] == "ready"
    assert readiness["governance_preserved"] is True

    record = create_dead_letter_record(
        tenant_id="tenant_test",
        workflow_id="workflow_test",
        agent_id="marketing_specialist_agent",
        action_type="provider_execution",
        failure_reason="provider_timeout_after_retries",
        payload={"safe": True},
        retry_count=3,
        severity="high",
    )
    assert record["status"] == "dead_lettered"
    assert record["owner_review_required"] is True
    assert record["no_autonomous_spend_or_scaling"] is True

    listed = list_dead_letters(tenant_id="tenant_test")
    assert listed["count"] >= 1

    queue = list_manual_review_queue(tenant_id="tenant_test")
    assert queue["count"] >= 1
    review_id = queue["manual_review_items"][-1]["review_id"]

    blocked = record_manual_review_decision(
        review_id=review_id,
        decision="retry",
        actor_role="client",
        notes="client should not be able to approve manual recovery",
    )
    assert blocked["status"] == "blocked"

    approved = record_manual_review_decision(
        review_id=review_id,
        decision="retry",
        actor_role="owner",
        notes="safe retry approved after review",
    )
    assert approved["status"] == "ok"

    bad_decision = record_manual_review_decision(
        review_id=review_id,
        decision="scale_campaign",
        actor_role="owner",
        notes="must remain blocked by governance",
    )
    assert bad_decision["status"] == "blocked"

    print("DEAD_LETTER_MANUAL_REVIEW_RUNTIME_OK")


if __name__ == "__main__":
    main()
