from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import inspect
from typing import Any, Dict, Mapping, Optional

from backend.app.runtime import direct_media_provider_execution_runtime as direct_media
from backend.app.runtime.billing_credit_spend_governance import (
    evaluate_provider_cost_cap,
    redact_secret_values,
)


COMPLETE_MEDIA_FINAL_DELIVERABLE_PROOF_VERSION = "complete_media_final_deliverable_proof_v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def safe_hash(value: Any, length: int = 12) -> str:
    text = clean_text(value, 2000)
    if not text:
        return ""
    return sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:length]


def base_side_effect_guards() -> Dict[str, bool]:
    return {
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "stripe_call_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
        "media_generation_attempted": False,
        "customer_asset_used": False,
        "customer_likeness_used": False,
    }


def synthetic_complete_media_request(overrides: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "job_id": "synthetic_complete_media_final_deliverable_job",
        "customer_id": "synthetic_non_customer",
        "tenant_id": "synthetic_non_customer_tenant",
        "actor_role": "owner",
        "requested_by_role": "owner",
        "selected_agent": "ugc_media_agent",
        "selected_agents": ["ugc_media_agent"],
        "agent_ids": ["ugc_media_agent"],
        "multi_agent_media_execution": False,
        "requested_from": "complete_media_final_deliverable_proof",
        "media_type": "complete_video",
        "asset_type": "video",
        "output_type": "video",
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "duration_seconds": 5,
        "aspect_ratio": "9:16",
        "platform": "internal proof",
        "business_name": "Synthetic Non-Customer Proof",
        "product_or_service": "synthetic media workflow proof",
        "audience": "internal owner review only",
        "goal": "prove final deliverable safety gate without customer traffic",
        "offer": "no commercial offer",
        "call_to_action": "review the proof safely",
        "tone": "natural, confident, professional, warm",
        "human_avatar_mode": "No human/avatar",
        "prompt": (
            "Synthetic non-customer five second complete-media proof. "
            "Create a low-risk abstract visual card with no people, no brand, "
            "no customer asset, and a short voiceover saying this is an internal proof."
        ),
        "media_prompt": (
            "Synthetic non-customer five second complete-media proof with no people, "
            "no customer files, and no real brand."
        ),
        "owner_approved": True,
        "owner_approval_granted": True,
        "owner_provider_cost_approval": True,
        "cost_safety_confirmed": True,
        "paid_provider_risk_confirmed": True,
        "credit_risk_acknowledged": True,
        "two_provider_smoke_test": True,
        "two_provider_call_smoke_test": True,
        "complete_media_final_deliverable_proof": True,
        "max_visual_provider_calls": 1,
        "max_audio_provider_calls": 1,
        "max_total_provider_calls": 2,
        "max_provider_retries": 0,
        "provider_estimated_cost": 1,
        "provider_cost_cap": 2,
        "approval_required_for_spend": True,
        "approval_status": "owner_approved",
        "credit_reservation_status": "not_mutated_synthetic_proof",
        "dry_run": True,
        "preflight_only": True,
        "smoke_test_mode": True,
        "run_smoke_test": True,
        "customer_asset_used": False,
        "customer_likeness_used": False,
    }
    payload.update(dict(overrides or {}))
    return payload


