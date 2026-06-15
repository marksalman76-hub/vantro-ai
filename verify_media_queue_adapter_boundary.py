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
    queue = load_module(
        "backend/app/runtime/media_queue_adapter_boundary.py",
        "media_queue_adapter_boundary_under_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_queue_test",
    )
    source = read("backend/app/runtime/media_queue_adapter_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    popup_payload = {
        "job_id": "job_queue_aws03_test",
        "client_id": "client_456",
        "tenant_id": "tenant_456",
        "requested_from": "complete_media_popup",
        "media_type": "complete_video",
        "asset_type": "final_mp4",
        "output_type": "Complete video with voiceover",
        "prompt": "Create a polished epoxy flooring ad for homeowners.",
        "media_prompt": "Premium epoxy floor reveal with no people.",
        "business_name": "Bright Floors",
        "product_or_service": "Epoxy flooring",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "multi_agent_media_execution": True,
        "duration_seconds": 25,
        "aspect_ratio": "9:16",
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "dry_run": False,
        "preflight_only": False,
        "smoke_test_mode": False,
        "credit_risk_acknowledged": True,
        "cost_safety_confirmed": True,
        "paid_provider_risk_confirmed": True,
        "portal_mode": "admin",
        "role": "owner",
        "is_owner": True,
        "owner_approval_required": False,
        "requires_credit_check": False,
        "requires_package_check": False,
        "approval_status": "admin_unrestricted",
        "credit_reservation_status": "not_reserved",
        "correlation_id": "corr_aws03_test",
        "idempotency_key": "idem_aws03_test",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
        "internal_config": {"stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK"},
    }

    message = queue.build_media_queue_message(popup_payload)
    validation = queue.validate_media_queue_message(message)
    enqueue_result = queue.enqueue_media_work_locally_or_noop(message, env={"AWS_OPTION_A_ENABLED": "false"})
    enabled_result = queue.enqueue_media_work_locally_or_noop(message, env={"AWS_OPTION_A_ENABLED": "true"})
    local_contract = aws_contract.aws_option_a_readiness({})
    message_text = str(message)
    enqueue_text = str(enqueue_result)

    require(validation["valid"] is True, f"Queue message should validate: {validation}")
    require(message["job_id"] == "job_queue_aws03_test", "Queue message must preserve job_id.")
    require(message["customer_id"] == "client_456", "Queue message must preserve customer/account reference.")
    require(message["requested_from"] == "complete_media_popup", "Queue message must preserve popup requested_from.")
    require(message["media_type"] == "complete_video", "Queue message must preserve media_type.")
    require(message["asset_type"] == "final_mp4", "Queue message must preserve asset_type.")
    require(message["output_type"] == "Complete video with voiceover", "Queue message must preserve output_type.")
    require(message["prompt_metadata"]["prompt"], "Queue message must include prompt metadata.")
    require(message["prompt_metadata"]["media_prompt"], "Queue message must include media_prompt metadata.")

    require(message["selected_agent"] == "creative_director_agent", "Queue message must preserve selected_agent.")
    require(message["selected_agents"] == popup_payload["selected_agents"], "Queue message must preserve selected_agents.")
    require(message["agent_ids"] == popup_payload["agent_ids"], "Queue message must preserve agent_ids.")
    require(message["multi_agent_media_execution"] is True, "Queue message must preserve multi_agent_media_execution.")

    require(message["duration_seconds"] == 25, "Queue message must preserve duration_seconds.")
    require(message["aspect_ratio"] == "9:16", "Queue message must preserve aspect_ratio.")
    require(message["provider_preferences"]["video_provider"] == "runway", "Queue message must preserve video provider.")
    require(message["provider_preferences"]["audio_provider"] == "elevenlabs", "Queue message must preserve audio provider.")
    require(message["execution_flags"]["dry_run"] is False, "Queue message must preserve dry_run flag.")
    require(message["execution_flags"]["preflight_only"] is False, "Queue message must preserve preflight_only flag.")
    require(message["execution_flags"]["smoke_test_mode"] is False, "Queue message must preserve smoke_test_mode flag.")

    require(message["task_type"] == "media_generation", "Queue message must include full-SaaS task_type marker.")
    require(message["workflow_type"] == "universal_complete_media", "Queue message must include workflow_type marker.")
    require(message["approval_controls"]["approval_status"] == "admin_unrestricted", "Queue message must include approval placeholder.")
    require(message["credit_reservation"]["credit_reservation_status"] == "not_reserved", "Queue message must include credit reservation placeholder.")
    require(message["audit"]["correlation_id"] == "corr_aws03_test", "Queue message must include audit/correlation marker.")
    require(message["future_sqs"]["target_backend"] == "aws_sqs", "Queue message must include future SQS metadata.")
    require(message["future_sqs"]["sqs_send_enabled"] is False, "AWS-03 must not enable SQS sends.")

    for secret_value in [
        "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "ELEVEN_SECRET_SHOULD_NOT_LEAK",
        "STRIPE_SECRET_SHOULD_NOT_LEAK",
    ]:
        require(secret_value not in message_text, f"Queue message leaked secret value: {secret_value}")
        require(secret_value not in enqueue_text, f"Queue enqueue result leaked secret value: {secret_value}")

    require(local_contract["aws_option_a_enabled"] is False, "AWS Option A must remain disabled by default.")
    require(enqueue_result["success"] is True, "AWS disabled queue boundary should accept local/no-op enqueue.")
    require(enqueue_result["status"] == "local_noop_enqueued", "AWS disabled queue boundary must use local/no-op behavior.")
    require(enqueue_result["sqs_send_attempted"] is False, "AWS disabled queue boundary must not attempt SQS send.")
    require(enqueue_result["paid_provider_calls_started"] is False, "Queue boundary must not start paid provider calls.")
    require(enqueue_result["stripe_or_credit_reservation_attempted"] is False, "Queue boundary must not alter Stripe/credits.")
    require(enqueue_result["portal_auth_or_session_changed"] is False, "Queue boundary must not alter portal auth/session.")

    require(enabled_result["status"] == "aws_sqs_adapter_not_enabled_yet", "AWS enabled path must remain a disabled SQS stub.")
    require(enabled_result["sqs_send_attempted"] is False, "AWS-03 must not send to live SQS even when env flag is true.")

    for marker in [
        "CanonicalMediaQueueMessage",
        "build_media_queue_message",
        "validate_media_queue_message",
        "LocalNoopMediaQueueAdapter",
        "enqueue_media_work_locally_or_noop",
        "task_type",
        "workflow_type",
        "credit_reservation",
        "approval_controls",
        "future_sqs",
    ]:
        require(marker in source, f"Queue adapter source missing marker: {marker}")

    for marker in [
        "AWS-03",
        "media queue adapter boundary",
        "verify_media_queue_adapter_boundary.py",
        "local/no-op queue behavior",
        "SQS-ready message envelope",
        "future non-media queues",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-03 marker: {marker}")

    print("MEDIA_QUEUE_ADAPTER_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
