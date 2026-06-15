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


def base_popup_payload() -> dict:
    return {
        "job_id": "job_worker_aws06_test",
        "client_id": "client_worker_001",
        "tenant_id": "tenant_worker_001",
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
        "approval_status": "admin_unrestricted",
        "requires_credit_check": False,
        "requires_package_check": False,
        "credit_reservation_status": "not_reserved",
        "correlation_id": "corr_worker_aws06",
        "idempotency_key": "idem_worker_aws06",
        "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
        "provider_credentials": {"elevenlabs_api_key": "ELEVEN_SECRET_SHOULD_NOT_LEAK"},
    }


def assert_worker_result_safe(result: dict, source_name: str) -> None:
    task = result["task"]
    admin_view = result["admin_view"]
    client_view = result["client_view"]
    all_text = str(result)
    client_text = str(client_view)
    lifecycle_states = [event.get("state") for event in task.get("lifecycle_events") or []]

    require(result["success"] is True, f"{source_name} worker result should succeed in local/no-op mode.")
    require(result["status"] == "completed_local_noop", f"{source_name} worker result must complete local/no-op.")
    require(task["job_id"] == "job_worker_aws06_test", f"{source_name} must preserve job_id.")
    require(task["selected_agent"] == "creative_director_agent", f"{source_name} must preserve selected_agent.")
    require(task["selected_agents"] == ["creative_director_agent", "media_producer_agent"], f"{source_name} must preserve selected_agents.")
    require(task["agent_ids"] == ["creative_director_agent", "media_producer_agent"], f"{source_name} must preserve agent_ids.")
    require(task["multi_agent_media_execution"] is True, f"{source_name} must preserve multi_agent_media_execution.")
    require(task["media_type"] == "complete_video", f"{source_name} must preserve media_type.")
    require(task["duration_seconds"] == 25, f"{source_name} must preserve duration_seconds.")
    require(task["aspect_ratio"] == "9:16", f"{source_name} must preserve aspect_ratio.")
    require(task["provider_preferences"]["video_provider"] == "runway", f"{source_name} must preserve video provider.")
    require(task["provider_preferences"]["audio_provider"] == "elevenlabs", f"{source_name} must preserve audio provider.")
    require(task["authority"]["portal_mode"] == "admin", f"{source_name} must preserve authority markers.")
    require(task["audit"]["correlation_id"] == "corr_worker_aws06", f"{source_name} must preserve audit/correlation id.")

    for state in [
        "received",
        "claimed",
        "validating",
        "planning",
        "provider_preflight_ready",
        "provider_execution_disabled",
        "composing_disabled",
        "asset_persistence_disabled",
        "completed_local_noop",
    ]:
        require(state in lifecycle_states, f"{source_name} missing lifecycle state: {state}")

    require(result["provider_execution_started"] is False, f"{source_name} must not start providers.")
    require(result["ffmpeg_invoked"] is False, f"{source_name} must not invoke ffmpeg.")
    require(result["composition_started"] is False, f"{source_name} must not compose media.")
    require(result["asset_persistence_started"] is False, f"{source_name} must not persist assets.")
    require(result["billing_credit_finalization_started"] is False, f"{source_name} must not finalize credits.")
    require(result["aws_calls_started"] is False, f"{source_name} must not call AWS.")
    require(result["worker_loop_started"] is False, f"{source_name} must not start a worker loop.")
    require(result["final_27_agent_catalogue_not_modified"] is True, f"{source_name} must not modify final 27-agent catalogue.")

    for secret_value in ["RUNWAY_SECRET_SHOULD_NOT_LEAK", "ELEVEN_SECRET_SHOULD_NOT_LEAK"]:
        require(secret_value not in all_text, f"{source_name} leaked secret value: {secret_value}")

    for hidden_key in [
        "lifecycle_events",
        "future_worker_hooks",
        "retry_dlq",
        "runtime_readiness",
        "accepted_envelope",
        "queue_message",
        "provider_preferences",
        "authority",
        "audit",
    ]:
        require(hidden_key not in client_view, f"Client worker view must hide {hidden_key}.")
    require(client_view["status"] == "processing_not_yet_enabled", "Client view must show friendly not-enabled status.")
    require("provider_execution_disabled" not in client_text, "Client view must hide internal lifecycle states.")

    require("lifecycle_events" in admin_view, "Admin worker view must include lifecycle events.")
    require("future_worker_hooks" in admin_view, "Admin worker view must include future hook diagnostics.")
    require(admin_view["audit"]["correlation_id"] == "corr_worker_aws06", "Admin view must preserve correlation id.")
    require(admin_view["provider_execution_started"] is False, "Admin view must show provider execution disabled.")


