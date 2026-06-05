import os
import tempfile

os.environ["REFUND_LEDGER_DIR"] = tempfile.mkdtemp(prefix="refund_ledger_test_")

from backend.app.core.governed_refund_runtime import (
    submit_refund_request,
    list_refund_requests,
    decide_refund_request,
    execute_stripe_refund,
)


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


unused = submit_refund_request({
    "tenant_id": "tenant_unused",
    "customer_email": "unused@example.com",
    "requested_amount_cents": 9900,
    "reason": "changed_mind_before_use",
    "usage_evidence": {
        "account_activated": False,
        "agent_executed": False,
        "credits_consumed": 0,
        "deliverables_generated": 0,
        "assets_generated": 0,
        "integration_execution_used": False,
    },
})
assert_true(unused["success"] is True, "unused refund request should submit")
assert_true(unused["status"] == "pending_owner_review", "unused account should be reviewable")

approved = decide_refund_request({
    "refund_id": unused["refund_id"],
    "decision": "approve",
    "approved_by": "owner_admin",
    "note": "Approved because system was not activated or used.",
})
assert_true(approved["success"] is True, "unused refund should approve")
assert_true(approved["status"] == "owner_approved_pending_stripe_refund", "approved refund should wait for Stripe execution")

executed = execute_stripe_refund({
    "refund_id": unused["refund_id"],
    "actor": "owner_admin",
    "amount_cents": 9900,
})
assert_true(executed["success"] is True, "approved unused refund should execute or simulate")
assert_true(executed["status"] == "refund_completed", "refund should complete")

used = submit_refund_request({
    "tenant_id": "tenant_used",
    "customer_email": "used@example.com",
    "requested_amount_cents": 9900,
    "reason": "refund_after_use",
    "usage_evidence": {
        "account_activated": True,
        "agent_executed": True,
        "credits_consumed": 1,
        "deliverables_generated": 1,
    },
})
assert_true(used["status"] == "refund_ineligible_platform_used", "used account must be refund-ineligible")

blocked = decide_refund_request({
    "refund_id": used["refund_id"],
    "decision": "approve",
    "approved_by": "owner_admin",
})
assert_true(blocked["success"] is False, "used account refund approval must be blocked")
assert_true(blocked["error"] == "refund_ineligible_platform_used", "used account must return policy error")

listed = list_refund_requests()
assert_true(listed["count"] >= 2, "ledger should list refund records")

print("GOVERNED_REFUND_WORKFLOW_TEST_PASSED")
