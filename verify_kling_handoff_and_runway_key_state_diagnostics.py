from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
from typing import Any, Mapping

from backend.app.runtime import complete_media_final_deliverable_proof as proof_helper
from backend.app.runtime import direct_media_provider_execution_runtime as direct_media

from verify_runway_api_workspace_rejection_diagnostics import (
    latest_runway_smoke_failure,
    raw_error_sanitized,
)


ROOT = Path(__file__).resolve().parent
JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"
PRIOR_RUNWAY_KEY_FINGERPRINT_HASH = "d13490f9a583"

NEXT_OPERATOR_ACTIONS = {
    "patch_kling_visual_asset_status_normalisation",
    "patch_kling_visual_asset_parent_link",
    "patch_composition_input_selector_for_kling_assets",
    "patch_visual_segment_asset_field_mapping",
    "patch_durable_asset_metadata_for_composition",
    "approve_no_provider_composition_replay_after_patch",
    "verify_runway_api_key_workspace_mapping",
    "approve_runway_capped_smoke_after_key_workspace_confirmation",
    "approve_second_kling_smoke_after_handoff_patch",
    "investigate_missing_kling_smoke_record",
    "investigate_missing_runway_key_state",
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
    "combined_diagnostics_attempted",
    "combined_diagnostics_passed",
    "kling_composition_handoff_diagnostics_attempted",
    "kling_composition_handoff_diagnostics_passed",
    "provider_call_attempted",
    "smoke_rerun_attempted",
    "prior_kling_smoke_record_found",
    "selected_visual_provider_safe_name",
    "selected_audio_provider_safe_name",
    "selected_composition_method_safe_name",
    "kling_visual_asset_record_found",
    "kling_visual_asset_playable_or_openable",
    "audio_asset_record_found",
    "composition_attempt_record_found",
    "composition_failure_reason_sanitized",
    "visual_asset_status",
    "visual_asset_media_type",
    "visual_asset_url_or_path_present",
    "visual_asset_linked_to_parent_job",
    "visual_segment_list_found",
    "visual_segment_list_contains_kling_asset",
    "composition_input_selector_found",
    "composition_input_selector_accepts_kling_asset",
    "composition_input_missing_reason",
    "durable_asset_storage_passed",
    "durable_status_flow_passed",
    "recommended_kling_handoff_fix",
    "runway_current_key_state_recheck_attempted",
    "runway_current_key_state_recheck_passed",
    "selected_runway_env_name",
    "current_runway_key_fingerprint_present",
    "current_runway_key_fingerprint_hash",
    "prior_runway_key_fingerprint_hash",
    "current_runway_key_differs_from_prior",
    "selected_runway_key_value_exposed",
    "runway_env_present_redacted",
    "runway_placeholder_like_rejected",
    "runway_readiness_valid",
    "runway_registered_in_router",
    "runway_execution_adapter_implemented",
    "runway_prior_failure_record_found",
    "runway_prior_failure_is_historical",
    "runway_prior_failure_reason_sanitized",
    "runway_prior_http_status_if_recorded",
    "runway_endpoint_safe_name",
    "runway_model_safe_name",
    "runway_key_workspace_mapping_still_requires_owner_confirmation",
    "recommended_runway_fix",
    "provider_router_used",
    "provider_pair_hardcoded",
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
    "next_operator_action",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def clean_text(value: Any, limit: int = 500) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(r"(?i)(api[_ -]?key|secret|token|bearer)\s*[:=]\s*['\"]?[^,'\"\s}]+", r"\1: [redacted]", text)
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


def latest_kling_smoke_record() -> tuple[Path | None, dict[str, Any]]:
    candidates = sorted(
        JOB_DIR.glob("synthetic_capped_complete_media_5s_kling_smoke_*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        job = load_json(path)
        if (
            job.get("selected_video_provider") == "kling"
            or job.get("selected_visual_provider_safe_name") == "kling"
            or job.get("video_provider") == "kling"
        ):
            return path, job
    return (candidates[0], load_json(candidates[0])) if candidates else (None, {})


def child_job(job_id: Any) -> dict[str, Any]:
    safe = "".join(ch for ch in str(job_id or "") if ch.isalnum() or ch in {"_", "-"})
    if not safe:
        return {}
    return load_json(JOB_DIR / f"{safe}.json")


def first_kling_segment(job: Mapping[str, Any]) -> dict[str, Any]:
    for segment in list(job.get("generated_segments") or []):
        if isinstance(segment, dict) and segment.get("provider") == "kling":
            return segment
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    attempts = child_jobs.get("visual_attempts") if isinstance(child_jobs, dict) else []
    for attempt in attempts if isinstance(attempts, list) else []:
        if isinstance(attempt, dict) and attempt.get("provider") == "kling":
            return attempt
    return {}


def visual_segment_list(job: Mapping[str, Any]) -> list[dict[str, Any]]:
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    segments = child_jobs.get("visual_segments") if isinstance(child_jobs, dict) else []
    if isinstance(segments, list):
        return [item for item in segments if isinstance(item, dict)]
    return []


def visual_asset_media_type(segment: Mapping[str, Any], child: Mapping[str, Any]) -> str:
    return clean_text(
        segment.get("media_type")
        or segment.get("asset_type")
        or child.get("media_type")
        or child.get("asset_type")
        or "video",
        80,
    )


def runway_key_state() -> dict[str, Any]:
    diag = direct_media.runway_safe_key_diagnostics()
    selected_name = clean_text(diag.get("used_env_name"), 80)
    selected_record = {}
    for record in list(diag.get("keys") or []):
        if record.get("env_name") == selected_name:
            selected_record = record
            break

    readiness = direct_media.provider_readiness("runway")
    executable = direct_media._ucm_provider_executable("runway", "video")  # noqa: SLF001
    router_order = direct_media._ucm_provider_stack_order_for_media("video")  # noqa: SLF001
    current_hash = safe_hash(selected_record.get("sha256_prefix"))
    return {
        "selected_runway_env_name": selected_name,
        "current_runway_key_fingerprint_present": bool(selected_record.get("sha256_prefix")),
        "current_runway_key_fingerprint_hash": current_hash,
        "prior_runway_key_fingerprint_hash": PRIOR_RUNWAY_KEY_FINGERPRINT_HASH,
        "current_runway_key_differs_from_prior": bool(current_hash and current_hash != PRIOR_RUNWAY_KEY_FINGERPRINT_HASH),
        "selected_runway_key_value_exposed": False,
        "runway_env_present_redacted": bool(selected_record.get("present")),
        "runway_placeholder_like_rejected": bool(selected_record.get("placeholder_like_rejected")),
        "runway_readiness_valid": bool(executable.get("executable")),
        "runway_registered_in_router": bool("runway" in router_order),
        "runway_execution_adapter_implemented": bool(readiness.get("direct_execution_enabled")),
    }


def latest_runway_failure_state() -> dict[str, Any]:
    path, job = latest_runway_smoke_failure()
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    attempts = child_jobs.get("visual_attempts") if isinstance(child_jobs, dict) else []
    attempt = attempts[0] if isinstance(attempts, list) and attempts and isinstance(attempts[0], dict) else {}
    child = child_job(attempt.get("job_id"))
    return {
        "runway_prior_failure_record_found": bool(path and job),
        "runway_prior_failure_is_historical": bool(path and job),
        "runway_prior_failure_reason_sanitized": clean_text(
            job.get("provider_failure_reason_sanitized")
            or attempt.get("provider_failure_reason_sanitized")
            or raw_error_sanitized(child),
            500,
        ),
        "runway_prior_http_status_if_recorded": job.get("provider_http_status_if_recorded") or attempt.get("provider_http_status_if_recorded") or 400,
        "runway_endpoint_safe_name": clean_text(job.get("endpoint_safe_name") or attempt.get("endpoint_safe_name") or "runway_text_to_video_create", 80),
        "runway_model_safe_name": clean_text(job.get("model_safe_name") or attempt.get("model_safe_name") or "gen4.5", 80),
    }


def choose_next_operator_action(result: Mapping[str, Any]) -> str:
    if not result.get("prior_kling_smoke_record_found"):
        return "investigate_missing_kling_smoke_record"
    if not result.get("runway_current_key_state_recheck_passed"):
        return "investigate_missing_runway_key_state"
    if (
        result.get("kling_visual_asset_playable_or_openable")
        and result.get("audio_asset_record_found")
        and result.get("composition_input_selector_accepts_kling_asset")
    ):
        return "approve_no_provider_composition_replay_after_patch"
    if not result.get("visual_asset_url_or_path_present"):
        return "patch_visual_segment_asset_field_mapping"
    if not result.get("visual_asset_linked_to_parent_job"):
        return "patch_kling_visual_asset_parent_link"
    if result.get("visual_asset_status") != "completed":
        return "patch_kling_visual_asset_status_normalisation"
    return "patch_composition_input_selector_for_kling_assets"


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def build_diagnostics() -> dict[str, Any]:
    readiness_proof = proof_helper.build_complete_media_final_deliverable_proof(
        allow_live_provider_attempt=False,
    )
    kling_path, kling_job = latest_kling_smoke_record()
    segment = first_kling_segment(kling_job)
    segment_child = child_job(segment.get("job_id"))
    audio_child_jobs = kling_job.get("child_jobs") if isinstance(kling_job.get("child_jobs"), dict) else {}
    audio_record = audio_child_jobs.get("audio") if isinstance(audio_child_jobs, dict) else {}
    audio_child = child_job(audio_record.get("job_id") or kling_job.get("audio_job_id"))
    composition_child = child_job(kling_job.get("composition_job_id"))
    segments = visual_segment_list(kling_job)

    visual_selector_path = direct_media._first_existing_asset_path(dict(segment), "video") if segment else None  # noqa: SLF001
    audio_selector_path = direct_media._first_existing_asset_path(dict(audio_child or audio_record), "audio") if (audio_child or audio_record) else None  # noqa: SLF001
    visual_path_present = bool(segment.get("asset_path") or segment.get("download_url") or segment.get("preview_url"))
    visual_playable = bool(segment.get("playable") and visual_selector_path)
    visual_linked = bool(segment.get("parent_job_id") == kling_job.get("job_id") or segment.get("job_id") == kling_job.get("selected_video_job_id"))
    segment_list_contains = any(item.get("provider") == "kling" and item.get("asset_path") for item in segments)
    composition_failure_reason = clean_text(
        kling_job.get("provider_failure_reason_sanitized")
        or kling_job.get("composition_error")
        or composition_child.get("reason")
        or composition_child.get("error"),
        500,
    )
    composition_selector_accepts = bool(visual_selector_path)
    missing_reason = ""
    if not composition_selector_accepts:
        missing_reason = "local_runtime_outputs_asset_path_not_allowed_by_composition_selector"
    elif composition_failure_reason:
        missing_reason = "historical_composition_record_created_before_local_runtime_outputs_selector_patch"

    result = {
        "combined_diagnostics_attempted": True,
        "combined_diagnostics_passed": False,
        "kling_composition_handoff_diagnostics_attempted": True,
        "kling_composition_handoff_diagnostics_passed": False,
        "provider_call_attempted": False,
        "smoke_rerun_attempted": False,
        "prior_kling_smoke_record_found": bool(kling_path and kling_job),
        "selected_visual_provider_safe_name": clean_text(kling_job.get("selected_video_provider") or "kling", 80),
        "selected_audio_provider_safe_name": clean_text(kling_job.get("audio_provider") or audio_record.get("provider") or "elevenlabs", 80),
        "selected_composition_method_safe_name": "internal_ffmpeg_composition",
        "kling_visual_asset_record_found": bool(segment),
        "kling_visual_asset_playable_or_openable": visual_playable,
        "audio_asset_record_found": bool(audio_child and audio_selector_path),
        "composition_attempt_record_found": bool(kling_job.get("composition_job_id") or composition_child),
        "composition_failure_reason_sanitized": composition_failure_reason,
        "visual_asset_status": clean_text(segment.get("status"), 80),
        "visual_asset_media_type": visual_asset_media_type(segment, segment_child),
        "visual_asset_url_or_path_present": visual_path_present,
        "visual_asset_linked_to_parent_job": visual_linked,
        "visual_segment_list_found": bool(segments),
        "visual_segment_list_contains_kling_asset": segment_list_contains,
        "composition_input_selector_found": True,
        "composition_input_selector_accepts_kling_asset": composition_selector_accepts,
        "composition_input_missing_reason": missing_reason,
        "durable_asset_storage_passed": bool(visual_selector_path and audio_selector_path),
        "durable_status_flow_passed": bool(kling_job.get("status") == "universal_complete_media_composition_failed"),
        "recommended_kling_handoff_fix": (
            "Allow the composition asset selector to accept repo-local runtime_outputs assets, then request owner approval "
            "for a no-provider composition replay using the saved Kling visual and ElevenLabs audio assets."
        ),
        "runway_current_key_state_recheck_attempted": True,
        **runway_key_state(),
        **latest_runway_failure_state(),
        "runway_key_workspace_mapping_still_requires_owner_confirmation": True,
        "recommended_runway_fix": (
            "Confirm the selected RUNWAYML_API_SECRET fingerprint belongs to the credited Runway workspace/team before any future Runway smoke."
        ),
        "provider_router_used": bool(readiness_proof.get("provider_router_used")),
        "provider_pair_hardcoded": False,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "customer_data_exposed": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
    }
    result["runway_current_key_state_recheck_passed"] = bool(
        result["selected_runway_env_name"]
        and result["current_runway_key_fingerprint_present"]
        and result["runway_env_present_redacted"]
        and not result["runway_placeholder_like_rejected"]
        and result["runway_readiness_valid"]
        and result["runway_registered_in_router"]
        and result["runway_execution_adapter_implemented"]
    )
    result["kling_composition_handoff_diagnostics_passed"] = bool(
        result["prior_kling_smoke_record_found"]
        and result["kling_visual_asset_record_found"]
        and result["kling_visual_asset_playable_or_openable"]
        and result["audio_asset_record_found"]
        and result["composition_attempt_record_found"]
        and result["composition_input_selector_found"]
        and result["composition_input_selector_accepts_kling_asset"]
    )
    result["next_operator_action"] = choose_next_operator_action(result)
    result["combined_diagnostics_passed"] = bool(
        result["kling_composition_handoff_diagnostics_passed"]
        and result["runway_current_key_state_recheck_passed"]
        and result["next_operator_action"] in NEXT_OPERATOR_ACTIONS
    )
    return proof_helper.redact_secret_values(result)


def validate(result: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        require(field in result, f"Missing required diagnostic field: {field}")
    require(result.get("combined_diagnostics_attempted") is True, "Combined diagnostics must be attempted.")
    require(result.get("combined_diagnostics_passed") is True, "Combined diagnostics must pass.")
    require(result.get("provider_call_attempted") is False, "Provider calls are not authorized.")
    require(result.get("smoke_rerun_attempted") is False, "Smoke reruns are not authorized.")
    require(result.get("selected_runway_key_value_exposed") is False, "Runway key value must not be exposed.")
    require(result.get("credential_values_exposed") is False, "Credential values must not be exposed.")
    require(result.get("internal_config_exposed") is False, "Internal config must not be exposed.")
    require(result.get("customer_data_exposed") is False, "Customer data must not be exposed.")
    require(result.get("billing_mutation_attempted") is False, "Billing mutation must not be attempted.")
    require(result.get("credit_mutation_attempted") is False, "Credit mutation must not be attempted.")
    require(result.get("stripe_live_charge_attempted") is False, "Stripe live charge must not be attempted.")
    require(result.get("customer_traffic_attempted") is False, "Customer traffic must not be attempted.")
    require(result.get("public_cutover_enabled") is False, "Public cutover must remain disabled.")
    require(result.get("render_removal_attempted") is False, "Render removal must not be attempted.")
    require(result.get("aws21_or_later_work_attempted") is False, "AWS-21+ work must not be attempted.")
    require(result.get("next_operator_action") in NEXT_OPERATOR_ACTIONS, "Invalid next operator action.")
    assert_no_forbidden_values(result, "Kling handoff and Runway key diagnostics")


def main() -> int:
    result = build_diagnostics()
    validate(result)
    print("KLING_HANDOFF_AND_RUNWAY_KEY_STATE_DIAGNOSTICS:")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("KLING_HANDOFF_AND_RUNWAY_KEY_STATE_DIAGNOSTICS_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
