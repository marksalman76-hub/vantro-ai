import os
import tempfile

os.environ["ADMIN_INDUSTRY_STORE_DIR"] = tempfile.mkdtemp(prefix="industry_store_test_")

from backend.app.core.admin_industry_agent_store_learning_vault import (
    create_or_update_industry_pack,
    list_industry_packs,
    capture_tenant_safe_learning,
    list_learning_vault,
    admin_industry_learning_vault_status,
)


def assert_true(value, message):
    if not value:
        raise AssertionError(message)


pack = create_or_update_industry_pack({
    "industry": "Real Estate",
    "display_name": "Real Estate Growth Pack",
    "description": "Reusable agent deployment pack for property businesses.",
    "agents": [
        {"agent_id": "lead_generator_appointment_setter_agent", "role": "Buyer/seller lead flow"},
        {"agent_id": "social_media_manager_content_creator_agent", "role": "Listing content"},
    ],
    "recommended_integrations": ["crm", "calendar", "email"],
    "deployment_checklist": ["Connect CRM", "Load brand profile", "Confirm approval rules"],
})
assert_true(pack["success"], "industry pack should save")
assert_true(pack["pack"]["tenant_safe"] is True, "industry pack must be tenant-safe")

packs = list_industry_packs(industry="real_estate")
assert_true(packs["count"] == 1, "industry pack should be queryable")

capture = capture_tenant_safe_learning({
    "industry": "Real Estate",
    "agent_id": "lead_generator_appointment_setter_agent",
    "client_type": "Growth",
    "quality_score": 91,
    "approved_by_client": True,
    "tenant_safe_summary": "Short local-market lead magnet offers worked best.",
    "successful_patterns": ["Local suburb-specific seller valuation hooks"],
    "failed_patterns": ["Generic national property copy"],
    "recommended_improvements": ["Use location specificity and appointment-led CTA"],
    "raw_output": "PRIVATE CLIENT OUTPUT SHOULD NOT BE STORED",
    "customer_email": "private@example.com",
    "metadata": {"safe_segment": "property", "api_key": "SHOULD_NOT_STORE"},
})
assert_true(capture["success"], "learning capture should succeed")
assert_true(capture["raw_private_data_stored"] is False, "raw private data must not be stored")
record = capture["record"]
assert_true("raw_output" not in record, "raw output must not be present")
assert_true("customer_email" not in record, "customer email must not be present")
assert_true("api_key" not in record.get("safe_metadata", {}), "api key must not be present")

records = list_learning_vault(industry="real_estate", agent_id="lead_generator_appointment_setter_agent")
assert_true(records["count"] == 1, "learning record should be queryable")

status = admin_industry_learning_vault_status()
assert_true(status["admin_industry_agent_store_ready"] is True, "industry store status ready")
assert_true(status["tenant_safe_learning_vault_ready"] is True, "learning vault status ready")
assert_true(status["future_deployment_reuse_ready"] is True, "future deployment reuse ready")

print("ADMIN_INDUSTRY_AGENT_STORE_LEARNING_VAULT_TEST_PASSED")
