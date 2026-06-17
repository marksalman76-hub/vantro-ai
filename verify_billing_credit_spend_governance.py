from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent


REQUIRED_TRUE_FIELDS = [
    "billing_credit_governance_attempted",
    "billing_credit_governance_passed",
    "package_entitlement_required",
    "credit_reserve_before_execution_passed",
    "provider_cost_cap_blocked_without_approval",
    "owner_override_audited",
    "credit_finalize_after_success_represented",
    "credit_reversal_after_failure_represented",
    "refund_or_reconciliation_shape_present",
    "client_billing_view_redacted",
    "admin_billing_diagnostics_redacted",
]

REQUIRED_FALSE_FIELDS = [
    "stripe_live_charge_attempted",
    "provider_call_attempted",
    "media_generation_attempted",
    "real_customer_billing_mutation_attempted",
    "real_customer_credit_mutation_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "render_removal_attempted",
]

FORBIDDEN_VALUES = [
    "STRIPE_SECRET_SHOULD_NOT_LEAK",
    "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    "RUNWAY_SECRET_SHOULD_NOT_LEAK",
    "ELEVEN_SECRET_SHOULD_NOT_LEAK",
    "DATABASE_SECRET_SHOULD_NOT_LEAK",
    "QUEUE_SECRET_SHOULD_NOT_LEAK",
    "123456789012",
    "arn:aws:secretsmanager",
    "postgres://",
    "sk_live_",
    "sk_test_",
    "pk_live_",
    "card_number",
    "424242424242",
    "https://sqs.",
]

