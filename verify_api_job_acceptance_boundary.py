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


def main() -> int:
    acceptance = load_module(
        "backend/app/runtime/api_job_acceptance_boundary.py",
        "api_job_acceptance_boundary_under_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_acceptance_test",
    )
    source = read("backend/app/runtime/api_job_acceptance_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    popup_payload = {
        "job_id": "job_acceptance_aws05_test",
        "client_id": "client_999",
        "tenant_id": "tenant_999",
        "requested_from": "complete_media_popup",
        "requested_by_role": "admin",
        "role": "owner",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "media_type": "complete_video",
        "asset_type": "final_mp4",
        "output_type": "Complete video with voiceover",
        "duration_seconds": 25,
        "aspect_ratio": "9:16",
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "prompt": "Create a premium epoxy flooring promo.",
        "media_prompt": "Show polished epoxy floor reveal with CTA text.",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "multi_agent_media_execution": True,
        "approval_required": False,
        "owner_approval_required": False,
        "approval_status": "admin_unrestricted",
        "requires_credit_check": False,
        "requires_package_check": False,
        "credit_reservation_status": "not_reserved",
        "correlation_id": "corr_acceptance_aws05",
        "idempotency_key": "idem_acceptance_aws05",
        "assets": [
            {
                "asset_id": "asset_expected_output_aws05",
                "asset_type": "expected_final_video",
                "source_type": "generated",
                "client_safe_url": "/api/universal-complete-media-asset?id=asset_expected_output_aws05",
            }
        ],
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
    }

    result = acceptance.accept_api_job_locally_or_noop(popup_payload, env={"AWS_OPTION_A_ENABLED": "false"})
    envelope = result["envelope"]
    admin_view = result["admin_view"]
    client_view = result["client_view"]
    local_contract = aws_contract.aws_option_a_readiness({})
    all_text = str(result)
    client_text = str(client_view)

    require(result["success"] is True, "Acceptance boundary should return success in local/no-op mode.")
    require(result["accepted"] is True, "Acceptance boundary should accept the job envelope.")
    require(result["job_id"] == "job_acceptance_aws05_test", "Acceptance result must preserve job_id.")
    require(envelope["status_lifecycle"]["status"] == "accepted", "Envelope must include accepted lifecycle status.")
    require(envelope["status_lifecycle"]["queue_mode"] == "local_noop", "AWS disabled mode must use local/no-op queue mode.")
    require(envelope["status_lifecycle"]["local_compatibility"] is True, "AWS disabled mode must mark local compatibility.")

    require(envelope["selected_agent"] == "creative_director_agent", "Envelope must preserve selected_agent.")
    require(envelope["selected_agents"] == popup_payload["selected_agents"], "Envelope must preserve selected_agents.")
    require(envelope["agent_ids"] == popup_payload["agent_ids"], "Envelope must preserve agent_ids.")
    require(envelope["multi_agent_media_execution"] is True, "Envelope must preserve multi_agent_media_execution.")
    require(envelope["media_type"] == "complete_video", "Envelope must preserve media_type.")
    require(envelope["asset_type"] == "final_mp4", "Envelope must preserve asset_type.")
    require(envelope["output_type"] == "Complete video with voiceover", "Envelope must preserve output_type.")
    require(envelope["duration_seconds"] == 25, "Envelope must preserve duration_seconds.")
    require(envelope["aspect_ratio"] == "9:16", "Envelope must preserve aspect_ratio.")
    require(envelope["provider_preferences"]["video_provider"] == "runway", "Envelope must preserve video provider.")
    require(envelope["provider_preferences"]["audio_provider"] == "elevenlabs", "Envelope must preserve audio provider.")

    require(envelope["durable_job_record"]["job_id"] == "job_acceptance_aws05_test", "Envelope must include durable job record.")
    require(envelope["queue_message"]["job_id"] == "job_acceptance_aws05_test", "Envelope must include queue message.")
    require(envelope["queue_result"]["status"] == "local_noop_enqueued", "Envelope must include local/no-op queue result.")
    require(envelope["asset_placeholders"], "Envelope must include asset placeholders.")
    require(envelope["runtime_readiness"]["aws_option_a_enabled"] is False, "Envelope must include AWS readiness.")

    require(envelope["approval_controls"]["approval_status"] == "admin_unrestricted", "Approval placeholder must be preserved.")
    require(envelope["package_credit_controls"]["credit_reservation_status"] == "not_reserved", "Credit reservation placeholder must be preserved.")
    require(envelope["package_credit_controls"]["billing_mutation_attempted"] is False, "Acceptance must not mutate billing.")
    require(envelope["package_credit_controls"]["stripe_mutation_attempted"] is False, "Acceptance must not mutate Stripe.")

    require(result["rds_write_attempted"] is False, "Acceptance must not write RDS in AWS-05.")
    require(result["sqs_send_attempted"] is False, "Acceptance must not send SQS in AWS-05 local mode.")
    require(result["s3_upload_attempted"] is False, "Acceptance must not upload S3 in AWS-05.")
    require(result["paid_provider_calls_started"] is False, "Acceptance must not call providers.")
    require(result["billing_mutation_attempted"] is False, "Acceptance must not mutate billing.")
    require(result["stripe_mutation_attempted"] is False, "Acceptance must not mutate Stripe.")
    require(local_contract["ready_for_aws_execution"] is False, "No AWS credentials should be required for local acceptance.")

    for secret_value in [
        "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "ELEVEN_SECRET_SHOULD_NOT_LEAK",
        "STRIPE_SECRET_SHOULD_NOT_LEAK",
    ]:
        require(secret_value not in all_text, f"Acceptance result leaked secret value: {secret_value}")

    for hidden_key in [
        "queue_message",
        "queue_result",
        "durable_job_record",
        "runtime_readiness",
        "admin_diagnostics",
        "provider_preferences",
        "package_credit_controls",
        "approval_controls",
    ]:
        require(hidden_key not in client_view, f"Client view must hide internal field: {hidden_key}")
    require(client_view["status"] == "queued", "Client view must expose friendly queued status.")
    require(client_view["customer_safe"] is True, "Client view must be customer_safe.")
    require(client_view["credential_values_exposed"] is False, "Client view must not expose credentials.")
    require("local_path" not in client_text, "Client view must not expose local paths.")

    require("queue_message" in admin_view, "Admin view must include queue message for support diagnostics.")
    require("admin_diagnostics" in admin_view, "Admin view must include admin diagnostics.")
    require(admin_view["admin_diagnostics"]["boundary"] == "AWS-05_api_job_acceptance_boundary", "Admin diagnostics must identify boundary.")
    require(admin_view["audit"]["correlation_id"] == "corr_acceptance_aws05", "Admin view must preserve correlation id.")

    enabled_result = acceptance.accept_api_job_locally_or_noop(popup_payload, env={"AWS_OPTION_A_ENABLED": "true"})
    require(enabled_result["envelope"]["queue_result"]["status"] == "aws_sqs_adapter_not_enabled_yet", "AWS enabled path must remain disabled SQS facade.")
    require(enabled_result["sqs_send_attempted"] is False, "AWS-05 must not send SQS even when AWS flag is true.")

    for marker in [
        "AcceptedApiJobEnvelope",
        "build_api_job_acceptance_envelope",
        "build_admin_api_job_acceptance_view",
        "build_client_api_job_acceptance_view",
        "LocalCompatibilityApiJobAcceptanceBoundary",
        "accept_api_job_locally_or_noop",
        "billing_mutation_attempted",
        "stripe_mutation_attempted",
        "paid_provider_calls_started",
    ]:
        require(marker in source, f"Acceptance boundary source missing marker: {marker}")

    for marker in [
        "AWS-05",
        "API job acceptance boundary",
        "verify_api_job_acceptance_boundary.py",
        "accepted job envelope",
        "local/no-op queue acceptance",
        "future SaaS job acceptance",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-05 marker: {marker}")

    print("API_JOB_ACCEPTANCE_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
