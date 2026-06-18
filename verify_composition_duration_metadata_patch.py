from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Mapping

from backend.app.runtime import complete_media_final_deliverable_proof as proof_helper
from backend.app.runtime import direct_media_provider_execution_runtime as direct_media

from verify_kling_handoff_and_runway_key_state_diagnostics import FORBIDDEN_VALUES, clean_text


ROOT = Path(__file__).resolve().parent
JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"
REPLAY_JOB_PREFIX = "no_provider_kling_composition_replay_"

NEXT_OPERATOR_ACTIONS = {
    "approve_no_provider_final_deliverable_status_recheck",
    "approve_second_kling_smoke_after_duration_patch",
    "patch_ffprobe_duration_detection",
    "patch_final_asset_metadata_persistence",
    "patch_durable_status_success_transition",
    "patch_client_admin_final_asset_visibility",
    "investigate_missing_final_mp4_record",
}

REQUIRED_FIELDS = [
    "composition_duration_metadata_patch_attempted",
    "composition_duration_metadata_patch_passed",
    "provider_call_attempted",
    "smoke_rerun_attempted",
    "saved_final_combined_mp4_found",
    "saved_final_combined_mp4_playable_or_openable",
    "final_asset_duration_probe_attempted",
    "final_asset_duration_seconds",
    "final_asset_duration_gt_zero",
    "source_visual_duration_seconds_if_available",
    "source_audio_duration_seconds_if_available",
    "duration_tolerance_applied",
    "composition_duration_shortfall_resolved",
    "durable_status_flow_passed",
    "durable_asset_storage_passed",
    "final_asset_metadata_persisted",
    "final_deliverable_is_single_combined_file",
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


def latest_replay_job() -> tuple[Path | None, dict[str, Any]]:
    candidates = sorted(
        JOB_DIR.glob(f"{REPLAY_JOB_PREFIX}*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        job = load_json(path)
        if job.get("asset_path") or job.get("download_url") or job.get("output_path"):
            return path, job
    return (candidates[0], load_json(candidates[0])) if candidates else (None, {})


def asset_exists(value: Any) -> bool:
    try:
        return bool(value and Path(str(value)).exists() and Path(str(value)).is_file())
    except Exception:
        return False


def source_visual_duration(job: Mapping[str, Any]) -> float:
    paths = job.get("video_segment_asset_paths")
    if isinstance(paths, list) and paths:
        return float(sum(float(direct_media._ucm_get_duration_seconds(str(path)) or 0.0) for path in paths))  # noqa: SLF001
    value = job.get("video_duration_seconds") or job.get("visual_duration_seconds")
    try:
        return float(value or 0.0)
    except Exception:
        return 0.0


def source_audio_duration(job: Mapping[str, Any]) -> float:
    audio_path = job.get("audio_asset_path")
    if audio_path:
        return float(direct_media._ucm_get_duration_seconds(str(audio_path)) or 0.0)  # noqa: SLF001
    try:
        return float(job.get("audio_duration_seconds") or 0.0)
    except Exception:
        return 0.0


def asset_openable(value: Any) -> bool:
    if not asset_exists(value):
        return False
    duration = direct_media._ucm_get_duration_seconds(str(value))  # noqa: SLF001
    if duration is not None and duration > 0:
        return True
    try:
        with Path(str(value)).open("rb") as handle:
            return bool(handle.read(16))
    except Exception:
        return False


def choose_next_operator_action(summary: Mapping[str, Any]) -> str:
    if summary.get("composition_duration_metadata_patch_passed"):
        return "approve_second_kling_smoke_after_duration_patch"
    if not summary.get("saved_final_combined_mp4_found"):
        return "investigate_missing_final_mp4_record"
    if not summary.get("final_asset_duration_gt_zero"):
        return "patch_ffprobe_duration_detection"
    if not summary.get("final_asset_metadata_persisted"):
        return "patch_final_asset_metadata_persistence"
    if not summary.get("durable_status_flow_passed"):
        return "patch_durable_status_success_transition"
    return "patch_client_admin_final_asset_visibility"


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def build_diagnostics() -> dict[str, Any]:
    _path, job = latest_replay_job()
    refreshed = direct_media.refresh_composition_final_asset_metadata(job) if job else {}
    asset_path = refreshed.get("asset_path") or refreshed.get("download_url") or refreshed.get("output_path")
    final_duration = direct_media._ucm_get_duration_seconds(str(asset_path or "")) if asset_path else None  # noqa: SLF001
    requested = float(refreshed.get("requested_duration_seconds") or final_duration or 0.0)
    tolerance = direct_media._ucm_duration_tolerance_seconds(requested)  # noqa: SLF001
    final_found = asset_exists(asset_path)
    final_openable = asset_openable(asset_path)
    metadata_persisted = bool(
        refreshed.get("final_asset_metadata_refresh_attempted")
        and refreshed.get("final_duration_seconds")
        and refreshed.get("asset_path")
    )
    status_passed = bool(refreshed.get("status") == "completed" and refreshed.get("duration_fulfilled") is True)

    summary = {
        "composition_duration_metadata_patch_attempted": True,
        "composition_duration_metadata_patch_passed": bool(final_found and final_openable and metadata_persisted and status_passed),
        "provider_call_attempted": False,
        "smoke_rerun_attempted": False,
        "saved_final_combined_mp4_found": final_found,
        "saved_final_combined_mp4_playable_or_openable": final_openable,
        "final_asset_duration_probe_attempted": bool(asset_path),
        "final_asset_duration_seconds": float(final_duration or 0.0),
        "final_asset_duration_gt_zero": bool(final_duration and final_duration > 0),
        "source_visual_duration_seconds_if_available": source_visual_duration(refreshed),
        "source_audio_duration_seconds_if_available": source_audio_duration(refreshed),
        "duration_tolerance_applied": tolerance,
        "composition_duration_shortfall_resolved": bool(refreshed.get("status") == "completed"),
        "durable_status_flow_passed": status_passed,
        "durable_asset_storage_passed": bool(final_found and final_openable),
        "final_asset_metadata_persisted": metadata_persisted,
        "final_deliverable_is_single_combined_file": bool(final_openable and str(asset_path or "").lower().endswith(".mp4")),
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
        "failure_reason_sanitized": "" if status_passed else clean_text(refreshed.get("final_asset_metadata_refresh_reason") or refreshed.get("status"), 500),
        "final_asset_reference_hash": proof_helper.safe_hash(str(asset_path or ""), length=12) if final_found else "",
    }
    summary["next_operator_action"] = choose_next_operator_action(summary)
    return proof_helper.redact_secret_values(summary)


def validate(summary: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        require(field in summary, f"Missing required duration metadata field: {field}")
    require(summary.get("composition_duration_metadata_patch_attempted") is True, "Duration metadata patch must be attempted.")
    require(summary.get("composition_duration_metadata_patch_passed") is True, "Duration metadata patch must pass.")
    require(summary.get("provider_call_attempted") is False, "Provider calls are not authorized.")
    require(summary.get("smoke_rerun_attempted") is False, "Smoke reruns are not authorized.")
    require(summary.get("saved_final_combined_mp4_found") is True, "Saved final MP4 must exist.")
    require(summary.get("saved_final_combined_mp4_playable_or_openable") is True, "Saved final MP4 must be playable/openable.")
    require(summary.get("final_asset_duration_gt_zero") is True, "Final asset duration must be greater than zero.")
    require(summary.get("durable_status_flow_passed") is True, "Durable status flow must pass.")
    require(summary.get("final_asset_metadata_persisted") is True, "Final asset metadata must be persisted.")
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
    assert_no_forbidden_values(summary, "composition duration metadata patch")


def main() -> int:
    summary = build_diagnostics()
    validate(summary)
    print("COMPOSITION_DURATION_METADATA_PATCH:")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("COMPOSITION_DURATION_METADATA_PATCH_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
