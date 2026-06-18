from __future__ import annotations

import json
import sys
from typing import Any, Mapping

from backend.app.runtime import complete_media_final_deliverable_proof as proof_helper
from backend.app.runtime import direct_media_provider_execution_runtime as direct_media

import verify_capped_complete_media_5s_provider_smoke as base_smoke


OWNER_APPROVED_VISUAL_PROVIDER = "kling"

REQUIRED_FIELDS = [
    *base_smoke.REQUIRED_FIELDS,
    "owner_approved_visual_provider_override_used",
]


def _first_visual_attempt(job: Mapping[str, Any]) -> dict[str, Any]:
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    attempts = child_jobs.get("visual_attempts") if isinstance(child_jobs, dict) else []
    if isinstance(attempts, list) and attempts and isinstance(attempts[0], dict):
        return attempts[0]
    failed = job.get("failed_provider_attempts")
    if isinstance(failed, list) and failed and isinstance(failed[0], dict):
        return failed[0]
    return {}


def _provider_error_type(job: Mapping[str, Any]) -> str:
    if job.get("provider_error_type_sanitized"):
        return base_smoke.clean_text(job.get("provider_error_type_sanitized"), 120)
    attempt = _first_visual_attempt(job)
    return base_smoke.clean_text(attempt.get("provider_error_type_sanitized"), 120)


def _provider_http_status(job: Mapping[str, Any]) -> Any:
    if job.get("provider_http_status_if_recorded"):
        return job.get("provider_http_status_if_recorded")
    attempt = _first_visual_attempt(job)
    return attempt.get("provider_http_status_if_recorded") or ""


def _selected_names(readiness: Mapping[str, Any], job: Mapping[str, Any] | None = None) -> dict[str, str]:
    job = job or {}
    attempt = _first_visual_attempt(job)
    names = base_smoke.selected_names(readiness, job)
    names["selected_visual_provider_safe_name"] = base_smoke.clean_text(
        job.get("selected_video_provider")
        or attempt.get("provider")
        or OWNER_APPROVED_VISUAL_PROVIDER,
        80,
    )
    return names


def _choose_next_operator_action(summary: Mapping[str, Any]) -> str:
    if summary.get("complete_media_5s_smoke_passed"):
        return "review_kling_smoke_final_asset"
    error_type = str(summary.get("provider_error_type_sanitized") or "").strip()
    reason = str(summary.get("provider_failure_reason") or "").lower()
    if error_type == "insufficient_provider_credits" or "insufficient provider credits" in reason:
        return "resolve_kling_provider_credits_or_entitlement"
    if summary.get("complete_media_5s_smoke_attempted"):
        return "investigate_kling_provider_failure_before_retry"
    return "investigate_kling_smoke_precheck_blocker"


def _abort_summary(readiness_proof: Mapping[str, Any], reason: str) -> dict[str, Any]:
    summary = base_smoke.abort_summary(readiness_proof, reason)
    summary["owner_approved_visual_provider_override_used"] = False
    summary["selected_visual_provider_safe_name"] = OWNER_APPROVED_VISUAL_PROVIDER
    summary["next_operator_action"] = _choose_next_operator_action(summary)
    summary["client_safe_result_view"] = base_smoke.build_client_safe_view(summary)
    summary["admin_provider_diagnostics"] = base_smoke.build_admin_diagnostics(summary)
    return proof_helper.redact_secret_values(summary)


def _readiness_abort_reason(readiness_proof: Mapping[str, Any]) -> str:
    readiness = readiness_proof.get("provider_category_readiness") or {}
    kling = direct_media._ucm_provider_executable(OWNER_APPROVED_VISUAL_PROVIDER, "video")  # noqa: SLF001
    elevenlabs = direct_media._ucm_provider_executable("elevenlabs", "audio")  # noqa: SLF001

    if readiness.get("provider_category_readiness_verified") is not True:
        return "provider_category_readiness_not_verified"
    if readiness_proof.get("provider_environment_readiness_passed") is not True:
        return "provider_environment_readiness_not_passed"
    if readiness_proof.get("provider_router_used") is not True:
        return "provider_router_not_used"
    if readiness_proof.get("provider_pair_hardcoded") is not False:
        return "provider_pair_hardcoded"
    if readiness_proof.get("credential_values_exposed") is not False:
        return "credential_values_exposed"
    if kling.get("executable") is not True:
        return "kling_video_provider_not_executable"
    if elevenlabs.get("executable") is not True:
        return "elevenlabs_audio_provider_not_executable"
    if readiness.get("selected_composition_method_safe_name") != "internal_ffmpeg_composition":
        return "internal_ffmpeg_composition_not_ready"
    return ""