def analyse_current_complete_media_provider_attempt_shape() -> Dict[str, Any]:
    source = inspect.getsource(direct_media.start_universal_complete_media_workflow)
    visual_call_present = "_run_visual_segment" in source and "\"media_type\": \"video\"" in source
    audio_call_present = "_run_audio_job" in source and "\"media_type\": \"audio\"" in source
    concurrent_execution_present = "ThreadPoolExecutor" in source and "executor.submit(_run_audio_job)" in source
    two_provider_cap_present = all(
        marker in source
        for marker in [
            "two_provider_smoke_test",
            "max_visual_provider_calls",
            "max_audio_provider_calls",
            "max_total_provider_calls",
            "max_provider_retries",
        ]
    )
    current_provider_call_floor = int(visual_call_present) + int(audio_call_present)
    return {
        "visual_provider_call_present": visual_call_present,
        "audio_provider_call_present": audio_call_present,
        "concurrent_execution_present": concurrent_execution_present,
        "current_complete_media_provider_call_floor": current_provider_call_floor,
        "dedicated_two_provider_attempt_cap_present": two_provider_cap_present,
        "two_provider_attempt_cap_satisfied": bool(
            two_provider_cap_present
            and visual_call_present
            and audio_call_present
            and current_provider_call_floor <= 2
        ),
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_preflight_snapshot(payload: Mapping[str, Any]) -> Dict[str, Any]:
    safe_payload = dict(payload)
    plan = direct_media.build_universal_complete_media_plan(safe_payload)
    packet = direct_media.build_media_script_packet(safe_payload, plan)
    segment_plan = direct_media._ucm_build_segment_plan_from_script(  # noqa: SLF001
        packet,
        float(packet.get("requested_duration_seconds") or safe_payload.get("duration_seconds") or 5),
        int(packet.get("provider_safe_segment_seconds") or 5),
    )
    packet["segment_plan"] = segment_plan[:1]
    packet["segment_count"] = len(packet["segment_plan"])
    preflight = direct_media._ucm_preflight_universal_media_job(  # noqa: SLF001
        safe_payload,
        plan,
        packet,
    )
    return redact_secret_values({
        "preflight_status": preflight.get("status"),
        "preflight_success": bool(preflight.get("success")),
        "failed_preflight_checks": preflight.get("failed_preflight_checks") or [],
        "blocked_provider_calls": preflight.get("blocked_provider_calls") or [],
        "estimated_credit_risk": preflight.get("estimated_credit_risk") or {},
        "estimated_duration_seconds": preflight.get("estimated_duration_seconds"),
        "requested_duration_seconds": preflight.get("requested_duration_seconds"),
        "segment_count": preflight.get("segment_count"),
        "script_ready": bool(preflight.get("script_ready")),
        "script_duration_fit": preflight.get("script_duration_fit"),
        "executable_visual_provider_count": len(preflight.get("executable_visual_providers") or []),
        "executable_audio_provider_count": len(preflight.get("executable_audio_providers") or []),
        "composition_path_available": bool(preflight.get("composition_path_available")),
        "customer_safe": True,
        "credential_values_exposed": False,
    })


def build_client_safe_result_view(proof: Mapping[str, Any]) -> Dict[str, Any]:
    passed = bool(proof.get("complete_media_final_deliverable_passed"))
    return {
        "status": "final_deliverable_ready" if passed else "final_deliverable_proof_blocked",
        "message": (
            "The capped complete-media proof is ready for review."
            if passed
            else "Complete media proof was blocked before paid provider execution."
        ),
        "job_reference_hash": proof.get("synthetic_job_reference_hash"),
        "provider_call_attempted": bool(proof.get("provider_call_attempted")),
        "final_asset_ready": bool(proof.get("durable_asset_storage_passed") and passed),
        "support_available": bool(proof.get("failure_path_supportable")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "raw_provider_response_exposed": False,
        "raw_storage_identifiers_exposed": False,
    }


def build_admin_provider_diagnostics(proof: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "status": proof.get("status"),
        "proof_blocked_reason": proof.get("proof_blocked_reason"),
        "provider_selected_redacted_or_named_safe": proof.get("provider_selected_redacted_or_named_safe"),
        "provider_call_attempted": bool(proof.get("provider_call_attempted")),
        "provider_call_count": int(proof.get("provider_call_count") or 0),
        "provider_attempt_shape": proof.get("provider_attempt_shape"),
        "preflight_status": (proof.get("preflight_snapshot") or {}).get("preflight_status"),
        "failed_preflight_checks": (proof.get("preflight_snapshot") or {}).get("failed_preflight_checks") or [],
        "durable_status_flow": proof.get("durable_status_flow"),
        "next_operator_action": proof.get("next_operator_action"),
        "admin_provider_diagnostics_redacted": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "raw_provider_response_exposed": False,
        "raw_infrastructure_identifiers_exposed": False,
        "customer_safe": True,
    }


def build_complete_media_final_deliverable_proof(
    payload: Optional[Mapping[str, Any]] = None,
    *,
    asset_delivery_result: Optional[Mapping[str, Any]] = None,
    allow_live_provider_attempt: bool = False,
) -> Dict[str, Any]:
    safe_payload = synthetic_complete_media_request(payload)
    provider_attempt_shape = analyse_current_complete_media_provider_attempt_shape()
    cost_cap_decision = evaluate_provider_cost_cap(safe_payload)
    over_cap_block = evaluate_provider_cost_cap({
        **safe_payload,
        "actor_role": "client",
        "requested_by_role": "client",
        "provider_estimated_cost": 30,
        "provider_cost_cap": safe_payload.get("provider_cost_cap") or 2,
        "owner_provider_cost_approval": False,
        "cost_safety_confirmed": False,
        "paid_provider_risk_confirmed": False,
        "credit_risk_acknowledged": False,
    })
    preflight_snapshot = build_preflight_snapshot(safe_payload)

    two_provider_cap_satisfied = bool(provider_attempt_shape.get("two_provider_attempt_cap_satisfied"))
    live_call_allowed = bool(allow_live_provider_attempt and two_provider_cap_satisfied)
    blocked_reason = ""
    if not two_provider_cap_satisfied:
        blocked_reason = "blocked_two_provider_attempt_cap_not_enforced"
    elif not preflight_snapshot.get("preflight_success"):
        blocked_reason = "blocked_provider_readiness_not_verified"
    elif not live_call_allowed:
        blocked_reason = "blocked_live_provider_execution_not_requested"

    durable_asset_storage_passed = bool(
        asset_delivery_result
        and asset_delivery_result.get("durable_asset_proof_passed") is True
        and asset_delivery_result.get("asset_store_passed") is True
        and asset_delivery_result.get("asset_open_or_download_proof_passed") is True
    )

    durable_status_flow = [
        {"status": "accepted", "customer_safe": True},
        {"status": "preflight", "customer_safe": True},
        {
            "status": "blocked_before_provider_call" if blocked_reason else "ready_for_two_provider_attempt",
            "customer_safe": True,
        },
    ]

    provider_call_attempted = False
    provider_call_count = 0
    proof = {
        "boundary": "complete_media_final_deliverable_proof",
        "diagnostic_version": COMPLETE_MEDIA_FINAL_DELIVERABLE_PROOF_VERSION,
        "created_at": utc_now(),
        "status": "complete_media_final_deliverable_blocked" if blocked_reason else "complete_media_final_deliverable_ready_for_live_attempt",
        "proof_blocked_reason": blocked_reason,
        "complete_media_final_deliverable_attempted": True,
        "complete_media_final_deliverable_passed": False,
        "owner_provider_approval_required": True,
        "provider_cost_cap_enforced": bool(
            cost_cap_decision.get("provider_execution_allowed_after_cost_gate") is True
            and over_cap_block.get("provider_cost_cap_blocked_without_approval") is True
        ),
        "provider_call_attempted": provider_call_attempted,
        "provider_call_count": provider_call_count,
        "visual_provider_call_count": 0,
        "audio_provider_call_count": 0,
        "provider_retry_count": 0,
        "provider_selected_redacted_or_named_safe": clean_text(safe_payload.get("video_provider") or "runway", 80),
        "long_form_generation_blocked_or_not_requested": bool(float(safe_payload.get("duration_seconds") or 0) <= 5),
        "multi_agent_provider_fanout_blocked": bool(
            not safe_payload.get("multi_agent_media_execution")
            and len(safe_payload.get("selected_agents") or []) == 1
        ),
        "synthetic_non_customer_request": True,
        "durable_status_flow_passed": bool(durable_status_flow and blocked_reason),
        "provider_output_or_failure_recorded": bool(blocked_reason),
        "durable_asset_storage_passed": durable_asset_storage_passed,
        "client_safe_result_view_redacted": True,
        "admin_provider_diagnostics_redacted": True,
        "failure_path_supportable": bool(blocked_reason),
        "preflight_passed_before_provider_call": bool(preflight_snapshot.get("preflight_success")),
        "provider_attempt_shape": provider_attempt_shape,
        "preflight_snapshot": preflight_snapshot,
        "cost_cap_decision": cost_cap_decision,
        "over_cap_block_decision": over_cap_block,
        "durable_status_flow": durable_status_flow,
        "asset_delivery_reference": {
            "durable_asset_proof_passed": bool(asset_delivery_result and asset_delivery_result.get("durable_asset_proof_passed")),
            "synthetic_asset_reference_hash": (asset_delivery_result or {}).get("synthetic_asset_reference_hash", ""),
            "client_safe_asset_view_redacted": bool(asset_delivery_result and asset_delivery_result.get("client_safe_asset_view_redacted")),
            "admin_asset_diagnostics_redacted": bool(asset_delivery_result and asset_delivery_result.get("admin_asset_diagnostics_redacted")),
            "customer_safe": True,
            "credential_values_exposed": False,
        },
        "next_operator_action": (
            "Load/verify Runway and ElevenLabs credentials in the execution environment, then rerun one "
            "bounded two-provider-call 5s smoke with the same caps."
            if blocked_reason == "blocked_provider_readiness_not_verified"
            else "Owner must either approve the capped two-provider-call proof shape or add a dedicated "
            "single-provider final-deliverable proof lane before live execution."
            if blocked_reason == "blocked_two_provider_attempt_cap_not_enforced"
            else "Resolve the sanitized blocker, then rerun one capped proof after owner approval."
        ),
        "synthetic_job_reference_hash": safe_hash(safe_payload.get("job_id")),
        "synthetic_tenant_reference_hash": safe_hash(safe_payload.get("tenant_id")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        **base_side_effect_guards(),
    }
    proof["client_safe_result_view"] = build_client_safe_result_view(proof)
    proof["admin_provider_diagnostics"] = build_admin_provider_diagnostics(proof)
    return redact_secret_values(proof)
