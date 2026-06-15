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


def assert_no_mutation(decision: dict) -> None:
    for key in [
        "billing_mutation_attempted",
        "stripe_call_attempted",
        "provider_call_attempted",
        "aws_call_attempted",
        "credit_mutation_attempted",
        "queue_mutation_attempted",
    ]:
        require(decision[key] is False, f"Boundary must not mutate/call external systems: {key}")


def main() -> int:
    enforcement = load_module(
        "backend/app/runtime/api_acceptance_entitlement_boundary.py",
        "api_acceptance_entitlement_boundary_under_test",
    )
    acceptance = load_module(
        "backend/app/runtime/api_job_acceptance_boundary.py",
        "api_job_acceptance_boundary_for_entitlement_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_entitlement_test",
    )

    source = read("backend/app/runtime/api_acceptance_entitlement_boundary.py")
    acceptance_source = read("backend/app/runtime/api_job_acceptance_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "import stripe",
        "stripe.",
        "boto3",
        "requests.",
        "httpx.",
        "get_secret_value",
        "put_object",
        "send_message",
        "provider.execute",
        "reserve_credit(",
        "finalize_credit(",
    ]:
        require(marker not in source, f"AWS-11 boundary must not contain live spend/provider/AWS marker: {marker}")
    require("canonical_entitlement_activation_runtime" not in source, "AWS-11 boundary must avoid entitlement runtime imports that can initialize persistence.")

    admin_payload = {
        "actor_role": "owner",
        "package_name": "starter",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "selected_agent": "head_agent",
        "selected_agents": ["head_agent", "marketing_specialist_agent"],
        "agent_ids": ["head_agent", "marketing_specialist_agent"],
        "video_provider": "future_video_provider",
        "estimated_credits_required": 1000,
        "approval_required": True,
        "credit_reservation_status": "not_reserved",
        "correlation_id": "corr_admin_entitlement",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK",
    }
    admin_decision = enforcement.build_api_acceptance_entitlement_decision(admin_payload)
    require(admin_decision["allowed"] is True, "Admin/owner should be unrestricted by package and credit limits.")
    require(admin_decision["actor_role"] == "admin", "Owner role should normalize to admin.")
    require(admin_decision["authority_level"] == "owner_unrestricted", "Admin decision must show owner unrestricted authority.")
    require(admin_decision["credit_reservation_required"] is False, "Admin should not require credit reservation.")
    require(admin_decision["approval_required"] is False, "Admin should not be blocked by approval mode.")
    require(admin_decision["audit"]["correlation_id"] == "corr_admin_entitlement", "Admin decision must preserve audit correlation.")
    assert_no_mutation(admin_decision)
    require("RUNWAY_SECRET_SHOULD_NOT_LEAK" not in str(admin_decision), "Admin decision must not leak provider secrets.")
    require("STRIPE_SECRET_SHOULD_NOT_LEAK" not in str(admin_decision), "Admin decision must not leak Stripe secrets.")

    client_allowed_payload = {
        "actor_role": "client",
        "package_name": "business",
        "entitlement_status": "active",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "selected_agent": "marketing_specialist_agent",
        "selected_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "active_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "video_provider": "future_video_provider",
        "credit_reservation_status": "reserved",
        "approval_required_for_spend": True,
        "approval_status": "owner_approved",
        "correlation_id": "corr_client_allowed",
    }
    client_allowed = enforcement.build_api_acceptance_entitlement_decision(client_allowed_payload)
    require(client_allowed["allowed"] is True, f"Client with active agents, reserved credits, and approval should be allowed: {client_allowed}")
    require(client_allowed["authority_level"] == "client_package_credit_governed", "Client decision must be package/credit governed.")
    require(client_allowed["credit_reservation_required"] is True, "Paid client job should require credit reservation placeholder.")
    require(client_allowed["credit_reservation_status"] == "reserved", "Credit reservation status placeholder must be preserved.")
    require(client_allowed["approval_required"] is True, "Spend-sensitive client job should require approval when configured.")
    require(client_allowed["approval_status"] == "owner_approved", "Approval status placeholder must be preserved.")
    assert_no_mutation(client_allowed)

    client_internal = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "selected_agent": "orchestration_agent",
        "selected_agents": ["orchestration_agent"],
        "active_agents": ["orchestration_agent"],
        "credit_reservation_status": "reserved",
        "approval_status": "owner_approved",
    })
    require(client_internal["allowed"] is False, "Client must be blocked from internal-only SYSTEM_AGENTS.")
    require("selected_agent_not_available" in client_internal["denial_reasons"], "Internal/system agent denial must be client-safe.")
    require(client_internal["final_27_agent_validation"]["internal_only_agent_keys"] == ["orchestration_agent"], "Admin diagnostics must identify internal-only selected agent.")

    client_inactive = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "active_agents": ["ugc_media_agent"],
        "credit_reservation_status": "reserved",
        "approval_status": "owner_approved",
    })
    require(client_inactive["allowed"] is False, "Client selected agents must be in active entitlement.")
    require("selected_agent_not_in_active_entitlement" in client_inactive["denial_reasons"], "Inactive agent denial reason missing.")

    client_credit_blocked = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "credit_reservation_status": "not_reserved",
        "approval_status": "owner_approved",
    })
    require(client_credit_blocked["allowed"] is False, "Client paid job must block without credit reservation placeholder.")
    require("credit_reservation_required" in client_credit_blocked["denial_reasons"], "Credit reservation denial reason missing.")
    require(client_credit_blocked["credit_finalization_status"] == "not_started", "Credit finalization must be placeholder only.")
    require(client_credit_blocked["refund_reversal_status"] == "not_started", "Refund/reversal must be placeholder only.")
    assert_no_mutation(client_credit_blocked)

    client_approval_blocked = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "credit_reservation_status": "reserved",
        "approval_status": "pending",
    })
    require(client_approval_blocked["allowed"] is False, "Client spend-sensitive job must block when approval is pending.")
    require("owner_approval_required" in client_approval_blocked["denial_reasons"], "Approval denial reason missing.")

    dry_run = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "dry_run": True,
        "credit_reservation_status": "not_reserved",
        "approval_status": "pending",
    })
    require(dry_run["allowed"] is True, "Dry run should not require paid credit mutation or spend approval.")
    require(dry_run["credit_reservation_required"] is False, "Dry run must not require credit reservation.")
    require(dry_run["approval_required"] is False, "Dry run must not require spend approval.")
    assert_no_mutation(dry_run)

    preflight = enforcement.build_api_acceptance_entitlement_decision({**client_allowed_payload, "preflight_only": True, "credit_reservation_status": "not_reserved"})
    smoke = enforcement.build_api_acceptance_entitlement_decision({**client_allowed_payload, "smoke_test_mode": True, "credit_reservation_status": "not_reserved"})
    require(preflight["credit_reservation_required"] is False, "Preflight must not require paid credit mutation.")
    require(smoke["credit_reservation_required"] is False, "Smoke test decision must not mutate paid credits.")
    assert_no_mutation(preflight)
    assert_no_mutation(smoke)

    generated_site = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "task_type": "generated_site",
        "workflow_type": "website_app_agent_delivery",
        "selected_agent": "website_app_agent",
        "selected_agents": ["website_app_agent"],
        "active_agents": ["website_app_agent"],
        "credit_reservation_status": "reserved",
        "approval_status": "owner_approved",
    })
    integration_job = enforcement.build_api_acceptance_entitlement_decision({
        **client_allowed_payload,
        "task_type": "integration_job",
        "workflow_type": "workflow_automation_agent_delivery",
        "selected_agent": "workflow_automation_agent",
        "selected_agents": ["workflow_automation_agent"],
        "active_agents": ["workflow_automation_agent"],
        "credit_reservation_status": "reserved",
        "approval_status": "owner_approved",
    })
    require(generated_site["spend_sensitive"] is True, "Generated site jobs must be spend-sensitive in the control plane.")
    require(integration_job["spend_sensitive"] is True, "Integration jobs must be represented in the control plane.")

    validation = enforcement.validate_api_acceptance_entitlement_decision(client_allowed)
    require(validation["valid"] is True, f"Valid enforcement decision should validate: {validation}")
    require(validation["stripe_call_attempted"] is False, "Validation must not call Stripe.")
    require(validation["aws_call_attempted"] is False, "Validation must not call AWS.")
    require(validation["provider_call_attempted"] is False, "Validation must not call providers.")
    require(validation["credit_mutation_attempted"] is False, "Validation must not mutate credits.")

    admin_view = enforcement.build_admin_safe_enforcement_view(client_credit_blocked)
    client_view = enforcement.build_client_safe_enforcement_view(client_credit_blocked)
    require("final_27_agent_validation" in admin_view, "Admin view must include final 27 validation diagnostics.")
    require("audit" in admin_view, "Admin view must include audit detail.")
    for hidden in ["final_27_agent_validation", "active_entitled_agents", "audit", "authority_level"]:
        require(hidden not in client_view, f"Client-safe view must hide internal diagnostic field: {hidden}")
    require(client_view["denial_reason"] == "credit_reservation_required", "Client view must expose safe denial reason.")
    require(client_view["credential_values_exposed"] is False, "Client view must not expose credentials.")

    envelope = acceptance.build_api_job_acceptance_envelope({
        **client_allowed_payload,
        "job_id": "job_aws11_envelope",
        "duration_seconds": 5,
        "aspect_ratio": "9:16",
    })
    require("acceptance_enforcement" in envelope, "AWS-05 envelope must include additive AWS-11 enforcement metadata.")
    require(envelope["acceptance_enforcement"]["allowed"] is True, "Envelope enforcement metadata should preserve allowed decision.")
    require(envelope["admin_diagnostics"]["aws_11_entitlement_boundary_attached"] is True, "Envelope diagnostics should mark AWS-11 boundary attachment.")
    envelope_client = acceptance.build_client_api_job_acceptance_view(envelope)
    require("acceptance_enforcement" in envelope_client, "Client envelope view should include client-safe enforcement summary.")
    require("final_27_agent_validation" not in str(envelope_client["acceptance_enforcement"]), "Client enforcement summary must hide internal catalogue diagnostics.")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-11 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-11 must not alter enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "AWS-11 must not expose SYSTEM_AGENTS as client-selectable.")

    for marker in [
        "CanonicalApiAcceptanceEntitlementDecision",
        "build_api_acceptance_entitlement_decision",
        "build_admin_safe_enforcement_view",
        "build_client_safe_enforcement_view",
        "validate_api_acceptance_entitlement_decision",
        "PACKAGE_RULES",
        "credit_reservation_required",
        "approval_required",
    ]:
        require(marker in source, f"AWS-11 source missing marker: {marker}")
    for marker in [
        "acceptance_enforcement",
        "build_api_acceptance_entitlement_decision",
        "aws_11_entitlement_boundary_attached",
    ]:
        require(marker in acceptance_source, f"AWS-05 envelope missing AWS-11 metadata marker: {marker}")
    for marker in [
        "AWS-11",
        "API acceptance entitlement boundary",
        "verify_api_acceptance_entitlement_boundary.py",
        "credit/package/approval enforcement",
        "no Stripe, AWS, provider, queue, or credit mutation",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-11 marker: {marker}")

    print("API_ACCEPTANCE_ENTITLEMENT_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
