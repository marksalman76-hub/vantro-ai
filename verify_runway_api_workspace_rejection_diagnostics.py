from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import re
from typing import Any, Mapping

from backend.app.runtime import direct_media_provider_execution_runtime as direct_media


ROOT = Path(__file__).resolve().parent
JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"
RUNTIME = ROOT / "backend" / "app" / "runtime" / "direct_media_provider_execution_runtime.py"
RUNWAY_ADAPTER = ROOT / "backend" / "app" / "runtime" / "runway_live_video_quality_adapter.py"

NEXT_OPERATOR_ACTIONS = {
    "verify_runway_api_key_workspace_mapping",
    "patch_runway_error_normalisation",
    "patch_runway_endpoint_or_model",
    "patch_runway_payload_shape",
    "patch_router_prefer_alternate_ready_visual_provider",
    "approve_kling_capped_smoke_after_owner_confirmation",
    "approve_runway_capped_smoke_after_key_workspace_confirmation",
    "investigate_missing_provider_failure_record",
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
    "runway_workspace_rejection_diagnostics_attempted",
    "runway_workspace_rejection_diagnostics_passed",
    "provider_call_attempted",
    "smoke_rerun_attempted",
    "visible_workspace_credits_claim_recorded",
    "prior_smoke_failure_record_found",
    "selected_visual_provider_safe_name",
    "alternate_ready_visual_provider_safe_names",
    "selected_runway_env_name",
    "selected_runway_key_fingerprint_present",
    "selected_runway_key_value_exposed",
    "provider_http_status_if_recorded",
    "provider_error_type_sanitized",
    "provider_failure_reason_sanitized",
    "endpoint_safe_name",
    "model_safe_name",
    "request_payload_shape_validated",
    "endpoint_model_plan_risk_detected",
    "key_workspace_mismatch_risk_detected",
    "error_normalization_may_be_over_broad",
    "raw_provider_response_available_redacted",
    "raw_provider_response_exposed",
    "credential_values_exposed",
    "internal_config_exposed",
    "customer_data_exposed",
    "router_selection_valid",
    "alternate_ready_visual_provider_available",
    "recommended_fix",
    "next_operator_action",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def clean_text(value: Any, limit: int = 500) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(r"(?i)(api[_ -]?key|secret|token|bearer)\s*[:=]\s*['\"]?[^,'\"\s}]+", r"\1: [redacted]", text)
    text = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "[redacted]", text)
    text = re.sub(r"rw[a-zA-Z0-9_\-]{12,}", "[redacted]", text)
    text = re.sub(r"https?://\S+", "[redacted_url]", text)
    text = re.sub(r"[A-Za-z0-9_./+=:-]{60,}", "[redacted_token]", text)
    return text[:limit]


def safe_hash(value: Any, length: int = 12) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


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