def main() -> int:
    worker = load_module(
        "backend/app/runtime/ecs_media_worker_execution_boundary.py",
        "ecs_media_worker_execution_boundary_under_test",
    )
    acceptance = load_module(
        "backend/app/runtime/api_job_acceptance_boundary.py",
        "api_job_acceptance_boundary_for_worker_test",
    )
    queue = load_module(
        "backend/app/runtime/media_queue_adapter_boundary.py",
        "media_queue_adapter_boundary_for_worker_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_worker_test",
    )
    source = read("backend/app/runtime/ecs_media_worker_execution_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    accepted = acceptance.build_api_job_acceptance_envelope(base_popup_payload(), env={"AWS_OPTION_A_ENABLED": "false"})
    queue_message = queue.build_media_queue_message(base_popup_payload())

    worker_from_envelope = worker.LocalNoopEcsMediaWorkerExecutionBoundary(
        env={"AWS_OPTION_A_ENABLED": "false"}
    ).process(accepted)
    worker_from_queue = worker.LocalNoopEcsMediaWorkerExecutionBoundary(
        env={"AWS_OPTION_A_ENABLED": "false"}
    ).process(queue_message)

    assert_worker_result_safe(worker_from_envelope, "accepted envelope")
    assert_worker_result_safe(worker_from_queue, "queue message")

    local_contract = aws_contract.aws_option_a_readiness({})
    require(local_contract["ready_for_aws_execution"] is False, "AWS credentials must not be required for AWS-06 local/no-op worker boundary.")
    require(worker_from_envelope["task"]["runtime_readiness"]["aws_option_a_enabled"] is False, "Worker task must include disabled AWS readiness.")

    for forbidden in [
        "boto3",
        "subprocess",
        "requests.post",
        "httpx.",
        "stripe.",
        "Popen",
        "run_one_media_worker_cycle(",
        "process_next(",
    ]:
        require(forbidden not in source, f"Worker boundary must not introduce live side-effect path: {forbidden}")

    for marker in [
        "WORKER_LIFECYCLE_STATES",
        "EcsMediaWorkerTaskEnvelope",
        "process_worker_task_locally_or_noop",
        "build_admin_worker_result_view",
        "build_client_worker_result_view",
        "LocalNoopEcsMediaWorkerExecutionBoundary",
        "provider_execution_disabled",
        "composing_disabled",
        "asset_persistence_disabled",
        "completed_local_noop",
        "final_27_agent_catalogue_not_modified",
    ]:
        require(marker in source, f"Worker boundary source missing marker: {marker}")

    require("approved_agents =" not in source, "AWS-06 must not create or preserve an agent catalogue list.")
    require("AGENT_CATALOGUE" not in source, "AWS-06 must not wire an agent catalogue.")
    require("create_agent" not in source, "AWS-06 must not create new agents.")

    for marker in [
        "AWS-06",
        "ECS/Fargate media worker execution boundary",
        "verify_ecs_media_worker_execution_boundary.py",
        "local/no-op worker processing",
        "future SaaS worker model",
        "final 27-agent catalogue",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-06 marker: {marker}")

    print("ECS_MEDIA_WORKER_EXECUTION_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
