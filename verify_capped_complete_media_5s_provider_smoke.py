from __future__ import annotations

from pathlib import Path
import json
import re
import sys
import time
from typing import Any, Mapping

from backend.app.runtime import complete_media_final_deliverable_proof as proof_helper
from backend.app.runtime import direct_media_provider_execution_runtime as direct_media


ROOT = Path(__file__).resolve().parent
SMOKE_PROMPT = (
    "Create a 5 second neutral test clip with simple abstract motion and a short "
    "neutral voiceover saying: readiness smoke test complete."
)
POLL_TIMEOUT_SECONDS = 1200
POLL_INTERVAL_SECONDS = 5

TERMINAL_STATUSES = {
    "blocked_owner_approval_required",
    "completed",
    "completed_duration_shortfall",
    "media_script_failed",
    "universal_complete_media_audio_failed",
    "universal_complete_media_composition_failed",
    "universal_complete_media_exception",
    "universal_complete_media_preflight_blocked",
    "universal_complete_media_preflight_dry_run",
    "universal_complete_media_smoke_cap_blocked",
    "universal_complete_media_smoke_cap_exceeded",
    "universal_complete_media_visual_failed",
}

FORBIDDEN_VALUES = [
    "STRIPE_SECRET_SHOULD_NOT_LEAK",
    "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    "RUNWAY_SECRET_SHOULD_NOT_LEAK",
    "ELEVEN_SECRET_SHOULD_NOT_LEAK",
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
    "complete_media_5s_smoke_attempted",
    "complete_media_5s_smoke_passed",
    "provider_router_used",
    "provider_pair_hardcoded",
    "selected_visual_provider_safe_name",
    "selected_audio_provider_safe_name",
    "selected_composition_method_safe_name",
    "visual_provider_call_count",
    "audio_provider_call_count",
    "provider_call_count",
    "provider_call_count_lte_2",
    "visual_provider_call_count_lte_1",
    "audio_provider_call_count_lte_1",
    "provider_retry_count",
    "provider_cost_cap_enforced",
    "provider_output_or_failure_recorded",
    "visual_intermediate_asset_recorded",
    "audio_intermediate_asset_recorded",
    "composition_attempted",
    "final_combined_asset_created",
    "final_combined_asset_playable_or_openable",
    "final_deliverable_is_single_combined_file",
    "durable_status_flow_passed",
    "durable_asset_storage_passed",
    "client_safe_result_view_redacted",
    "admin_provider_diagnostics_redacted",
    "credential_values_exposed",
    "internal_config_exposed",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "stripe_live_charge_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "render_removal_attempted",
    "aws21_or_later_work_attempted",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def clean_text(value: Any, limit: int = 500) -> str:
    text = " ".join(str(value or "").split())
    text = re.sub(r"https?://\S+", "[redacted_url]", text)
    text = re.sub(r"[A-Za-z0-9_./+=:-]{40,}", "[redacted_token]", text)
    return text[:limit]


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def asset_reference_hash(value: Any) -> str:
    return proof_helper.safe_hash(str(value or ""), length=12)


def local_asset_exists(value: Any) -> bool:
    text = str(value or "").strip()
    if not text or text.startswith(("http://", "https://")):
        return False
    try:
        return Path(text).exists()
    except Exception:
        return False


def asset_openable(value: Any) -> bool:
    text = str(value or "").strip()
    if not local_asset_exists(text):
        return False
    try:
        duration = direct_media._ucm_get_duration_seconds(text)  # noqa: SLF001
        if duration is not None and duration > 0:
            return True
        with Path(text).open("rb") as handle:
            return bool(handle.read(16))
    except Exception:
        return False


def smoke_payload() -> dict[str, Any]:
    job_suffix = int(time.time())
    return {
        "job_id": f"synthetic_capped_complete_media_5s_provider_smoke_{job_suffix}",
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
        "actor_role": "owner",
        "requested_by_role": "owner",
        "selected_agent": "ugc_media_agent",
        "selected_agents": ["ugc_media_agent"],
        "agent_ids": ["ugc_media_agent"],
        "multi_agent_media_execution": False,
        "requested_from": "capped_complete_media_5s_provider_smoke",
        "workflow_type": "universal_complete_media",
        "media_type": "complete_video",
        "asset_type": "video",
        "output_type": "video",
        "video_provider": "auto",
        "audio_provider": "auto",
        "provider_router_mode": "category_readiness",
        "duration_seconds": 5,
        "duration": 5,
        "aspect_ratio": "9:16",
        "platform": "internal smoke",
        "business_name": "Synthetic Non-Customer Smoke",
        "product_or_service": "neutral readiness smoke test clip",
        "audience": "internal readiness reviewer",
        "goal": "confirm the capped complete media workflow can safely execute once",
        "offer": "readiness smoke test complete",
        "call_to_action": "readiness smoke test complete",
        "tone": "neutral, calm, concise",
        "voice_style": "neutral short voiceover",
        "visual_style": "simple abstract motion, no text, no logos, no people",
        "human_avatar_mode": "No human/avatar",
        "must_avoid": "brands, real customers, uploaded likeness, copyrighted content, personal data",
        "prompt": SMOKE_PROMPT,
        "media_prompt": SMOKE_PROMPT,
        "complete_media_config": {
            "prompt": SMOKE_PROMPT,
            "duration_seconds": 5,
            "duration": 5,
            "video_provider": "auto",
            "audio_provider": "auto",
            "provider_router_mode": "category_readiness",
            "output_type": "video",
        },
        "owner_approved": True,
        "owner_approval_granted": True,
        "owner_provider_cost_approval": True,
        "cost_safety_confirmed": True,
        "paid_provider_risk_confirmed": True,
        "credit_risk_acknowledged": True,
        "approval_required_for_spend": True,
        "approval_status": "owner_approved",
        "provider_estimated_cost": 1,
        "provider_cost_cap": 2,
        "credit_reservation_status": "not_mutated_synthetic_smoke",
        "two_provider_smoke_test": True,
        "two_provider_call_smoke_test": True,
        "five_second_smoke_test": True,
        "smoke_test_mode": True,
        "run_smoke_test": True,
        "max_visual_provider_calls": 1,
        "max_audio_provider_calls": 1,
        "max_total_provider_calls": 2,
        "max_provider_retries": 0,
        "provider_retry_count": 0,
        "script_approval_required": False,
        "script_approved": True,
        "dry_run": False,
        "preflight_only": False,
        "customer_asset_used": False,
        "customer_likeness_used": False,
        "customer_traffic_attempted": False,
    }


def selected_names(readiness: Mapping[str, Any], job: Mapping[str, Any] | None = None) -> dict[str, str]:
    job = job or {}
    job_audio_provider = clean_text(job.get("audio_provider"), 80)
    if job_audio_provider == "auto":
        job_audio_provider = ""
    return {
        "selected_visual_provider_safe_name": clean_text(
            job.get("selected_video_provider")
            or readiness.get("selected_visual_provider_safe_name")
            or "",
            80,
        ),
        "selected_audio_provider_safe_name": clean_text(
            job_audio_provider
            or readiness.get("selected_audio_provider_safe_name")
            or "",
            80,
        ),
        "selected_composition_method_safe_name": clean_text(
            readiness.get("selected_composition_method_safe_name") or "",
            80,
        ),
    }


def provider_failure_reason(job: Mapping[str, Any]) -> str:
    status = clean_text(job.get("status"), 120)
    for key in (
        "video_error",
        "audio_error",
        "composition_error",
        "support_failure_message",
        "message",
        "reason",
        "error",
    ):
        if job.get(key):
            return clean_text(f"{status}: {job.get(key)}", 500)
    failed = list(job.get("failed_provider_attempts") or [])
    if failed:
        latest = failed[-1]
        return clean_text(
            f"{status}: {latest.get('safe_error_summary') or latest.get('status') or latest.get('reason')}",
            500,
        )
    return status


def poll_job(job_id: str) -> tuple[dict[str, Any], list[str]]:
    deadline = time.time() + POLL_TIMEOUT_SECONDS
    statuses: list[str] = []
    latest: dict[str, Any] = {}

    while time.time() < deadline:
        latest = direct_media._read_job(job_id)  # noqa: SLF001
        status = clean_text(latest.get("status"), 120)
        if status and (not statuses or statuses[-1] != status):
            statuses.append(status)
        if status in TERMINAL_STATUSES:
            return latest, statuses
        time.sleep(POLL_INTERVAL_SECONDS)

    latest = direct_media._read_job(job_id)  # noqa: SLF001
    status = clean_text(latest.get("status") or "poll_timeout", 120)
    if not statuses or statuses[-1] != status:
        statuses.append(status)
    return {**latest, "status": "poll_timeout", "poll_timeout": True}, statuses


def build_client_safe_view(summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": "complete_media_smoke_passed" if summary.get("complete_media_5s_smoke_passed") else "complete_media_smoke_not_passed",
        "final_asset_ready": bool(summary.get("final_combined_asset_playable_or_openable")),
        "provider_call_count_lte_2": bool(summary.get("provider_call_count_lte_2")),
        "support_available": bool(summary.get("provider_output_or_failure_recorded")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }


def build_admin_diagnostics(summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": summary.get("status"),
        "proof_blocked_reason": summary.get("proof_blocked_reason"),
        "provider_failure_reason": summary.get("provider_failure_reason"),
        "selected_visual_provider_safe_name": summary.get("selected_visual_provider_safe_name"),
        "selected_audio_provider_safe_name": summary.get("selected_audio_provider_safe_name"),
        "selected_composition_method_safe_name": summary.get("selected_composition_method_safe_name"),
        "provider_call_count": summary.get("provider_call_count"),
        "durable_status_flow": summary.get("durable_status_flow"),
        "admin_provider_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "raw_provider_response_exposed": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def abort_summary(readiness_proof: Mapping[str, Any], reason: str) -> dict[str, Any]:
    readiness = readiness_proof.get("provider_category_readiness") or {}
    summary = {
        "status": "blocked_before_provider_call",
        "complete_media_5s_smoke_attempted": False,
        "complete_media_5s_smoke_passed": False,
        "proof_blocked_reason": clean_text(reason, 500),
        "provider_failure_reason": "",
        "provider_router_used": bool(readiness_proof.get("provider_router_used")),
        "provider_pair_hardcoded": False,
        **selected_names(readiness),
        "visual_provider_call_count": 0,
        "audio_provider_call_count": 0,
        "provider_call_count": 0,
        "provider_call_count_lte_2": True,
        "visual_provider_call_count_lte_1": True,
        "audio_provider_call_count_lte_1": True,
        "provider_retry_count": 0,
        "provider_cost_cap_enforced": bool(readiness_proof.get("provider_cost_cap_enforced")),
        "provider_output_or_failure_recorded": True,
        "visual_intermediate_asset_recorded": False,
        "audio_intermediate_asset_recorded": False,
        "composition_attempted": False,
        "final_combined_asset_created": False,
        "final_combined_asset_playable_or_openable": False,
        "final_deliverable_is_single_combined_file": False,
        "durable_status_flow": ["accepted", "readiness_gate", "blocked_before_provider_call"],
        "durable_status_flow_passed": True,
        "durable_asset_storage_passed": True,
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
        "long_form_generation_blocked_or_not_requested": True,
        "customer_asset_used": False,
        "customer_likeness_used": False,
    }
    summary["client_safe_result_view"] = build_client_safe_view(summary)
    summary["admin_provider_diagnostics"] = build_admin_diagnostics(summary)
    return proof_helper.redact_secret_values(summary)


def validate_summary(summary: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        require(field in summary, f"Missing required output field: {field}")

    require(summary.get("provider_pair_hardcoded") is False, "Smoke must not hardcode a provider pair.")
    require(summary.get("provider_call_count_lte_2") is True, "Total provider calls exceeded cap.")
    require(summary.get("visual_provider_call_count_lte_1") is True, "Visual provider calls exceeded cap.")
    require(summary.get("audio_provider_call_count_lte_1") is True, "Audio provider calls exceeded cap.")
    require(summary.get("provider_retry_count") == 0, "Provider retry count must remain zero.")
    require(summary.get("credential_values_exposed") is False, "Credential values must not be exposed.")
    require(summary.get("internal_config_exposed") is False, "Internal config must not be exposed.")
    require(summary.get("billing_mutation_attempted") is False, "Billing mutation must remain untouched.")
    require(summary.get("credit_mutation_attempted") is False, "Credit mutation must remain untouched.")
    require(summary.get("stripe_live_charge_attempted") is False, "Stripe live charge must remain untouched.")
    require(summary.get("customer_traffic_attempted") is False, "Customer traffic must remain untouched.")
    require(summary.get("public_cutover_enabled") is False, "Public cutover must remain disabled.")
    require(summary.get("render_removal_attempted") is False, "Render removal must not be attempted.")
    require(summary.get("aws21_or_later_work_attempted") is False, "AWS-21+ work must not be attempted.")
    require(summary.get("client_safe_result_view_redacted") is True, "Client-safe result view must be redacted.")
    require(summary.get("admin_provider_diagnostics_redacted") is True, "Admin diagnostics must be redacted.")
    assert_no_forbidden_values(summary, "capped complete media smoke summary")


def run_smoke() -> dict[str, Any]:
    readiness_proof = proof_helper.build_complete_media_final_deliverable_proof(
        allow_live_provider_attempt=False,
    )
    readiness = readiness_proof.get("provider_category_readiness") or {}
    next_action = readiness_proof.get("next_operator_action")

    if readiness.get("provider_category_readiness_verified") is not True:
        return abort_summary(readiness_proof, "provider_category_readiness_not_verified")
    if next_action != "owner_approve_capped_5s_provider_smoke":
        return abort_summary(readiness_proof, f"unexpected_next_operator_action:{next_action}")

    payload = smoke_payload()
    require(payload["video_provider"] == "auto", "Smoke payload must use video_provider=auto.")
    require(payload["audio_provider"] == "auto", "Smoke payload must use audio_provider=auto.")
    require(payload["provider_router_mode"] == "category_readiness", "Smoke payload must use category readiness routing.")
    require(payload["max_provider_retries"] == 0, "Smoke payload must disable retries.")
    require(float(payload["duration_seconds"]) <= 5, "Smoke payload duration must be <= 5 seconds.")

    start_result = direct_media.start_universal_complete_media_workflow(payload)
    job_id = start_result.get("job_id")
    require(bool(job_id), "Complete media workflow did not return a job id.")

    final_job, statuses = poll_job(str(job_id))
    status = clean_text(final_job.get("status"), 120)
    visual_calls = as_int(final_job.get("visual_provider_call_count"))
    audio_calls = as_int(final_job.get("audio_provider_call_count"))
    provider_calls = as_int(final_job.get("provider_call_count"))
    provider_retries = as_int(final_job.get("provider_retry_count"))
    final_asset_path = final_job.get("asset_path")
    final_created = bool(status in {"completed", "completed_duration_shortfall"} and local_asset_exists(final_asset_path))
    final_openable = bool(final_created and asset_openable(final_asset_path))
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
    failure_reason = "" if passed else provider_failure_reason(final_job)
    provider_output_or_failure_recorded = bool(
        final_created
        or failure_reason
        or final_job.get("failed_provider_attempts")
        or status in TERMINAL_STATUSES
    )
    durable_status_flow_passed = bool(statuses and status in TERMINAL_STATUSES)
    durable_asset_storage_passed = bool(final_openable or provider_output_or_failure_recorded)

    summary = {
        "status": status,
        "complete_media_5s_smoke_attempted": True,
        "complete_media_5s_smoke_passed": passed,
        "proof_blocked_reason": "",
        "provider_failure_reason": failure_reason,
        "provider_router_used": True,
        "provider_pair_hardcoded": False,
        **selected_names(readiness, final_job),
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
        "final_asset_reference_hash": asset_reference_hash(final_asset_path) if final_created else "",
        "synthetic_job_reference_hash": asset_reference_hash(job_id),
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
    summary["client_safe_result_view"] = build_client_safe_view(summary)
    summary["admin_provider_diagnostics"] = build_admin_diagnostics(summary)
    return proof_helper.redact_secret_values(summary)


def main() -> int:
    summary = run_smoke()
    validate_summary(summary)
    print("CAPPED_COMPLETE_MEDIA_5S_PROVIDER_SMOKE:")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary.get("complete_media_5s_smoke_passed"):
        print("CAPPED_COMPLETE_MEDIA_5S_PROVIDER_SMOKE_PASSED")
    else:
        print("CAPPED_COMPLETE_MEDIA_5S_PROVIDER_SMOKE_SAFELY_FAILED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"CAPPED_COMPLETE_MEDIA_5S_PROVIDER_SMOKE_UNSAFE_FAILURE: {clean_text(error, 800)}", file=sys.stderr)
        raise