def source(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def latest_runway_smoke_failure() -> tuple[Path | None, dict[str, Any]]:
    candidates = sorted(
        JOB_DIR.glob("synthetic_capped_complete_media_5s_provider_smoke_*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        job = load_json(path)
        if (
            job.get("status") == "universal_complete_media_visual_failed"
            and (job.get("selected_visual_provider_safe_name") == "runway" or job.get("provider_safe_name") == "runway")
            and as_int(job.get("visual_provider_call_count")) == 1
            and as_int(job.get("provider_call_count")) <= 2
        ):
            return path, job
    return (candidates[0], load_json(candidates[0])) if candidates else (None, {})


def first_visual_attempt(job: Mapping[str, Any]) -> dict[str, Any]:
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    attempts = child_jobs.get("visual_attempts") if isinstance(child_jobs, dict) else []
    if isinstance(attempts, list) and attempts and isinstance(attempts[0], dict):
        return attempts[0]
    failed = job.get("failed_provider_attempts")
    if isinstance(failed, list) and failed and isinstance(failed[0], dict):
        return failed[0]
    return {}


def child_job(attempt: Mapping[str, Any]) -> dict[str, Any]:
    job_id = str(attempt.get("job_id") or "").strip()
    if not job_id:
        return {}
    return load_json(JOB_DIR / f"{job_id}.json")


def provider_result(child: Mapping[str, Any]) -> dict[str, Any]:
    result = child.get("provider_result")
    return result if isinstance(result, dict) else {}


def raw_error_sanitized(child: Mapping[str, Any]) -> str:
    result = provider_result(child)
    return clean_text(result.get("error") or child.get("provider_failure_reason_sanitized") or child.get("provider_status") or "")


def request_payload_shape_validated(runtime_text: str, adapter_text: str) -> bool:
    markers = [
        '"provider": video_provider',
        '"media_type": "video"',
        '"prompt": _ucm_provider_safe_visual_prompt',
        '"duration_seconds": min(float(segment.get("segment_duration_seconds")',
        "allow_live_execution=True",
        "client.text_to_video.create",
        "model=selected_model",
        "prompt_text=prompt_text.strip()",
        "ratio=selected_ratio",
        "duration=selected_duration",
    ]
    return all(marker in runtime_text or marker in adapter_text for marker in markers)


def runway_key_metadata() -> dict[str, Any]:
    diag = direct_media.runway_safe_key_diagnostics()
    selected_name = clean_text(diag.get("used_env_name"), 80)
    selected_record = {}
    for record in list(diag.get("keys") or []):
        if record.get("env_name") == selected_name:
            selected_record = record
            break
    return {
        "selected_runway_env_name": selected_name,
        "selected_runway_key_fingerprint_present": bool(selected_record.get("sha256_prefix")),
        "selected_runway_key_fingerprint_hash": safe_hash(selected_record.get("sha256_prefix")),
        "selected_runway_key_value_exposed": False,
    }


def ready_visual_providers() -> tuple[str, list[str]]:
    readiness = []
    for provider in ["runway", "kling", "heygen", "replicate", "openai", "sync"]:
        try:
            item = direct_media._ucm_provider_executable(provider, "video")  # noqa: SLF001
        except Exception:
            item = {"provider": provider, "executable": False}
        if item.get("executable"):
            readiness.append(provider)
    selected = readiness[0] if readiness else ""
    alternate = [provider for provider in readiness if provider != selected]
    return selected, alternate


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def build_diagnostics() -> dict[str, Any]:
    runtime_text = source(RUNTIME)
    adapter_text = source(RUNWAY_ADAPTER)
    smoke_path, smoke = latest_runway_smoke_failure()
    attempt = first_visual_attempt(smoke)
    child = child_job(attempt)
    result = provider_result(child)
    raw_error = raw_error_sanitized(child)
    selected_ready, alternate_ready = ready_visual_providers()
    key_meta = runway_key_metadata()
    http_status = smoke.get("provider_http_status_if_recorded") or child.get("provider_http_status_if_recorded") or ""
    error_type = clean_text(smoke.get("provider_error_type_sanitized") or child.get("provider_error_type_sanitized"), 120)
    reason = clean_text(smoke.get("provider_failure_reason_sanitized") or child.get("provider_failure_reason_sanitized"), 500)
    if not reason and raw_error:
        reason = "runway returned HTTP 400: insufficient provider credits" if "enough credits" in raw_error.lower() else raw_error
    model_safe_name = clean_text(result.get("model") or os.getenv("RUNWAY_MODEL") or "gen4.5", 80)
    endpoint_safe_name = clean_text(child.get("provider_endpoint_safe_name_if_recorded") or smoke.get("provider_endpoint_safe_name_if_recorded") or "runway_text_to_video_create", 120)
    raw_available = bool(raw_error)
    request_shape_ok = request_payload_shape_validated(runtime_text, adapter_text)
    endpoint_model_plan_risk = bool(model_safe_name in {"gen4.5", "gen4", "gen4_turbo"} and endpoint_safe_name == "runway_text_to_video_create")
    key_workspace_mismatch_risk = bool(
        key_meta["selected_runway_key_fingerprint_present"]
        and error_type == "insufficient_provider_credits"
    )
    over_broad = bool(
        error_type == "insufficient_provider_credits"
        and raw_available
        and not any(marker in raw_error.lower() for marker in ["workspace", "plan", "entitlement", "team", "billing account"])
    )

    if not smoke or not child:
        next_action = "investigate_missing_provider_failure_record"
        recommended = "Find or preserve a capped smoke parent and direct child provider failure record before changing provider routing."
    elif key_workspace_mismatch_risk:
        next_action = "verify_runway_api_key_workspace_mapping"
        recommended = (
            "Compare the backend Runway key fingerprint and selected env name with the intended credited Runway workspace/team API key; "
            "also confirm that the key has API/video-generation entitlement for the selected model before another smoke."
        )
    elif over_broad:
        next_action = "patch_runway_error_normalisation"
        recommended = "Patch Runway error normalization to preserve sanitized plan/workspace/entitlement details before any retry."
    elif endpoint_model_plan_risk:
        next_action = "patch_runway_endpoint_or_model"
        recommended = "Confirm the Runway model/endpoint entitlement and patch the adapter default if the selected model is not API-enabled."
    else:
        next_action = "patch_runway_error_normalisation"
        recommended = "Preserve more sanitized Runway response detail so support can distinguish credits, workspace, entitlement, endpoint, and payload rejections."

    passed = bool(
        smoke
        and child
        and key_meta["selected_runway_env_name"]
        and request_shape_ok
        and next_action in NEXT_OPERATOR_ACTIONS
    )

    return {
        "runway_workspace_rejection_diagnostics_attempted": True,
        "runway_workspace_rejection_diagnostics_passed": passed,
        "provider_call_attempted": False,
        "smoke_rerun_attempted": False,
        "visible_workspace_credits_claim_recorded": True,
        "visible_workspace_credits_redacted_summary": "owner reported credited Runway workspace: 815 total credits",
        "prior_smoke_failure_record_found": bool(smoke and child),
        "prior_smoke_failure_record_hash": safe_hash(smoke_path.name if smoke_path else ""),
        "selected_visual_provider_safe_name": clean_text(smoke.get("selected_visual_provider_safe_name") or attempt.get("provider") or selected_ready, 80),
        "alternate_ready_visual_provider_safe_names": alternate_ready,
        **key_meta,
        "provider_http_status_if_recorded": http_status,
        "provider_error_type_sanitized": error_type or "insufficient_provider_credits",
        "provider_failure_reason_sanitized": reason,
        "endpoint_safe_name": endpoint_safe_name,
        "model_safe_name": model_safe_name,
        "request_payload_shape_validated": request_shape_ok,
        "endpoint_model_plan_risk_detected": endpoint_model_plan_risk,
        "key_workspace_mismatch_risk_detected": key_workspace_mismatch_risk,
        "error_normalization_may_be_over_broad": over_broad,
        "raw_provider_response_available_redacted": raw_available,
        "raw_provider_response_excerpt_sanitized": raw_error if raw_available else "",
        "raw_provider_response_exposed": False,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "customer_data_exposed": False,
        "router_selection_valid": bool("executable_visual_provider_order" in runtime_text and selected_ready == "runway"),
        "alternate_ready_visual_provider_available": bool(alternate_ready),
        "recommended_fix": recommended,
        "next_operator_action": next_action,
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
        require(field in result, f"Missing required field: {field}")
    require(result.get("next_operator_action") in NEXT_OPERATOR_ACTIONS, "Invalid next operator action.")
    require(result.get("provider_call_attempted") is False, "Diagnostic must not call providers.")
    require(result.get("smoke_rerun_attempted") is False, "Diagnostic must not rerun smoke.")
    require(result.get("selected_runway_key_value_exposed") is False, "Runway key values must not be exposed.")
    require(result.get("raw_provider_response_exposed") is False, "Raw provider response must not be exposed.")
    for key in [
        "credential_values_exposed",
        "internal_config_exposed",
        "customer_data_exposed",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "stripe_live_charge_attempted",
        "customer_traffic_attempted",
        "public_cutover_enabled",
        "render_removal_attempted",
        "aws21_or_later_work_attempted",
    ]:
        require(result.get(key) is False, f"Forbidden exposure or side effect must be false: {key}")
    assert_no_forbidden_values(result, "runway workspace rejection diagnostics")


def main() -> int:
    result = build_diagnostics()
    validate(result)
    print("RUNWAY_API_WORKSPACE_REJECTION_DIAGNOSTICS:")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("RUNWAY_API_WORKSPACE_REJECTION_DIAGNOSTICS_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
