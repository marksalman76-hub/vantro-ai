from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import importlib.util
import os
import platform
import shutil
import sys
import tempfile

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


@dataclass(frozen=True)
class FfmpegWorkerReadinessContract:
    """
    AWS-07 readiness contract for the future ECS/Fargate media worker image.

    This is intentionally a readiness boundary, not composition execution. It
    does not invoke ffmpeg to process media, call AWS, call providers, write
    files, mutate credits, or require ffmpeg to be installed in local dev.
    """

    python_runtime: Dict[str, Any] = field(default_factory=dict)
    backend_import_readiness: Dict[str, Any] = field(default_factory=dict)
    ffmpeg_availability: Dict[str, Any] = field(default_factory=dict)
    workdir_contract: Dict[str, Any] = field(default_factory=dict)
    input_output_mount_contract: Dict[str, Any] = field(default_factory=dict)
    runtime_outputs_dependency: Dict[str, Any] = field(default_factory=dict)
    future_s3_contract: Dict[str, Any] = field(default_factory=dict)
    cloudwatch_log_readiness: Dict[str, Any] = field(default_factory=dict)
    safe_failure_behavior: Dict[str, Any] = field(default_factory=dict)
    runtime_readiness: Dict[str, Any] = field(default_factory=dict)
    customer_safe: bool = True
    credential_values_exposed: bool = False
    provider_secret_values_visible: bool = False
    ffmpeg_composition_invoked: bool = False
    provider_calls_started: bool = False
    aws_calls_started: bool = False
    billing_credit_mutation_started: bool = False
    media_generation_started: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def backend_import_readiness() -> Dict[str, Any]:
    target = "backend.app.runtime.ecs_media_worker_execution_boundary"
    spec = importlib.util.find_spec(target)
    return {
        "target_module": target,
        "importable": spec is not None,
        "required_for_worker_image": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def ffmpeg_availability_check(ffmpeg_binary: str = "ffmpeg", probe_version: bool = False) -> Dict[str, Any]:
    """
    Cheap local availability contract.

    By default this only checks the PATH with shutil.which. `probe_version`
    exists as a future hook but is intentionally not executed here, so this
    function cannot run composition or a long ffmpeg command.
    """

    binary_path = shutil.which(ffmpeg_binary)
    available = bool(binary_path)
    return {
        "binary": ffmpeg_binary,
        "available": available,
        "binary_path_present": available,
        "binary_path": binary_path or "",
        "version_probe_requested": bool(probe_version),
        "version_probe_executed": False,
        "composition_probe_executed": False,
        "missing_ffmpeg_safe_status": "ffmpeg_missing_safe" if not available else "",
        "required_for_local_dev": False,
        "required_for_aws_worker_image": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_workdir_contract(workdir: Optional[str] = None) -> Dict[str, Any]:
    temp_root = Path(workdir or tempfile.gettempdir())
    return {
        "expected_workdir": str(temp_root),
        "exists": temp_root.exists(),
        "writable_hint": os.access(str(temp_root), os.W_OK) if temp_root.exists() else False,
        "write_probe_executed": False,
        "safe_to_use_for_temp_media": True,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_ffmpeg_worker_readiness_contract(
    env: Optional[Mapping[str, Any]] = None,
    ffmpeg_binary: str = "ffmpeg",
    workdir: Optional[str] = None,
) -> Dict[str, Any]:
    readiness = aws_option_a_readiness(env or {})
    ffmpeg = ffmpeg_availability_check(ffmpeg_binary=ffmpeg_binary, probe_version=False)

    contract = FfmpegWorkerReadinessContract(
        python_runtime={
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable_present": bool(sys.executable),
            "required_for_worker_image": True,
            "customer_safe": True,
        },
        backend_import_readiness=backend_import_readiness(),
        ffmpeg_availability=ffmpeg,
        workdir_contract=build_workdir_contract(workdir),
        input_output_mount_contract={
            "safe_input_sources": ["future_s3_signed_read", "local_dev_reference"],
            "safe_output_targets": ["future_s3_object_write", "local_dev_reference"],
            "raw_customer_files_not_logged": True,
            "local_mount_required_after_aws_cutover": False,
        },
        runtime_outputs_dependency={
            "runtime_outputs_allowed_for_local_dev": True,
            "runtime_outputs_required_after_aws_cutover": False,
            "replacement_after_cutover": "s3_asset_reference_contract",
        },
        future_s3_contract={
            "input_contract": "read source assets from S3/object references or signed URLs",
            "output_contract": "write composed media, previews, captions, thumbnails, transcripts, and evidence to S3/object references",
            "s3_calls_started": False,
            "requires_aws_credentials_now": False,
        },
        cloudwatch_log_readiness={
            "structured_worker_logs_required": True,
            "cloudwatch_log_group_configured": bool(readiness.get("cloudwatch_log_group")),
            "cloudwatch_calls_started": False,
            "secret_values_logged": False,
        },
        safe_failure_behavior={
            "missing_ffmpeg_blocks_live_composition": True,
            "missing_ffmpeg_crashes_process": False,
            "status_when_missing": "ffmpeg_missing_safe",
            "admin_action": "install ffmpeg in worker image before enabling composition",
            "client_message": "Media composition is not ready yet.",
        },
        runtime_readiness=readiness,
        ffmpeg_composition_invoked=False,
        provider_calls_started=False,
        aws_calls_started=False,
        billing_credit_mutation_started=False,
        media_generation_started=False,
    )
    return contract.to_dict()


def admin_ffmpeg_worker_readiness_view(readiness_or_env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = (
        dict(readiness_or_env or {})
        if "ffmpeg_availability" in dict(readiness_or_env or {})
        else build_ffmpeg_worker_readiness_contract(readiness_or_env)
    )
    return {
        **readiness,
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    }


def client_ffmpeg_worker_readiness_view(readiness_or_env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = (
        dict(readiness_or_env or {})
        if "ffmpeg_availability" in dict(readiness_or_env or {})
        else build_ffmpeg_worker_readiness_contract(readiness_or_env)
    )
    ffmpeg = dict(readiness.get("ffmpeg_availability") or {})
    return {
        "status": "composition_ready" if ffmpeg.get("available") else "composition_not_ready",
        "message": "Media composition is ready." if ffmpeg.get("available") else "Media composition is not ready yet.",
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }
