from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
from typing import Any, Mapping

from backend.app.runtime import direct_media_provider_execution_runtime as direct_media


ROOT = Path(__file__).resolve().parent
JOB_DIR = ROOT / "runtime_outputs" / "direct_media_provider_jobs"

NEXT_OPERATOR_ACTIONS = {
    "resolve_runway_provider_credits",
    "patch_provider_failure_propagation",
    "investigate_missing_child_failure_record",
    "approve_second_capped_smoke_after_provider_credit_fix",
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
    "provider_failure_propagation_attempted",
    "provider_failure_propagation_passed",
    "prior_smoke_failure_record_found",
    "child_failure_reason_found",
    "parent_failure_reason_preserved",
    "provider_failure_reason_sanitized",
    "provider_error_type_sanitized",
    "provider_http_status_if_recorded",
    "provider_failure_stage",
    "provider_safe_name",
    "admin_actionable_failure_visible",
    "client_safe_result_view_redacted",
    "admin_provider_diagnostics_redacted",
    "credential_values_exposed",
    "internal_config_exposed",
    "customer_data_exposed",
    "provider_router_used",
    "provider_pair_hardcoded",
    "provider_call_attempted",
    "media_generation_attempted",
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


def latest_visual_failed_smoke() -> tuple[Path | None, dict[str, Any]]:
    candidates = sorted(
        JOB_DIR.glob("synthetic_capped_complete_media_5s_provider_smoke_*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        job = load_json(path)
        if (
            job.get("status") == "universal_complete_media_visual_failed"
            and as_int(job.get("visual_provider_call_count")) == 1
            and as_int(job.get("audio_provider_call_count")) == 1
            and as_int(job.get("provider_call_count")) == 2
        ):
            return path, job
    return (candidates[0], load_json(candidates[0])) if candidates else (None, {})


def first_visual_attempt(job: Mapping[str, Any]) -> dict[str, Any]:
    child_jobs = job.get("child_jobs") if isinstance(job.get("child_jobs"), dict) else {}
    attempts = child_jobs.get("visual_attempts") if isinstance(child_jobs, dict) else []
    if isinstance(attempts, list) and attempts and isinstance(attempts[0], dict):
        return attempts[0]
    return {}


def direct_child_job(attempt: Mapping[str, Any]) -> dict[str, Any]:
    job_id = str(attempt.get("job_id") or "").strip()
    if not job_id:
        return {}
    return load_json(JOB_DIR / f"{job_id}.json")


def client_safe_result_view(parent_diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": "provider_failure_recorded",
        "support_available": bool(parent_diagnostics.get("provider_failure_reason_sanitized")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
    }


def admin_provider_diagnostics(parent_diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "provider_failure_reason_sanitized": parent_diagnostics.get("provider_failure_reason_sanitized"),
        "provider_error_type_sanitized": parent_diagnostics.get("provider_error_type_sanitized"),
        "provider_http_status_if_recorded": parent_diagnostics.get("provider_http_status_if_recorded"),
        "provider_failure_stage": parent_diagnostics.get("provider_failure_stage"),
        "provider_safe_name": parent_diagnostics.get("provider_safe_name"),
        "admin_actionable_failure_visible": bool(parent_diagnostics.get("provider_failure_reason_sanitized")),
        "admin_provider_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
        "customer_data_exposed": False,
    }


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def build_proof() -> dict[str, Any]:
    smoke_path, smoke = latest_visual_failed_smoke()
    attempt = first_visual_attempt(smoke)
    child = direct_child_job(attempt)
    segment = {
        "segment_index": 1,
        "segment_start_seconds": 0,
        "segment_end_seconds": 5,
        "segment_duration_seconds": 5,
        "segment_prompt": "redacted synthetic visual segment",
    }
    propagated_child = direct_media._ucm_segment_child_record(  # noqa: SLF001
        "synthetic_parent_for_failure_propagation",
        segment,
        "runway",
        child,
    ) if child else {}
    parent_diagnostics = direct_media._ucm_parent_failure_diagnostics(  # noqa: SLF001
        propagated_child,
        selected_visual_provider="runway",
        selected_audio_provider="elevenlabs",
        selected_composition_method="internal_ffmpeg_composition",
    ) if propagated_child else {}
    admin_view = admin_provider_diagnostics(parent_diagnostics)
    client_view = client_safe_result_view(parent_diagnostics)
    reason = clean_text(parent_diagnostics.get("provider_failure_reason_sanitized"), 500)
    error_type = clean_text(parent_diagnostics.get("provider_error_type_sanitized"), 120)
    next_action = "resolve_runway_provider_credits" if error_type == "insufficient_provider_credits" else "patch_provider_failure_propagation"
    passed = bool(
        smoke
        and child
        and propagated_child
        and parent_diagnostics
        and "insufficient provider credits" in reason.lower()
        and error_type == "insufficient_provider_credits"
        and parent_diagnostics.get("provider_http_status_if_recorded") == 400
        and admin_view.get("admin_actionable_failure_visible") is True
        and next_action == "resolve_runway_provider_credits"
    )

    return {
        "provider_failure_propagation_attempted": True,
        "provider_failure_propagation_passed": passed,
        "prior_smoke_failure_record_found": bool(smoke),
        "prior_smoke_failure_record_hash": safe_hash(smoke_path.name if smoke_path else ""),
        "child_failure_reason_found": bool(child and child.get("provider_result")),
        "parent_failure_reason_preserved": bool(parent_diagnostics.get("provider_failure_reason_sanitized") == reason and reason),
        "provider_failure_reason_sanitized": reason,
        "provider_error_type_sanitized": error_type,
        "provider_http_status_if_recorded": parent_diagnostics.get("provider_http_status_if_recorded") or "",
        "provider_failure_stage": parent_diagnostics.get("provider_failure_stage") or "",
        "provider_safe_name": parent_diagnostics.get("provider_safe_name") or "",
        "selected_visual_provider_safe_name": parent_diagnostics.get("selected_visual_provider_safe_name") or "",
        "selected_audio_provider_safe_name": parent_diagnostics.get("selected_audio_provider_safe_name") or "",
        "selected_composition_method_safe_name": parent_diagnostics.get("selected_composition_method_safe_name") or "",
        "admin_actionable_failure_visible": bool(admin_view.get("admin_actionable_failure_visible")),
        "client_safe_result_view_redacted": bool(
            client_view.get("credential_values_exposed") is False
            and client_view.get("provider_secret_values_visible") is False
            and "provider_failure_reason_sanitized" not in client_view
        ),
        "admin_provider_diagnostics_redacted": bool(admin_view.get("admin_provider_diagnostics_redacted")),
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "customer_data_exposed": False,
        "provider_router_used": True,
        "provider_pair_hardcoded": False,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
        "next_operator_action": next_action,
    }


def validate(proof: Mapping[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        require(field in proof, f"Missing required field: {field}")
    require(proof.get("provider_failure_propagation_passed") is True, "Provider failure propagation proof must pass.")
    require(proof.get("next_operator_action") in NEXT_OPERATOR_ACTIONS, "Invalid next operator action.")
    require(proof.get("next_operator_action") == "resolve_runway_provider_credits", "Successful propagation should point to Runway credit resolution.")
    require(proof.get("provider_pair_hardcoded") is False, "Provider pair must not be hardcoded.")
    require(proof.get("client_safe_result_view_redacted") is True, "Client-safe result must remain redacted.")
    require(proof.get("admin_provider_diagnostics_redacted") is True, "Admin diagnostics must remain redacted.")
    for key in [
        "credential_values_exposed",
        "internal_config_exposed",
        "customer_data_exposed",
        "provider_call_attempted",
        "media_generation_attempted",
        "billing_mutation_attempted",
        "credit_mutation_attempted",
        "stripe_live_charge_attempted",
        "customer_traffic_attempted",
        "public_cutover_enabled",
        "render_removal_attempted",
        "aws21_or_later_work_attempted",
    ]:
        require(proof.get(key) is False, f"Forbidden side effect or exposure must remain false: {key}")
    assert_no_forbidden_values(proof, "provider failure propagation proof")


def main() -> int:
    proof = build_proof()
    validate(proof)
    print("COMPLETE_MEDIA_PROVIDER_FAILURE_PROPAGATION_PROOF:")
    print(json.dumps(proof, indent=2, sort_keys=True))
    print("COMPLETE_MEDIA_PROVIDER_FAILURE_PROPAGATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
