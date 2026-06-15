from __future__ import annotations

from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parent


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


def assert_no_mutation(entry: dict) -> None:
    require(entry["mutation_mode"] == "no_mutation_placeholder", "Ledger entry must stay in no-mutation placeholder mode.")
    for key in [
        "billing_mutation_attempted",
        "stripe_call_attempted",
        "provider_call_attempted",
        "aws_call_attempted",
        "credit_mutation_attempted",
        "rds_write_attempted",
        "queue_mutation_attempted",
    ]:
        require(entry[key] is False, f"Ledger boundary must not mutate/call external systems: {key}")


def main() -> int:
    ledger = load_module(
        "backend/app/runtime/billing_credit_ledger_boundary.py",
        "billing_credit_ledger_boundary_under_test",
    )
    enforcement = load_module(
        "backend/app/runtime/api_acceptance_entitlement_boundary.py",
        "api_acceptance_entitlement_boundary_for_ledger_test",
    )
    acceptance = load_module(
        "backend/app/runtime/api_job_acceptance_boundary.py",
        "api_job_acceptance_boundary_for_ledger_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_ledger_test",
    )

    source = read("backend/app/runtime/billing_credit_ledger_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "import stripe",
        "stripe.",
        "boto3",
        "requests.",
        "httpx.",
        "send_message",
        "put_object",
        "provider.execute",
        "INSERT INTO",
        "UPDATE ",
        "reserve_credit(",
        "finalize_credit(",
        "refund(",
    ]:
        require(marker not in source, f"AWS-12 boundary must not contain live billing/provider/AWS marker: {marker}")

    expected_event_types = {
        "credit_reservation_requested",
        "credit_reserved_placeholder",
        "credit_reservation_denied",
        "credit_finalization_requested",
        "credit_finalized_placeholder",
        "credit_refund_requested",
        "credit_refunded_placeholder",
        "credit_reversal_requested",
        "credit_reversed_placeholder",
        "admin_override_recorded",
        "provider_cost_estimate_recorded",
        "provider_actual_cost_recorded",
        "billing_audit_event_recorded",
    }
    require(expected_event_types == set(ledger.LEDGER_EVENT_TYPES), "AWS-12 must define the full canonical ledger event set.")

    client_payload = {
        "actor_role": "client",
        "package_name": "business",
        "entitlement_status": "active",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "job_id": "job_billing_aws12_media",
        "customer_id": "client_123",
        "account_id": "account_123",
        "selected_agent": "marketing_specialist_agent",
        "selected_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "agent_ids": ["marketing_specialist_agent", "ugc_media_agent"],
        "active_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "media_type": "complete_video",
        "asset_type": "final_mp4",
        "video_provider": "future_video_provider",
        "duration_seconds": 25,
        "segment_count": 5,
        "provider_cost_weight": 1,
        "quality_cost_weight": 1,
        "provider_estimated_cost": 12.5,
        "approval_status": "owner_approved",
        "credit_reservation_status": "reserved",
        "correlation_id": "corr_billing_aws12",
        "stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK",
        "provider_api_key": "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    }
    decision = enforcement.build_api_acceptance_entitlement_decision(client_payload)
    require(decision["allowed"] is True, f"Client payload should be allowed by AWS-11 decision: {decision}")
    reservation = ledger.build_credit_reservation_placeholder(decision, envelope=client_payload)
    require(reservation["event_type"] == "credit_reserved_placeholder", "Allowed client decision should produce reservation placeholder.")
    require(reservation["job_id"] == "job_billing_aws12_media", "Ledger entry must preserve job_id.")
    require(reservation["customer_id"] == "client_123", "Ledger entry must preserve customer reference.")
    require(reservation["actor_role"] == "client", "Ledger entry must preserve client actor role.")
    require(reservation["authority_level"] == "client_package_credit_governed", "Ledger entry must preserve client authority.")
    require(reservation["package_name"] == "business", "Ledger entry must preserve package.")
    require(reservation["selected_agents"] == ["marketing_specialist_agent", "ugc_media_agent"], "Ledger entry must preserve selected agents.")
    require(reservation["final_27_agent_validation"]["valid"] is True, "Ledger entry must include final 27 validation.")
    require(reservation["task_type"] == "media_generation", "Ledger entry must preserve task type.")
    require(reservation["workflow_type"] == "universal_complete_media", "Ledger entry must preserve workflow type.")
    require(reservation["provider_class"] == "video_generation_providers", "Ledger should record provider class placeholder.")
    require(reservation["provider_name"] == "future_video_provider", "Ledger should record provider name placeholder.")
    require(reservation["estimated_credit_cost"] > 0, "Ledger must estimate credit cost from duration/provider factors.")
    require(reservation["reserved_credit_amount"] == reservation["estimated_credit_cost"], "Reservation placeholder should mirror estimated credits.")
    require(reservation["provider_estimated_cost"] == 12.5, "Admin diagnostics can preserve provider estimated cost placeholder.")
    require(reservation["stripe_reference"] == "stripe_reference_placeholder", "Ledger must include Stripe reference placeholder.")
    require(reservation["package_entitlement_reference"] == "package_entitlement_reference_placeholder", "Ledger must include package entitlement placeholder.")
    require(reservation["audit"]["correlation_id"] == "corr_billing_aws12", "Ledger must preserve audit/correlation evidence.")
    assert_no_mutation(reservation)
    require("STRIPE_SECRET_SHOULD_NOT_LEAK" not in str(reservation), "Ledger entry must redact Stripe secrets.")
    require("PROVIDER_SECRET_SHOULD_NOT_LEAK" not in str(reservation), "Ledger entry must redact provider secrets.")

    finalization = ledger.build_credit_finalization_placeholder({
        **client_payload,
        "actual_credit_cost": 9,
        "provider_actual_cost": 8.75,
    })
    refund = ledger.build_credit_refund_placeholder({**client_payload, "refund_credit_amount": 3})
    reversal = ledger.build_credit_reversal_placeholder({**client_payload, "reversal_credit_amount": 4})
    admin_override = ledger.build_admin_override_placeholder({
        **client_payload,
        "actor_role": "owner",
        "selected_agent": "head_agent",
        "selected_agents": ["head_agent"],
        "agent_ids": ["head_agent"],
        "admin_override_reason": "support_recovery",
    })
    estimate_event = ledger.build_provider_cost_estimate_placeholder({**client_payload, "provider_estimated_cost": 21.25})
    actual_event = ledger.build_provider_actual_cost_placeholder({**client_payload, "provider_actual_cost": 19.5})
    audit_event = ledger.build_billing_audit_event_placeholder(client_payload)

    require(finalization["event_type"] == "credit_finalized_placeholder", "Finalization placeholder missing.")
    require(finalization["finalized_credit_amount"] == 9, "Finalization placeholder must preserve finalized amount.")
    require(refund["event_type"] == "credit_refunded_placeholder", "Refund placeholder missing.")
    require(refund["refunded_credit_amount"] == 3, "Refund placeholder must preserve refund amount.")
    require(reversal["event_type"] == "credit_reversed_placeholder", "Reversal placeholder missing.")
    require(reversal["reversed_credit_amount"] == 4, "Reversal placeholder must preserve reversal amount.")
    require(admin_override["event_type"] == "admin_override_recorded", "Admin override placeholder missing.")
    require(admin_override["status"] == "admin_override_audit_only", "Admin override must be audit-only.")
    require(estimate_event["event_type"] == "provider_cost_estimate_recorded", "Provider estimate placeholder missing.")
    require(actual_event["event_type"] == "provider_actual_cost_recorded", "Provider actual cost placeholder missing.")
    require(audit_event["event_type"] == "billing_audit_event_recorded", "Billing audit placeholder missing.")
    for entry in [finalization, refund, reversal, admin_override, estimate_event, actual_event, audit_event]:
        assert_no_mutation(entry)

    internal_decision = enforcement.build_api_acceptance_entitlement_decision({
        **client_payload,
        "selected_agent": "orchestration_agent",
        "selected_agents": ["orchestration_agent"],
        "agent_ids": ["orchestration_agent"],
        "active_agents": ["orchestration_agent"],
    })
    denied_reservation = ledger.build_credit_reservation_placeholder(internal_decision, envelope=client_payload)
    require(internal_decision["allowed"] is False, "Client must be blocked from reserving for internal-only system agents.")
    require(denied_reservation["event_type"] == "credit_reservation_denied", "Internal agent reservation must become denied placeholder.")
    require(denied_reservation["denial_reason"], "Denied reservation must preserve a safe denial reason.")
    require(denied_reservation["final_27_agent_validation"]["internal_only_agent_keys"] == ["orchestration_agent"], "Denied reservation must preserve final 27 diagnostics for admin.")
    assert_no_mutation(denied_reservation)

    dry_run_decision = enforcement.build_api_acceptance_entitlement_decision({**client_payload, "dry_run": True, "credit_reservation_status": "not_reserved"})
    preflight_decision = enforcement.build_api_acceptance_entitlement_decision({**client_payload, "preflight_only": True, "credit_reservation_status": "not_reserved"})
    smoke_decision = enforcement.build_api_acceptance_entitlement_decision({**client_payload, "smoke_test_mode": True, "credit_reservation_status": "not_reserved"})
    for decision_item in [dry_run_decision, preflight_decision, smoke_decision]:
        entry = ledger.build_credit_reservation_placeholder(decision_item, envelope=client_payload)
        require(entry["status"] == "no_mutation_evidence_recorded", "Dry/preflight/smoke should record no-mutation evidence.")
        assert_no_mutation(entry)

    site_payload = {
        **client_payload,
        "task_type": "generated_site",
        "workflow_type": "website_app_agent_delivery",
        "selected_agent": "website_app_agent",
        "selected_agents": ["website_app_agent"],
        "agent_ids": ["website_app_agent"],
        "active_agents": ["website_app_agent"],
    }
    site_decision = enforcement.build_api_acceptance_entitlement_decision(site_payload)
    integration_payload = {
        **client_payload,
        "task_type": "integration_job",
        "workflow_type": "workflow_automation_agent_delivery",
        "selected_agent": "workflow_automation_agent",
        "selected_agents": ["workflow_automation_agent"],
        "agent_ids": ["workflow_automation_agent"],
        "active_agents": ["workflow_automation_agent"],
        "integration_provider": "future_integration_provider",
    }
    integration_decision = enforcement.build_api_acceptance_entitlement_decision(integration_payload)
    support_payload = {
        **client_payload,
        "actor_role": "owner",
        "task_type": "support_admin_action",
        "workflow_type": "support_recovery",
        "selected_agent": "operations_agent",
        "selected_agents": ["operations_agent"],
        "agent_ids": ["operations_agent"],
    }
    support_decision = enforcement.build_api_acceptance_entitlement_decision(support_payload)
    require(ledger.build_credit_reservation_placeholder(site_decision, envelope=site_payload)["task_type"] == "generated_site", "Ledger must support generated site jobs.")
    require(ledger.build_credit_reservation_placeholder(integration_decision, envelope=integration_payload)["task_type"] == "integration_job", "Ledger must support integration jobs.")
    require(ledger.build_admin_override_placeholder(support_payload)["event_type"] == "admin_override_recorded", "Ledger must support support/admin actions.")

    envelope = acceptance.build_api_job_acceptance_envelope({**client_payload, "job_id": "job_billing_aws12_envelope"})
    envelope_reservation = ledger.build_credit_reservation_placeholder(envelope)
    require(envelope_reservation["job_id"] == "job_billing_aws12_envelope", "Ledger must consume AWS-05 accepted envelope metadata.")
    require(envelope_reservation["final_27_agent_validation"]["valid"] is True, "Envelope ledger entry must consume AWS-11 enforcement metadata.")

    client_view = ledger.build_client_safe_billing_view(reservation)
    admin_view = ledger.build_admin_safe_billing_diagnostics_view(reservation)
    for hidden in [
        "provider_estimated_cost",
        "provider_actual_cost",
        "provider_class",
        "provider_name",
        "stripe_reference",
        "package_entitlement_reference",
        "final_27_agent_validation",
        "audit",
    ]:
        require(hidden not in client_view, f"Client billing view must hide internal/provider/Stripe diagnostic: {hidden}")
    require(client_view["estimated_credit_cost"] == reservation["estimated_credit_cost"], "Client view may show credit estimate.")
    require(client_view["credential_values_exposed"] is False, "Client billing view must not expose credentials.")
    require("provider_estimated_cost" in admin_view, "Admin diagnostics should include provider estimated cost placeholder.")
    require("stripe_reference" in admin_view, "Admin diagnostics should include Stripe reference placeholder.")
    require(admin_view["credential_values_exposed"] is False, "Admin diagnostics must not expose credentials.")
    require("STRIPE_SECRET_SHOULD_NOT_LEAK" not in str(admin_view), "Admin diagnostics must redact secrets.")

    validation = ledger.validate_billing_credit_ledger_entry(reservation)
    require(validation["valid"] is True, f"Reservation ledger entry should validate: {validation}")
    require(validation["stripe_call_attempted"] is False, "Ledger validation must not call Stripe.")
    require(validation["aws_call_attempted"] is False, "Ledger validation must not call AWS.")
    require(validation["provider_call_attempted"] is False, "Ledger validation must not call providers.")
    require(validation["credit_mutation_attempted"] is False, "Ledger validation must not mutate credits.")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-12 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-12 must not alter enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "AWS-12 must not expose SYSTEM_AGENTS as client-selectable.")

    for marker in [
        "CanonicalBillingCreditLedgerEntry",
        "LEDGER_EVENT_TYPES",
        "build_credit_reservation_placeholder",
        "build_credit_finalization_placeholder",
        "build_credit_refund_placeholder",
        "build_credit_reversal_placeholder",
        "build_admin_override_placeholder",
        "build_client_safe_billing_view",
        "build_admin_safe_billing_diagnostics_view",
        "no_mutation_placeholder",
    ]:
        require(marker in source, f"AWS-12 source missing marker: {marker}")

    for marker in [
        "AWS-12",
        "billing/credit ledger boundary",
        "verify_billing_credit_ledger_boundary.py",
        "reservation/finalization/refund/reversal placeholders",
        "no Stripe, AWS, provider, RDS, queue, or credit mutation",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-12 marker: {marker}")

    print("BILLING_CREDIT_LEDGER_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
