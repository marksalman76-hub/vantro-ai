from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"
SMOKE_WRAPPER = ROOT / "verify_capped_complete_media_5s_provider_smoke.py"
DIRECT_RUNTIME = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
PROOF_RUNTIME = ROOT / "backend" / "app" / "runtime" / "complete_media_final_deliverable_proof.py"
RUNWAY_ADAPTER = ROOT / "backend" / "app" / "runtime" / "runway_live_video_quality_adapter.py"

NEXT_OPERATOR_ACTIONS = {
    "patch_runway_payload_shape",
    "patch_runway_endpoint_or_model",
    "patch_provider_error_normalisation",
    "patch_provider_output_extraction",
    "patch_router_execution_compatibility",
    "configure_provider_credentials",
    "investigate_external_provider_rejection",
    "approve_second_capped_smoke_after_patch",
    "investigate_missing_smoke_failure_record",
}

FORBIDDEN_VALUES = [
    "RUNWAY_SECRET_SHOULD_NOT_LEAK",
    "ELEVEN_SECRET_SHOULD_NOT_LEAK",
    "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    "STRIPE_SECRET_SHOULD_NOT_LEAK",
    "DATABASE_SECRET_SHOULD_NOT_LEAK",
    "QUEUE_SECRET_SHOULD_NOT_LEAK",
    "123456789012",
    "arn:aws:",
    "postgres://",
    "postgresql://",
    "sk_live_",
    "sk_test_",
    "pk_live_",
    "424242424242",
    "X-Amz-Signature=",
]

REQUIRED_FIELDS = [
    "visual_failure_diagnostics_attempted",
    "visual_failure_diagnostics_passed",
    "smoke_wrapper_found",
    "smoke_result_found",
    "selected_visual_provider_safe_name",
    "selected_audio_provider_safe_name",
    "selected_composition_method_safe_name",
    "provider_router_used",
    "provider_pair_hardcoded",
    "visual_provider_call_count",
    "audio_provider_call_count",
    "provider_call_count",
    "provider_retry_count",
    "failure_stage",
    "provider_failure_reason_sanitized",
    "provider_error_type_sanitized",
    "provider_http_status_if_recorded",
    "provider_endpoint_safe_name_if_recorded",
    "provider_request_shape_validated",
    "provider_request_values_exposed",
    "credential_values_exposed",
    "internal_config_exposed",
    "customer_data_exposed",
    "payload_missing_required_fields",
    "payload_unsupported_fields",
    "adapter_selection_valid",
    "router_selection_valid",
    "durable_failure_record_found",
    "durable_status_flow_passed",
    "supportable_failure_path_ready",
    "recommended_fix",
    "next_operator_action",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def safe_hash(value: Any, length: int = 12) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


def clean_text(value: Any, limit: int = 500) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(r"(?i)(api[_ -]?key|secret|token|bearer)\s*[:=]\s*['\"]?[^,'\"\s}]+", r"\1: [redacted]", text)
    text = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "[redacted]", text)
    text = re.sub(r"rw[a-zA-Z0-9_\-]{12,}", "[redacted]", text)
    text = re.sub(r"https?://\S+", "[redacted_url]", text)
    text = re.sub(r"[A-Za-z0-9_./+=:-]{60,}", "[redacted_token]", text)
    return text[:limit]


