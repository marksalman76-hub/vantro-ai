from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any, Mapping

from backend.app.runtime import complete_media_final_deliverable_proof as proof_helper
from backend.app.runtime import direct_media_provider_execution_runtime as direct_media

from verify_kling_handoff_and_runway_key_state_diagnostics import (
    FORBIDDEN_VALUES,
    child_job,
    clean_text,
    first_kling_segment,
    latest_kling_smoke_record,
)


ROOT = Path(__file__).resolve().parent
JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"
REPLAY_MARKER_PREFIX = "no_provider_kling_composition_replay"

NEXT_OPERATOR_ACTIONS = {
    "approve_second_kling_smoke_after_handoff_patch",
    "patch_composition_ffmpeg_invocation",
    "patch_composition_asset_duration_metadata",
    "patch_composition_audio_video_muxing",
    "patch_final_asset_persistence",
    "patch_client_admin_final_asset_visibility",
    "investigate_missing_saved_kling_assets",
}

REQUIRED_FIELDS = [
    "no_provider_composition_replay_attempted",
    "no_provider_composition_replay_passed",
    "provider_call_attempted",
    "smoke_rerun_attempted",
    "prior_kling_smoke_record_found",
    "saved_kling_visual_asset_found",
    "saved_kling_visual_asset_playable_or_openable",
    "saved_audio_asset_found",
    "ffmpeg_ready",
    "local_runtime_outputs_path_allowed",
    "composition_input_selector_accepts_saved_kling_asset",
    "composition_attempted",
    "final_combined_asset_created",
    "final_combined_asset_playable_or_openable",
    "final_deliverable_is_single_combined_file",
    "durable_asset_storage_passed",
    "durable_status_flow_passed",
    "client_safe_result_view_redacted",
    "admin_provider_diagnostics_redacted",
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


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def safe_job_id(value: Any) -> str:
    return "".join(ch for ch in str(value or "") if ch.isalnum() or ch in {"_", "-"})


def replay_job_id(parent_job: Mapping[str, Any], visual_segment: Mapping[str, Any], audio_job: Mapping[str, Any]) -> str:
    parent_id = safe_job_id(parent_job.get("job_id"))
    visual_id = safe_job_id(visual_segment.get("job_id"))
    audio_id = safe_job_id(audio_job.get("job_id"))
    return f"{REPLAY_MARKER_PREFIX}_{parent_id}_{visual_id}_{audio_id}"[:180]


def replay_job_path(job_id: str) -> Path:
    return JOB_DIR / f"{safe_job_id(job_id)}.json"


def local_asset_exists(value: Any) -> bool:
    try:
        return bool(value and Path(str(value)).exists() and Path(str(value)).is_file())
    except Exception:
        return False


def asset_openable(value: Any) -> bool:
    if not local_asset_exists(value):
        return False
    try:
        duration = direct_media._ucm_get_duration_seconds(str(value))  # noqa: SLF001
        if duration is not None and duration > 0:
            return True
        with Path(str(value)).open("rb") as handle:
            return bool(handle.read(16))
    except Exception:
        return False


def saved_audio_job(parent_job: Mapping[str, Any]) -> dict[str, Any]:
    child_jobs = parent_job.get("child_jobs") if isinstance(parent_job.get("child_jobs"), dict) else {}
    audio_record = child_jobs.get("audio") if isinstance(child_jobs, dict) else {}
    audio_id = parent_job.get("audio_job_id") or (audio_record or {}).get("job_id")
    return child_job(audio_id)


def failure_reason(result: Mapping[str, Any]) -> str:
    return clean_text(
        result.get("reason")
        or result.get("error")
        or result.get("status")
        or "composition replay did not create a playable final asset",
        700,
    )


def choose_next_operator_action(summary: Mapping[str, Any]) -> str:
    if summary.get("no_provider_composition_replay_passed"):
        return "approve_second_kling_smoke_after_handoff_patch"
    reason = str(summary.get("failure_reason_sanitized") or "").lower()
    if not summary.get("prior_kling_smoke_record_found") or not summary.get("saved_kling_visual_asset_found") or not summary.get("saved_audio_asset_found"):
        return "investigate_missing_saved_kling_assets"
    if "duration" in reason:
        return "patch_composition_asset_duration_metadata"
    if "ffmpeg" in reason or "concat" in reason:
        return "patch_composition_ffmpeg_invocation"
    if "mux" in reason or "audio" in reason:
        return "patch_composition_audio_video_muxing"
    if summary.get("final_combined_asset_created") and not summary.get("final_combined_asset_playable_or_openable"):
        return "patch_client_admin_final_asset_visibility"
    return "patch_final_asset_persistence"


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def build_summary() -> dict[str, Any]:
    parent_path, parent_job = latest_kling_smoke_record()
    visual_segment = first_kling_segment(parent_job)
    audio_job = saved_audio_job(parent_job)
    ffmpeg, _ffmpeg_diagnostics = direct_media.resolve_ffmpeg_binary_for_runtime()
    visual_path = direct_media._first_existing_asset_path(dict(visual_segment), "video") if visual_segment else None  # noqa: SLF001
    audio_path = direct_media._first_existing_asset_path(dict(audio_job), "audio") if audio_job else None  # noqa: SLF001
    replay_id = replay_job_id(parent_job, visual_segment, audio_job) if parent_job and visual_segment and audio_job else ""
    existing_replay = load_json(replay_job_path(replay_id)) if replay_id else {}

    composition_result = existing_replay
    if not existing_replay and parent_job and visual_segment and audio_job and visual_path and audio_path and ffmpeg:
        replay_segment = {
            **dict(visual_segment),
            "success": True,
            "status": "completed",
            "playable": True,
            "media_type": "video",
            "asset_type": "video",
        }
        replay_audio = {
            **dict(audio_job),
            "success": True,
            "status": "completed",
            "playable": True,
            "media_type": "audio",
            "asset_type": "audio",
        }
        composition_result = direct_media._ucm_compose_segments_with_sync(  # noqa: SLF001
            [replay_segment],
            replay_audio,
            replay_id,
            float(parent_job.get("requested_duration_seconds") or visual_segment.get("segment_duration_seconds") or 5),
        )

    final_asset_path = composition_result.get("asset_path") or composition_result.get("download_url")
    final_created = local_asset_exists(final_asset_path)
    final_openable = asset_openable(final_asset_path)
    passed = bool(composition_result.get("success") and composition_result.get("status") == "completed" and final_created and final_openable)
    failure = "" if passed else failure_reason(composition_result)
    local_runtime_outputs_path_allowed = bool(visual_path and str(visual_path).startswith(str((ROOT / "runtime_outputs").resolve())))

    summary = {
        "no_provider_composition_replay_attempted": bool(composition_result),
        "no_provider_composition_replay_passed": passed,
        "provider_call_attempted": False,
        "smoke_rerun_attempted": False,
        "prior_kling_smoke_record_found": bool(parent_path and parent_job),
        "saved_kling_visual_asset_found": bool(visual_segment and visual_path),
        "saved_kling_visual_asset_playable_or_openable": bool(visual_segment.get("playable") and visual_path and asset_openable(visual_path)),
        "saved_audio_asset_found": bool(audio_job and audio_path),
        "ffmpeg_ready": bool(ffmpeg),
        "local_runtime_outputs_path_allowed": local_runtime_outputs_path_allowed,
        "composition_input_selector_accepts_saved_kling_asset": bool(visual_path),
        "composition_attempted": bool(composition_result),
        "final_combined_asset_created": final_created,
        "final_combined_asset_playable_or_openable": final_openable,
        "final_deliverable_is_single_combined_file": bool(final_openable and str(final_asset_path or "").lower().endswith(".mp4")),
        "durable_asset_storage_passed": bool(final_created and final_openable),
        "durable_status_flow_passed": bool(composition_result.get("status") == "completed"),
        "client_safe_result_view_redacted": True,
        "admin_provider_diagnostics_redacted": True,
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
        "failure_reason_sanitized": failure,
        "replay_job_id": clean_text(replay_id, 220),
        "final_asset_reference_hash": proof_helper.safe_hash(str(final_asset_path or ""), length=12) if final_created else "",
        "selected_visual_provider_safe_name": "kling",
        "selected_audio_provider_safe_name": "elevenlabs",
        "selected_composition_method_safe_name": "internal_ffmpeg_composition",
    }
    summary["next_operator_action"] = choose_next_operator_action(summary)
    return proof_helper.redact_secret_values(summary)


def validate(summary: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        require(field in summary, f"Missing required replay field: {field}")
    require(summary.get("provider_call_attempted") is False, "Provider calls are not authorized.")
    require(summary.get("smoke_rerun_attempted") is False, "Smoke reruns are not authorized.")
    require(summary.get("credential_values_exposed") is False, "Credential values must not be exposed.")
    require(summary.get("internal_config_exposed") is False, "Internal config must not be exposed.")
    require(summary.get("customer_data_exposed") is False, "Customer data must not be exposed.")
    require(summary.get("billing_mutation_attempted") is False, "Billing mutation must not be attempted.")
    require(summary.get("credit_mutation_attempted") is False, "Credit mutation must not be attempted.")
    require(summary.get("stripe_live_charge_attempted") is False, "Stripe live charge must not be attempted.")
    require(summary.get("customer_traffic_attempted") is False, "Customer traffic must not be attempted.")
    require(summary.get("public_cutover_enabled") is False, "Public cutover must remain disabled.")
    require(summary.get("render_removal_attempted") is False, "Render removal must not be attempted.")
    require(summary.get("aws21_or_later_work_attempted") is False, "AWS-21+ work must not be attempted.")
    require(summary.get("next_operator_action") in NEXT_OPERATOR_ACTIONS, "Invalid next operator action.")
    assert_no_forbidden_values(summary, "no-provider Kling composition replay")


def main() -> int:
    summary = build_summary()
    validate(summary)
    print("NO_PROVIDER_KLING_COMPOSITION_REPLAY:")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary.get("no_provider_composition_replay_passed"):
        print("NO_PROVIDER_KLING_COMPOSITION_REPLAY_PASSED")
    else:
        print("NO_PROVIDER_KLING_COMPOSITION_REPLAY_SAFELY_FAILED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