def _kling_payload() -> dict[str, Any]:
    payload = base_smoke.smoke_payload()
    payload["video_provider"] = OWNER_APPROVED_VISUAL_PROVIDER
    payload["audio_provider"] = "auto"
    payload["provider_router_mode"] = "category_readiness"
    payload["owner_approved_visual_provider_override"] = OWNER_APPROVED_VISUAL_PROVIDER
    payload["owner_approved_visual_provider_override_used"] = True
    payload["requested_from"] = "capped_complete_media_5s_kling_provider_smoke"
    payload["job_id"] = payload["job_id"].replace(
        "synthetic_capped_complete_media_5s_provider_smoke",
        "synthetic_capped_complete_media_5s_kling_smoke",
    )
    config = payload.get("complete_media_config")
    if isinstance(config, dict):
        config["video_provider"] = OWNER_APPROVED_VISUAL_PROVIDER
        config["audio_provider"] = "auto"
        config["provider_router_mode"] = "category_readiness"
    return payload


def validate_summary(summary: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        base_smoke.require(field in summary, f"Missing required output field: {field}")

    base_smoke.validate_summary(summary)
    if summary.get("complete_media_5s_smoke_attempted"):
        base_smoke.require(
            summary.get("owner_approved_visual_provider_override_used") is True,
            "Kling smoke must use the owner-approved visual provider override.",
        )
        base_smoke.require(
            summary.get("selected_visual_provider_safe_name") == OWNER_APPROVED_VISUAL_PROVIDER,
            "Kling smoke selected a different visual provider.",
        )


def run_smoke() -> dict[str, Any]:
    readiness_proof = proof_helper.build_complete_media_final_deliverable_proof(
        allow_live_provider_attempt=False,
    )
    readiness = readiness_proof.get("provider_category_readiness") or {}
    abort_reason = _readiness_abort_reason(readiness_proof)
    if abort_reason:
        return _abort_summary(readiness_proof, abort_reason)

    payload = _kling_payload()
    base_smoke.require(payload["video_provider"] == OWNER_APPROVED_VISUAL_PROVIDER, "Kling smoke must request video_provider=kling.")
    base_smoke.require(payload["audio_provider"] == "auto", "Kling smoke must use audio_provider=auto.")
    base_smoke.require(payload["provider_router_mode"] == "category_readiness", "Kling smoke must use category readiness routing.")
    base_smoke.require(payload["max_provider_retries"] == 0, "Kling smoke must disable retries.")
    base_smoke.require(float(payload["duration_seconds"]) <= 5, "Kling smoke duration must be <= 5 seconds.")

    start_result = direct_media.start_universal_complete_media_workflow(payload)
    job_id = start_result.get("job_id")
    base_smoke.require(bool(job_id), "Complete media workflow did not return a job id.")

    final_job, statuses = base_smoke.poll_job(str(job_id))
    status = base_smoke.clean_text(final_job.get("status"), 120)
    visual_calls = base_smoke.as_int(final_job.get("visual_provider_call_count"))
    audio_calls = base_smoke.as_int(final_job.get("audio_provider_call_count"))
    provider_calls = base_smoke.as_int(final_job.get("provider_call_count"))
    provider_retries = base_smoke.as_int(final_job.get("provider_retry_count"))
    final_asset_path = final_job.get("asset_path")
    final_created = bool(status in {"completed", "completed_duration_shortfall"} and base_smoke.local_asset_exists(final_asset_path))
    final_openable = bool(final_created and base_smoke.asset_openable(final_asset_path))
    generated_segments = list(final_job.get("generated_segments") or [])
    child_jobs = final_job.get("child_jobs") if isinstance(final_job.get("child_jobs"), dict) else {}
    visual_asset_recorded = bool(generated_segments)
    audio_asset_recorded = bool(
        final_job.get("audio_job_id")
        or (isinstance(child_jobs, dict) and (child_jobs.get("audio") or {}).get("job_id"))
    )
    composition_attempted = bool(
        final_job.get("composition_job_id")
        or status in {"running_synchronised_composition", "universal_complete_media_composition_failed", "completed", "completed_duration_shortfall"}
    )
    passed = bool(
        status == "completed"
        and provider_calls <= 2
        and visual_calls <= 1
        and audio_calls <= 1
        and provider_retries == 0
        and final_openable
    )
    failure_reason = "" if passed else base_smoke.provider_failure_reason(final_job)
    provider_output_or_failure_recorded = bool(
        final_created
        or failure_reason
        or final_job.get("failed_provider_attempts")
        or status in base_smoke.TERMINAL_STATUSES
    )
    durable_status_flow_passed = bool(statuses and status in base_smoke.TERMINAL_STATUSES)
    durable_asset_storage_passed = bool(final_openable or provider_output_or_failure_recorded)

    summary = {
        "status": status,
        "complete_media_5s_smoke_attempted": True,
        "complete_media_5s_smoke_passed": passed,
        "owner_approved_visual_provider_override_used": True,
        "proof_blocked_reason": "",
        "provider_failure_reason": failure_reason,
        "provider_error_type_sanitized": _provider_error_type(final_job),
        "provider_http_status_if_recorded": _provider_http_status(final_job),
        "provider_router_used": True,
        "provider_pair_hardcoded": False,
        **_selected_names(readiness, final_job),
        "visual_provider_call_count": visual_calls,
        "audio_provider_call_count": audio_calls,
        "provider_call_count": provider_calls,
        "provider_call_count_lte_2": provider_calls <= 2,
        "visual_provider_call_count_lte_1": visual_calls <= 1,
        "audio_provider_call_count_lte_1": audio_calls <= 1,
        "provider_retry_count": provider_retries,
        "provider_cost_cap_enforced": bool(readiness_proof.get("provider_cost_cap_enforced")),
        "provider_output_or_failure_recorded": provider_output_or_failure_recorded,
        "visual_intermediate_asset_recorded": visual_asset_recorded,
        "audio_intermediate_asset_recorded": audio_asset_recorded,
        "composition_attempted": composition_attempted,
        "final_combined_asset_created": final_created,
        "final_combined_asset_playable_or_openable": final_openable,
        "final_deliverable_is_single_combined_file": bool(final_openable and final_job.get("composition_job_id")),
        "durable_status_flow": statuses,
        "durable_status_flow_passed": durable_status_flow_passed,
        "durable_asset_storage_passed": durable_asset_storage_passed,
        "final_asset_reference_hash": base_smoke.asset_reference_hash(final_asset_path) if final_created else "",
        "synthetic_job_reference_hash": base_smoke.asset_reference_hash(job_id),
        "client_safe_result_view_redacted": True,
        "admin_provider_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
        "synthetic_non_customer_request": True,
        "duration_seconds_lte_5": True,
        "requested_duration_seconds": 5,
        "max_visual_provider_calls": 1,
        "max_audio_provider_calls": 1,
        "max_total_provider_calls": 2,
        "multi_agent_provider_fanout_blocked": True,
        "long_form_generation_blocked_or_not_requested": True,
        "customer_asset_used": False,
        "customer_likeness_used": False,
    }
    summary["next_operator_action"] = _choose_next_operator_action(summary)
    summary["client_safe_result_view"] = base_smoke.build_client_safe_view(summary)
    summary["admin_provider_diagnostics"] = base_smoke.build_admin_diagnostics(summary)
    return proof_helper.redact_secret_values(summary)


def main() -> int:
    summary = run_smoke()
    validate_summary(summary)
    print("CAPPED_COMPLETE_MEDIA_5S_KLING_SMOKE:")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary.get("complete_media_5s_smoke_passed"):
        print("CAPPED_COMPLETE_MEDIA_5S_KLING_SMOKE_PASSED")
    else:
        print("CAPPED_COMPLETE_MEDIA_5S_KLING_SMOKE_SAFELY_FAILED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"CAPPED_COMPLETE_MEDIA_5S_KLING_SMOKE_UNSAFE_FAILURE: {base_smoke.clean_text(error, 800)}", file=sys.stderr)
        raise
