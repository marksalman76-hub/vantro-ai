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


def sample_queue_payload() -> dict:
    return {
        "job_id": "job_ffmpeg_aws07_test",
        "client_id": "client_ffmpeg_001",
        "tenant_id": "tenant_ffmpeg_001",
        "requested_from": "complete_media_popup",
        "role": "owner",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "media_type": "complete_video",
        "asset_type": "final_mp4",
        "output_type": "Complete video with voiceover",
        "duration_seconds": 10,
        "aspect_ratio": "16:9",
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "multi_agent_media_execution": True,
        "correlation_id": "corr_ffmpeg_aws07",
    }


def main() -> int:
    readiness_module = load_module(
        "backend/app/runtime/ffmpeg_worker_readiness_boundary.py",
        "ffmpeg_worker_readiness_boundary_under_test",
    )
    worker_module = load_module(
        "backend/app/runtime/ecs_media_worker_execution_boundary.py",
        "ecs_media_worker_execution_boundary_for_ffmpeg_test",
    )
    queue_module = load_module(
        "backend/app/runtime/media_queue_adapter_boundary.py",
        "media_queue_adapter_boundary_for_ffmpeg_test",
    )
    source = read("backend/app/runtime/ffmpeg_worker_readiness_boundary.py")
    worker_source = read("backend/app/runtime/ecs_media_worker_execution_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    missing = readiness_module.build_ffmpeg_worker_readiness_contract(
        env={"AWS_OPTION_A_ENABLED": "false"},
        ffmpeg_binary="definitely_missing_ffmpeg_binary_codex_test",
    )
    admin_view = readiness_module.admin_ffmpeg_worker_readiness_view(missing)
    client_view = readiness_module.client_ffmpeg_worker_readiness_view(missing)

    require(missing["python_runtime"]["python_version"], "Readiness must include Python runtime metadata.")
    require(missing["backend_import_readiness"]["importable"] is True, "Readiness must confirm backend worker boundary importability.")
    require(missing["ffmpeg_availability"]["available"] is False, "Missing ffmpeg binary must be reported as unavailable.")
    require(missing["ffmpeg_availability"]["missing_ffmpeg_safe_status"] == "ffmpeg_missing_safe", "Missing ffmpeg must be safe status.")
    require(missing["ffmpeg_availability"]["version_probe_executed"] is False, "Readiness must not execute ffmpeg version probe by default.")
    require(missing["ffmpeg_availability"]["composition_probe_executed"] is False, "Readiness must not execute composition probe.")
    require(missing["workdir_contract"]["write_probe_executed"] is False, "Readiness must not write probe files.")
    require(missing["runtime_outputs_dependency"]["runtime_outputs_required_after_aws_cutover"] is False, "AWS cutover must not depend on runtime_outputs.")
    require(missing["future_s3_contract"]["s3_calls_started"] is False, "Readiness must not call S3.")
    require(missing["future_s3_contract"]["requires_aws_credentials_now"] is False, "Readiness must not require AWS credentials.")
    require(missing["cloudwatch_log_readiness"]["cloudwatch_calls_started"] is False, "Readiness must not call CloudWatch.")
    require(missing["safe_failure_behavior"]["missing_ffmpeg_crashes_process"] is False, "Missing ffmpeg must not crash process.")
    require(missing["ffmpeg_composition_invoked"] is False, "Readiness must not invoke ffmpeg composition.")
    require(missing["provider_calls_started"] is False, "Readiness must not call providers.")
    require(missing["aws_calls_started"] is False, "Readiness must not call AWS.")
    require(missing["billing_credit_mutation_started"] is False, "Readiness must not mutate billing/credits.")
    require(missing["media_generation_started"] is False, "Readiness must not generate media.")

    require("binary_path" in admin_view["ffmpeg_availability"], "Admin readiness view may include binary path diagnostics.")
    require("binary_path" not in str(client_view), "Client readiness view must not expose binary path/internal diagnostics.")
    require(client_view["status"] == "composition_not_ready", "Client readiness view must be friendly when ffmpeg is missing.")

    queue_message = queue_module.build_media_queue_message(sample_queue_payload())
    worker_result = worker_module.LocalNoopEcsMediaWorkerExecutionBoundary(
        env={"AWS_OPTION_A_ENABLED": "false"}
    ).process(queue_message)
    task = worker_result["task"]
    admin_worker_view = worker_result["admin_view"]
    client_worker_view = worker_result["client_view"]

    require(worker_result["success"] is True, "Worker boundary must still process local/no-op with ffmpeg readiness attached.")
    require("ffmpeg_readiness" in task, "Worker task must reference ffmpeg readiness result.")
    require("ffmpeg_readiness" in admin_worker_view, "Admin worker view must expose ffmpeg readiness diagnostics.")
    require("ffmpeg_readiness" not in client_worker_view, "Client worker view must hide ffmpeg readiness diagnostics.")
    require(worker_result["ffmpeg_invoked"] is False, "Worker boundary must not invoke ffmpeg.")
    require(worker_result["composition_started"] is False, "Worker boundary must not start composition.")
    require(worker_result["provider_execution_started"] is False, "Worker boundary must not start providers.")
    require(worker_result["aws_calls_started"] is False, "Worker boundary must not call AWS.")

    for forbidden in [
        "subprocess",
        "Popen",
        "requests.",
        "httpx.",
        "boto3",
        "ffmpeg -i",
        "run(",
        "check_call",
        "check_output",
    ]:
        require(forbidden not in source, f"ffmpeg readiness boundary must not introduce live execution call: {forbidden}")

    for marker in [
        "FfmpegWorkerReadinessContract",
        "build_ffmpeg_worker_readiness_contract",
        "ffmpeg_availability_check",
        "admin_ffmpeg_worker_readiness_view",
        "client_ffmpeg_worker_readiness_view",
        "missing_ffmpeg_safe_status",
        "runtime_outputs_required_after_aws_cutover",
        "future_s3_contract",
        "cloudwatch_log_readiness",
    ]:
        require(marker in source, f"ffmpeg readiness source missing marker: {marker}")

    for marker in [
        "build_ffmpeg_worker_readiness_contract",
        "ffmpeg_readiness",
        "ffmpeg_invoked",
    ]:
        require(marker in worker_source, f"worker boundary missing ffmpeg readiness marker: {marker}")

    for marker in [
        "AWS-07",
        "ffmpeg worker image/readiness boundary",
        "verify_ffmpeg_worker_readiness_boundary.py",
        "safe missing-ffmpeg handling",
        "future S3 input/output contract",
        "CloudWatch log readiness",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-07 marker: {marker}")

    print("FFMPEG_WORKER_READINESS_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