SIDE_EFFECT_KEYS = {
    "stripe_live_charge_attempted",
    "stripe_call_attempted",
    "provider_call_attempted",
    "media_generation_attempted",
    "real_customer_billing_mutation_attempted",
    "real_customer_credit_mutation_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "render_removal_attempted",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "aws_call_attempted",
    "rds_write_attempted",
    "queue_mutation_attempted",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AssertionError(f"Could not load module: {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def assert_no_side_effects(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SIDE_EFFECT_KEYS:
                require(item is False, f"{label} attempted side effect: {key}")
            assert_no_side_effects(item, label)
    elif isinstance(value, list):
        for item in value:
            assert_no_side_effects(item, label)


def assert_client_safe(client_view: dict) -> None:
    require(client_view.get("customer_safe") is True, "Client billing view must be customer safe.")
    safe_boolean_keys = {
        "credential_values_exposed",
        "provider_secret_values_visible",
        "internal_config_exposed",
    }
    text = str({key: value for key, value in client_view.items() if key not in safe_boolean_keys}).lower()
    for forbidden in [
        "provider_estimated_cost",
        "provider_actual_cost",
        "provider_class",
        "provider_name",
        "stripe_reference",
        "package_entitlement_reference",
        "final_27_agent_validation",
        "audit",
        "credential",
        "secret",
        "internal_config",
    ]:
        require(forbidden not in text, f"Client billing view exposed internal marker: {forbidden}")
    assert_no_forbidden_values(client_view, "client billing view")


def main() -> int:
    governance = load_module(
        "backend/app/runtime/billing_credit_spend_governance.py",
        "billing_credit_spend_governance_under_test",
    )
    source = read("backend/app/runtime/billing_credit_spend_governance.py")
    ledger_source = read("backend/app/runtime/billing_credit_ledger_boundary.py")
    entitlement_source = read("backend/app/runtime/api_acceptance_entitlement_boundary.py")
    frontend_source = read("frontend/src/lib/packageCreditEnforcement.ts")
    main_source = read("backend/app/main.py")
    master_plan = read("PRODUCTION_COMPLETION_MASTER_PLAN.md")
    audit_plan = read("PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for source_name, text in {
        "billing governance": source,
        "billing ledger": ledger_source,
        "entitlement boundary": entitlement_source,
    }.items():
        for marker in [
            "import stripe",
            "stripe.",
            "requests.",
            "httpx.",
            "boto3",
            ".connect(",
            ".execute(",
            ".send_message(",
            ".put_object(",
            "runway.",
            "elevenlabs.",
            "kling.",
            "openai.",
            "charge.create",
            "checkout.Session.create",
            "PaymentIntent.create",
            "reserve_credit(",
            "finalize_credit(",
            "refund(",
        ]:
            require(marker not in text, f"{source_name} must not contain live billing/provider marker: {marker}")

    for marker in [
        "real_stripe_checkout_session_bridge_v2",
        "stripe.checkout.Session.create",
        "stripe_live_required",
    ]:
        require(marker in main_source, f"Existing Stripe route marker should remain inspectable but not invoked by verifier: {marker}")

    proof = governance.build_billing_credit_spend_governance_proof({
        "stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK",
        "provider_api_key": "PROVIDER_SECRET_SHOULD_NOT_LEAK",
        "stripe_event_id": "evt_test_raw_should_hash",
        "checkout_session_id": "cs_test_raw_should_hash",
        "invoice_id": "in_test_raw_should_hash",
    })

    for field in REQUIRED_TRUE_FIELDS:
        require(proof.get(field) is True, f"Required proof field must be true: {field}")
    for field in REQUIRED_FALSE_FIELDS:
        require(proof.get(field) is False, f"Required proof field must be false: {field}")

    entitlement = proof["entitlement_decision"]
    require(entitlement["allowed"] is False, "Missing entitlement fixture must block client execution.")
    require("package_entitlement_not_active" in entitlement["denial_reasons"], "Entitlement denial must be package based.")

    reservation = proof["provider_cost_estimate_event"]
    require(reservation["event_type"] == "provider_cost_estimate_recorded", "Provider estimate event must be represented.")
    require(reservation["provider_estimated_cost"] > 0, "Provider estimate event must preserve redacted cost value.")

    cost_gate = proof["provider_cost_cap_decision"]
    require(cost_gate["provider_cost_cap_exceeded"] is True, "High-cost fixture must exceed cap.")
    require(cost_gate["provider_cost_cap_blocked_without_approval"] is True, "High-cost fixture must be blocked without owner approval.")
    require(cost_gate["provider_execution_allowed_after_cost_gate"] is False, "Cost gate must block provider-eligible execution.")

    owner_override = proof["owner_override_decision"]
    require(owner_override["owner_override_allowed"] is True, "Owner-approved override fixture must be allowed at governance layer.")
    require(proof["owner_override_audit"]["event_type"] == "admin_override_recorded", "Owner override must produce audit event.")
    require(proof["owner_override_audit"]["status"] == "admin_override_audit_only", "Owner override must be audit-only.")

    require(proof["credit_finalization_event"]["event_type"] == "credit_finalized_placeholder", "Credit finalization shape missing.")
    require(proof["credit_reversal_event"]["event_type"] == "credit_reversed_placeholder", "Credit reversal shape missing.")
    require(proof["refund_event"]["event_type"] == "credit_refunded_placeholder", "Refund shape missing.")
    require(proof["stripe_test_reconciliation"]["mode"] == "test_fixture_only", "Stripe proof must be test fixture only.")
    require(proof["stripe_test_reconciliation"]["mock_webhook_reconciliation_represented"] is True, "Mock Stripe reconciliation missing.")
    require(proof["stripe_test_reconciliation"]["stripe_live_charge_attempted"] is False, "Stripe live charge must stay false.")
    require(proof["stripe_test_reconciliation"]["stripe_api_call_attempted"] is False, "Stripe API call must stay false.")

    assert_client_safe(proof["client_billing_view"])
    require(proof["admin_billing_diagnostics"]["credential_values_exposed"] is False, "Admin billing diagnostics must be redacted.")
    require(proof["admin_billing_diagnostics"]["provider_secret_values_visible"] is False, "Admin billing diagnostics must hide provider secrets.")
    require(proof["reservation_validation"]["valid"] is True, f"Reservation ledger validation failed: {proof['reservation_validation']}")
    require(proof["allowed_decision_validation"]["valid"] is True, f"Allowed decision validation failed: {proof['allowed_decision_validation']}")

    assert_no_side_effects(proof, "billing governance proof")
    assert_no_forbidden_values(proof, "billing governance proof")

    for marker in [
        "BILLING_CREDIT_SPEND_GOVERNANCE_VERSION",
        "evaluate_provider_cost_cap",
        "build_mock_stripe_test_reconciliation_shape",
        "build_billing_credit_spend_governance_proof",
        "provider_cost_cap_blocked_without_approval",
        "stripe_live_charge_attempted",
    ]:
        require(marker in source, f"Billing governance source missing marker: {marker}")

    for marker in [
        "package_credit_enforcement_enabled",
        "owner_admin_bypass",
        "consumeExecutionCredit",
        "backend_execution_decision_authority",
    ]:
        require(marker in frontend_source, f"Frontend package/credit enforcement marker missing: {marker}")

    for marker in [
        "Billing credit spend governance proof",
        "billing_credit_governance_passed=true",
        "provider_cost_cap_blocked_without_approval=true",
        "stripe_live_charge_attempted=false",
    ]:
        require(
            marker in master_plan or marker in audit_plan or marker in matrix,
            f"Production docs missing billing governance marker: {marker}",
        )

    proof_summary = {
        field: proof.get(field)
        for field in [*REQUIRED_TRUE_FIELDS, *REQUIRED_FALSE_FIELDS]
    }
    proof_summary.update({
        "stripe_test_or_mock_reconciliation_represented": proof.get("stripe_test_or_mock_reconciliation_represented"),
        "synthetic_job_reference_hash": proof.get("synthetic_job_reference_hash"),
        "synthetic_tenant_reference_hash": proof.get("synthetic_tenant_reference_hash"),
        "credential_values_exposed": proof.get("credential_values_exposed"),
        "provider_secret_values_visible": proof.get("provider_secret_values_visible"),
    })
    print("BILLING_CREDIT_SPEND_GOVERNANCE_PROOF:")
    print(json.dumps(proof_summary, indent=2, sort_keys=True))
    print("BILLING_CREDIT_SPEND_GOVERNANCE_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