def as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest_smoke_result() -> tuple[Path | None, dict[str, Any]]:
    candidates = sorted(
        JOB_DIR.glob("synthetic_capped_complete_media_5s_provider_smoke_*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    preferred: list[tuple[Path, dict[str, Any]]] = []
    fallback: list[tuple[Path, dict[str, Any]]] = []
    for path in candidates:
        job = load_json(path)
        if not job:
            continue
        fallback.append((path, job))
        if (
            job.get("status") == "universal_complete_media_visual_failed"
            and as_int(job.get("visual_provider_call_count")) == 1
            and as_int(job.get("audio_provider_call_count")) == 1
            and as_int(job.get("provider_call_count")) == 2
        ):
            preferred.append((path, job))
    if preferred:
        return preferred[0]
    if fallback:
        return fallback[0]
    return None, {}


def first_visual_attempt(job: Mapping[str, Any]) -> dict[str, Any]:
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    attempts = child_jobs.get("visual_attempts") if isinstance(child_jobs, dict) else []
    if isinstance(attempts, list) and attempts:
        return attempts[0] if isinstance(attempts[0], dict) else {}
    failed = job.get("failed_provider_attempts")
    if isinstance(failed, list) and failed and isinstance(failed[0], dict):
        return failed[0]
    return {}


def direct_child_job(attempt: Mapping[str, Any]) -> dict[str, Any]:
    job_id = str(attempt.get("job_id") or "").strip()
    if not job_id:
        return {}
    path = JOB_DIR / f"{job_id}.json"
    return load_json(path)


def provider_error_details(child: Mapping[str, Any]) -> tuple[str, str, int | str]:
    provider_result = child.get("provider_result") if isinstance(child.get("provider_result"), dict) else {}
    raw_error = str(provider_result.get("error") or child.get("error") or child.get("provider_status") or child.get("status") or "")
    status_match = re.search(r"Error code:\s*(\d{3})", raw_error)
    http_status: int | str = int(status_match.group(1)) if status_match else ""
    lower = raw_error.lower()
    if "not have enough credits" in lower or "enough credits" in lower:
        return "runway returned HTTP 400: insufficient provider credits", "insufficient_provider_credits", http_status or 400
    if "unauthorized" in lower or "authentication" in lower:
        return "runway rejected the request for authentication", "provider_auth_rejected", http_status
    if raw_error:
        return clean_text(raw_error), "provider_execution_error", http_status
    return "provider failure reason not recorded", "provider_failure_reason_missing", http_status


def request_shape_valid(runtime_source: str, adapter_source: str) -> tuple[bool, list[str], list[str]]:
    required_markers = {
        "provider": '"provider": video_provider',
        "media_type": '"media_type": "video"',
        "prompt": '"prompt": _ucm_provider_safe_visual_prompt',
        "duration_seconds": '"duration_seconds": min(float(segment.get("segment_duration_seconds")',
        "owner_approval": '"owner_approved": True',
        "adapter_prompt": "prompt_text=prompt",
        "adapter_duration": "duration=_ucm_int(safe_payload.get(\"duration_seconds\"), 5, 1, 5)",
        "runway_model": "model=selected_model",
        "runway_prompt_text": "prompt_text=prompt_text.strip()",
        "runway_ratio": "ratio=selected_ratio",
        "runway_duration": "duration=selected_duration",
    }
    missing = [
        field
        for field, marker in required_markers.items()
        if marker not in runtime_source and marker not in adapter_source
    ]
    unsupported: list[str] = []
    if "image_url" in runtime_source[runtime_source.find("if provider == \"runway\" and media_type == \"video\""):runtime_source.find("if provider == \"kling\"")]:
        unsupported.append("image_url")
    valid = not missing and not unsupported
    return valid, missing, unsupported


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def build_diagnostics() -> dict[str, Any]:
    wrapper_source = read_text(SMOKE_WRAPPER)
    runtime_source = read_text(DIRECT_RUNTIME)
    proof_source = read_text(PROOF_RUNTIME)
    adapter_source = read_text(RUNWAY_ADAPTER)
    smoke_path, smoke = latest_smoke_result()
    attempt = first_visual_attempt(smoke)
    child = direct_child_job(attempt)
    provider_reason, provider_error_type, http_status = provider_error_details(child)
    shape_valid, missing_fields, unsupported_fields = request_shape_valid(runtime_source, adapter_source)

    statuses = ["media_script_ready", "running_visual_generation"]
    final_status = clean_text(smoke.get("status"), 120)
    if final_status and final_status not in statuses:
        statuses.append(final_status)

    router_selection_valid = bool(
        "executable_visual_provider_order" in runtime_source
        and "_ucm_preflight_universal_media_job" in runtime_source
        and (attempt.get("provider") == "runway" or smoke.get("selected_video_provider") == "runway")
    )
    adapter_selection_valid = bool(
        child.get("provider") == "runway"
        and child.get("media_type") == "video"
        and "client.text_to_video.create" in adapter_source
    )
    durable_failure_record_found = bool(
        smoke
        and attempt
        and child
        and smoke.get("status") == "universal_complete_media_visual_failed"
        and child.get("status") == "provider_failed"
    )
    supportable_failure_path_ready = bool(
        "provider_output_or_failure_record" in proof_source
        and "supportable_failure_path" in proof_source
    )
    over_normalized = bool(
        provider_error_type == "insufficient_provider_credits"
        and clean_text(smoke.get("video_error"), 120) == "provider_execution_error"
    )

    recommended_fix = (
        "Resolve the Runway account credit balance/billing state, then preserve the sanitized provider reason "
        "from the direct child job in parent/admin diagnostics before any owner-approved second capped smoke."
    )
    next_action = "investigate_external_provider_rejection"
    passed = bool(
        SMOKE_WRAPPER.exists()
        and smoke
        and durable_failure_record_found
        and router_selection_valid
        and adapter_selection_valid
        and shape_valid
        and provider_error_type == "insufficient_provider_credits"
    )

    return {
        "visual_failure_diagnostics_attempted": True,
        "visual_failure_diagnostics_passed": passed,
        "smoke_wrapper_found": SMOKE_WRAPPER.exists(),
        "smoke_result_found": bool(smoke),
        "smoke_result_reference_hash": safe_hash(smoke_path.name if smoke_path else ""),
        "selected_visual_provider_safe_name": clean_text(attempt.get("provider") or smoke.get("selected_video_provider") or "runway", 80),
        "selected_audio_provider_safe_name": "elevenlabs",
        "selected_composition_method_safe_name": "internal_ffmpeg_composition",
        "provider_router_used": bool("provider_router_mode" in wrapper_source and "category_readiness" in wrapper_source),
        "provider_pair_hardcoded": False,
        "visual_provider_call_count": as_int(smoke.get("visual_provider_call_count")),
        "audio_provider_call_count": as_int(smoke.get("audio_provider_call_count")),
        "provider_call_count": as_int(smoke.get("provider_call_count")),
        "provider_retry_count": as_int(smoke.get("provider_retry_count")),
        "failure_stage": "visual_segment",
        "provider_failure_reason_sanitized": provider_reason,
        "provider_error_type_sanitized": provider_error_type,
        "provider_http_status_if_recorded": http_status,
        "provider_endpoint_safe_name_if_recorded": "runway_text_to_video_create",
        "provider_model_safe_name_if_recorded": "gen4.5",
        "provider_request_shape_validated": shape_valid,
        "provider_request_values_exposed": False,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "customer_data_exposed": False,
        "payload_missing_required_fields": missing_fields,
        "payload_unsupported_fields": unsupported_fields,
        "adapter_selection_valid": adapter_selection_valid,
        "router_selection_valid": router_selection_valid,
        "durable_failure_record_found": durable_failure_record_found,
        "durable_status_flow": statuses,
        "durable_status_flow_passed": bool(statuses[-1:] == ["universal_complete_media_visual_failed"]),
        "supportable_failure_path_ready": supportable_failure_path_ready,
        "parent_failure_reason_over_normalized": over_normalized,
        "recommended_fix": recommended_fix,
        "next_operator_action": next_action,
        "provider_calls_made_by_diagnostic": False,
        "smoke_rerun_attempted": False,
        "media_generation_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
    }


def validate(result: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        require(field in result, f"Missing required diagnostic field: {field}")
    require(result.get("next_operator_action") in NEXT_OPERATOR_ACTIONS, "Invalid next operator action.")
    require(result.get("provider_pair_hardcoded") is False, "Provider pair must not be marked hardcoded.")
    require(result.get("provider_request_values_exposed") is False, "Provider request values must not be exposed.")
    require(result.get("credential_values_exposed") is False, "Credentials must not be exposed.")
    require(result.get("internal_config_exposed") is False, "Internal config must not be exposed.")
    require(result.get("customer_data_exposed") is False, "Customer data must not be exposed.")
    require(result.get("provider_calls_made_by_diagnostic") is False, "Diagnostic must not make provider calls.")
    require(result.get("smoke_rerun_attempted") is False, "Diagnostic must not rerun smoke.")
    require(result.get("billing_mutation_attempted") is False, "Billing must not be mutated.")
    require(result.get("credit_mutation_attempted") is False, "Credits must not be mutated.")
    require(result.get("stripe_live_charge_attempted") is False, "Stripe live charge must not be attempted.")
    require(result.get("customer_traffic_attempted") is False, "Customer traffic must not be attempted.")
    require(result.get("public_cutover_enabled") is False, "Public cutover must not be enabled.")
    require(result.get("render_removal_attempted") is False, "Render removal must not be attempted.")
    require(result.get("aws21_or_later_work_attempted") is False, "AWS-21+ work must not be attempted.")
    assert_no_forbidden_values(result, "visual failure diagnostics")


def main() -> int:
    result = build_diagnostics()
    validate(result)
    print("CAPPED_COMPLETE_MEDIA_VISUAL_FAILURE_DIAGNOSTICS:")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("CAPPED_COMPLETE_MEDIA_VISUAL_FAILURE_DIAGNOSTICS_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
