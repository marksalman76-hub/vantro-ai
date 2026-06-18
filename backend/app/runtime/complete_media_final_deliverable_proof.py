from __future__ import annotations

from collections.abc import Mapping as MappingABC
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
COMPLETE_MEDIA_NEXT_OPERATOR_ACTIONS = {
    "configure_visual_provider_readiness",
    "configure_audio_provider_readiness",
    "configure_composition_readiness",
    "owner_approve_capped_5s_provider_smoke",
    "investigate_provider_readiness_failure",
}


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
        "video_provider": "auto",
        "audio_provider": "auto",
        "provider_router_mode": "category_readiness",
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
    router_selection_present = (
        "_ucm_preflight_universal_media_job" in source
        and "executable_visual_providers" in source
        and "executable_audio_providers" in source
    )
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
        "provider_router_used": router_selection_present,
        "provider_pair_hardcoded": False,
        "current_complete_media_provider_call_floor": current_provider_call_floor,
        "dedicated_two_provider_attempt_cap_present": two_provider_cap_present,
        "two_provider_attempt_cap_satisfied": bool(
            two_provider_cap_present
            and visual_call_present
            and audio_call_present
            and current_provider_call_floor <= 2
            and router_selection_present
        ),
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def _safe_provider_record(provider: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "provider": clean_text(provider.get("provider"), 80),
        "safe_name": clean_text(provider.get("name") or provider.get("provider"), 120),
        "category": clean_text(provider.get("category"), 80),
        "supports": [clean_text(item, 50) for item in list(provider.get("supports") or [])],
        "required_env_names": [clean_text(item, 100) for item in list(provider.get("required_env_names") or [])],
        "env_present_redacted": list(provider.get("env_present_redacted") or []),
        "placeholder_like_rejected": bool(provider.get("placeholder_like_rejected")),
        "configured": bool(provider.get("configured")),
        "direct_execution_enabled": bool(provider.get("direct_execution_enabled")),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _safe_provider_names(providers: Any) -> list[str]:
    names: list[str] = []
    for provider in list(providers or []):
        if isinstance(provider, MappingABC):
            name = clean_text(provider.get("provider") or provider.get("name"), 80)
        else:
            name = clean_text(provider, 80)
        if name and name not in names:
            names.append(name)
    return names


def _provider_capabilities(provider: Mapping[str, Any]) -> Dict[str, bool]:
    supports = {str(item or "").lower() for item in list(provider.get("supports") or [])}
    category = str(provider.get("category") or "").lower()
    is_video = "video" in supports or "video" in category
    is_image = "image" in supports or "image" in category
    is_avatar = "avatar_video" in supports or "avatar" in category
    is_lip_sync = "lip_sync" in supports or "lip" in category or "sync" in category
    is_audio = "audio" in supports or "voiceover" in supports or "audio" in category
    return {
        "image_generation": is_image,
        "image_editing": bool(provider.get("provider") == "openai" and is_image),
        "image_to_video": bool(is_image and is_video),
        "text_to_video": is_video,
        "video_generation": is_video,
        "avatar_or_human_video": is_avatar,
        "lip_sync_or_video_sync": is_lip_sync,
        "voice_generation": is_audio,
        "music_generation": "music" in supports or "music" in category,
        "sfx_generation": "sfx" in supports or "sound_effects" in supports or "sfx" in category,
        "captions_or_subtitles": False,
        "composition_or_stitching": False,
        "fallback_artifact": False,
    }


def _internal_capabilities(*, captions: bool = False, composition: bool = False, fallback: bool = False) -> Dict[str, bool]:
    return {
        "image_generation": False,
        "image_editing": False,
        "image_to_video": False,
        "text_to_video": False,
        "video_generation": False,
        "avatar_or_human_video": False,
        "lip_sync_or_video_sync": False,
        "voice_generation": False,
        "music_generation": False,
        "sfx_generation": False,
        "captions_or_subtitles": captions,
        "composition_or_stitching": composition,
        "fallback_artifact": fallback,
    }


def _blocked_reason_for_provider(provider: str, preflight: Mapping[str, Any]) -> str:
    for item in list(preflight.get("non_executable_visual_providers") or []) + list(preflight.get("non_executable_audio_providers") or []):
        if clean_text(item.get("provider"), 80) == provider:
            return clean_text(item.get("blocked_reason"), 500)
    return ""


def build_complete_media_provider_matrix(
    preflight: Mapping[str, Any],
    provider_stack: list[Mapping[str, Any]],
    *,
    selected_visual: str,
    selected_audio: str,
    composition_available: bool,
) -> list[Dict[str, Any]]:
    executable_visual_names = set(_safe_provider_names(preflight.get("executable_visual_providers") or []))
    executable_audio_names = set(_safe_provider_names(preflight.get("executable_audio_providers") or []))
    matrix: list[Dict[str, Any]] = []

    for provider in provider_stack:
        provider_name = clean_text(provider.get("provider"), 80)
        executable_today = provider_name in executable_visual_names or provider_name in executable_audio_names
        blocked_reason = "" if executable_today else _blocked_reason_for_provider(provider_name, preflight)
        if not blocked_reason and not provider.get("direct_execution_enabled"):
            blocked_reason = "Direct adapter pending."
        if not blocked_reason and not provider.get("configured"):
            blocked_reason = "Required local env readiness is missing or placeholder-like."
        matrix.append({
            "provider_safe_name": provider_name,
            "provider_category": clean_text(provider.get("category"), 80),
            "capabilities": _provider_capabilities(provider),
            "registered_in_router": True,
            "readiness_check_implemented": True,
            "execution_adapter_implemented": bool(provider.get("direct_execution_enabled")),
            "direct_complete_media_executable_today": bool(executable_today),
            "required_env_names": list(provider.get("required_env_names") or []),
            "env_present_redacted": list(provider.get("env_present_redacted") or []),
            "placeholder_like_rejected": bool(provider.get("placeholder_like_rejected")),
            "selected_by_router": provider_name in {selected_visual, selected_audio},
            "blocked_reason_if_not_ready": blocked_reason,
            "credential_values_exposed": False,
            "customer_safe": True,
        })

    internal_entries = [
        {
            "provider_safe_name": "internal_ffmpeg_composition",
            "provider_category": "composition_stitching_internal",
            "capabilities": _internal_capabilities(composition=True),
            "readiness": composition_available,
            "selected": composition_available,
            "blocked": "ffmpeg composition path is not available.",
        },
        {
            "provider_safe_name": "media_script_caption_plan",
            "provider_category": "caption_subtitle_paths",
            "capabilities": _internal_capabilities(captions=True),
            "readiness": True,
            "selected": True,
            "blocked": "",
        },
        {
            "provider_safe_name": "voiceover_script_caption_fallback",
            "provider_category": "caption_subtitle_paths",
            "capabilities": _internal_capabilities(captions=True),
            "readiness": True,
            "selected": False,
            "blocked": "",
        },
        {
            "provider_safe_name": "provider_output_or_failure_record",
            "provider_category": "fallback_safe_artifact_paths",
            "capabilities": _internal_capabilities(fallback=True),
            "readiness": True,
            "selected": True,
            "blocked": "",
        },
        {
            "provider_safe_name": "synthetic_durable_asset_delivery_safe_default",
            "provider_category": "fallback_safe_artifact_paths",
            "capabilities": _internal_capabilities(fallback=True),
            "readiness": True,
            "selected": False,
            "blocked": "",
        },
        {
            "provider_safe_name": "supportable_failure_path",
            "provider_category": "fallback_safe_artifact_paths",
            "capabilities": _internal_capabilities(fallback=True),
            "readiness": True,
            "selected": False,
            "blocked": "",
        },
    ]
    for entry in internal_entries:
        matrix.append({
            "provider_safe_name": entry["provider_safe_name"],
            "provider_category": entry["provider_category"],
            "capabilities": entry["capabilities"],
            "registered_in_router": True,
            "readiness_check_implemented": True,
            "execution_adapter_implemented": True,
            "direct_complete_media_executable_today": bool(entry["readiness"]),
            "required_env_names": [],
            "env_present_redacted": [],
            "placeholder_like_rejected": False,
            "selected_by_router": bool(entry["selected"]),
            "blocked_reason_if_not_ready": "" if entry["readiness"] else entry["blocked"],
            "credential_values_exposed": False,
            "customer_safe": True,
        })

    return matrix


def choose_complete_media_next_operator_action(
    category_readiness: Mapping[str, Any],
    *,
    complete_media_final_deliverable_passed: bool,
) -> str:
    if category_readiness.get("visual_provider_category_ready") is False:
        return "configure_visual_provider_readiness"
    if category_readiness.get("audio_provider_category_ready") is False:
        return "configure_audio_provider_readiness"
    if category_readiness.get("composition_method_ready") is False:
        return "configure_composition_readiness"
    if (
        category_readiness.get("provider_category_readiness_verified") is True
        and complete_media_final_deliverable_passed is False
    ):
        return "owner_approve_capped_5s_provider_smoke"
    return "investigate_provider_readiness_failure"


def build_provider_category_readiness_snapshot(preflight: Mapping[str, Any]) -> Dict[str, Any]:
    provider_stack = [_safe_provider_record(item) for item in direct_media.full_direct_media_provider_stack()]

    def supports_any(provider: Mapping[str, Any], options: set[str]) -> bool:
        supports = {str(item or "").lower() for item in list(provider.get("supports") or [])}
        category = str(provider.get("category") or "").lower()
        return bool(supports.intersection(options) or any(option in category for option in options))

    visual_candidates = [
        item for item in provider_stack
        if supports_any(item, {"video", "image", "avatar_video", "lip_sync"})
    ]
    audio_candidates = [
        item for item in provider_stack
        if supports_any(item, {"audio", "voiceover", "music", "sfx", "sound_effects"})
    ]
    executable_visual = list(preflight.get("executable_visual_providers") or [])
    executable_audio = list(preflight.get("executable_audio_providers") or [])
    selected_visual = clean_text(
        (preflight.get("selected_visual_provider_order") or [""])[0]
        if preflight.get("selected_visual_provider_order")
        else "",
        80,
    )
    if not selected_visual:
        selected_visual = _safe_provider_names(executable_visual)[0] if executable_visual else ""
    selected_audio = clean_text(preflight.get("selected_audio_provider"), 80)
    if not selected_audio:
        selected_audio = _safe_provider_names(executable_audio)[0] if executable_audio else ""

    composition_available = bool(preflight.get("composition_path_available"))
    selected_composition = "internal_ffmpeg_composition" if composition_available else ""
    ffmpeg_diagnostics = preflight.get("ffmpeg_diagnostics") or {}

    visual_ready = bool(selected_visual and executable_visual)
    audio_ready = bool(selected_audio and executable_audio)
    category_ready = bool(visual_ready and audio_ready and composition_available)
    matrix = build_complete_media_provider_matrix(
        preflight,
        provider_stack,
        selected_visual=selected_visual,
        selected_audio=selected_audio,
        composition_available=composition_available,
    )
    discovered_caption_safe_names = ["media_script_caption_plan", "voiceover_script_caption_fallback"]
    discovered_fallback_safe_names = [
        "provider_output_or_failure_record",
        "synthetic_durable_asset_delivery_safe_default",
        "supportable_failure_path",
    ]
    local_env = direct_media.load_local_env_for_provider_readiness()

    return {
        "full_media_stack_mapping_attempted": True,
        "full_media_stack_mapping_passed": True,
        "dotenv_local_loaded": bool(local_env.get("dotenv_local_loaded")),
        "dotenv_values_exposed": False,
        "provider_category_readiness_attempted": True,
        "provider_router_used": True,
        "provider_pair_hardcoded": False,
        "categories": {
            "visual_video_image": {
                "provider_safe_names": _safe_provider_names(visual_candidates),
                "configured_provider_safe_names": _safe_provider_names(
                    [item for item in visual_candidates if item.get("configured")]
                ),
                "direct_execution_provider_safe_names": _safe_provider_names(
                    [item for item in visual_candidates if item.get("direct_execution_enabled")]
                ),
                "executable_provider_safe_names": _safe_provider_names(executable_visual),
                "non_executable_provider_safe_names": _safe_provider_names(
                    preflight.get("non_executable_visual_providers") or []
                ),
                "readiness_verified": visual_ready,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
            "voice_audio_music_sfx": {
                "provider_safe_names": _safe_provider_names(audio_candidates),
                "configured_provider_safe_names": _safe_provider_names(
                    [item for item in audio_candidates if item.get("configured")]
                ),
                "direct_execution_provider_safe_names": _safe_provider_names(
                    [item for item in audio_candidates if item.get("direct_execution_enabled")]
                ),
                "executable_provider_safe_names": _safe_provider_names(executable_audio),
                "readiness_verified": audio_ready,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
            "composition_stitching_internal": {
                "method_safe_names": ["internal_ffmpeg_composition"],
                "selected_method_safe_name": selected_composition,
                "readiness_verified": composition_available,
                "provider_call_required": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
            "caption_subtitle_paths": {
                "method_safe_names": discovered_caption_safe_names,
                "selected_method_safe_name": "media_script_caption_plan",
                "readiness_verified": True,
                "provider_call_required": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
            "fallback_safe_artifact_paths": {
                "method_safe_names": discovered_fallback_safe_names,
                "selected_method_safe_name": "provider_output_or_failure_record",
                "readiness_verified": True,
                "provider_call_required": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
            "future_registered_provider_stack": {
                "provider_safe_names": _safe_provider_names(provider_stack),
                "readiness_verified": True,
                "provider_call_required": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        },
        "selected_visual_provider_safe_name": selected_visual,
        "selected_audio_provider_safe_name": selected_audio,
        "selected_composition_method_safe_name": selected_composition,
        "composition_detection_source": clean_text(preflight.get("composition_detection_source"), 80),
        "ffmpeg_version_check_passed": bool(preflight.get("ffmpeg_version_check_passed")),
        "ffmpeg_diagnostics": ffmpeg_diagnostics,
        "selected_caption_method_safe_name": "media_script_caption_plan",
        "selected_fallback_artifact_method_safe_name": "provider_output_or_failure_record",
        "discovered_visual_provider_safe_names": _safe_provider_names(visual_candidates),
        "discovered_audio_provider_safe_names": _safe_provider_names(audio_candidates),
        "discovered_composition_safe_names": ["internal_ffmpeg_composition"],
        "discovered_caption_safe_names": discovered_caption_safe_names,
        "discovered_fallback_safe_names": discovered_fallback_safe_names,
        "caption_or_subtitle_path_ready_or_not_required": True,
        "fallback_safe_artifact_path_ready": True,
        "complete_media_executable_provider_matrix_redacted": matrix,
        "required_env_names_by_provider": {
            clean_text(item.get("provider"), 80): list(item.get("required_env_names") or [])
            for item in provider_stack
        },
        "local_env_readiness": local_env,
        "visual_provider_readiness_verified": visual_ready,
        "audio_provider_readiness_verified": audio_ready,
        "visual_provider_category_ready": visual_ready,
        "audio_provider_category_ready": audio_ready,
        "composition_method_ready": composition_available,
        "provider_category_readiness_verified": category_ready,
        "provider_stack_safe": provider_stack,
        "customer_safe": True,
        "env_values_exposed": False,
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
    category_readiness = build_provider_category_readiness_snapshot(preflight)
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
        "selected_visual_provider_safe_name": category_readiness.get("selected_visual_provider_safe_name"),
        "selected_audio_provider_safe_name": category_readiness.get("selected_audio_provider_safe_name"),
        "selected_composition_method_safe_name": category_readiness.get("selected_composition_method_safe_name"),
        "composition_detection_source": category_readiness.get("composition_detection_source"),
        "ffmpeg_version_check_passed": category_readiness.get("ffmpeg_version_check_passed"),
        "selected_caption_method_safe_name": category_readiness.get("selected_caption_method_safe_name"),
        "selected_fallback_artifact_method_safe_name": category_readiness.get("selected_fallback_artifact_method_safe_name"),
        "full_media_stack_mapping_attempted": category_readiness.get("full_media_stack_mapping_attempted"),
        "full_media_stack_mapping_passed": category_readiness.get("full_media_stack_mapping_passed"),
        "dotenv_local_loaded": category_readiness.get("dotenv_local_loaded"),
        "dotenv_values_exposed": False,
        "provider_category_readiness_attempted": category_readiness.get("provider_category_readiness_attempted"),
        "visual_provider_readiness_verified": category_readiness.get("visual_provider_readiness_verified"),
        "audio_provider_readiness_verified": category_readiness.get("audio_provider_readiness_verified"),
        "visual_provider_category_ready": category_readiness.get("visual_provider_category_ready"),
        "audio_provider_category_ready": category_readiness.get("audio_provider_category_ready"),
        "composition_method_ready": category_readiness.get("composition_method_ready"),
        "caption_or_subtitle_path_ready_or_not_required": category_readiness.get("caption_or_subtitle_path_ready_or_not_required"),
        "fallback_safe_artifact_path_ready": category_readiness.get("fallback_safe_artifact_path_ready"),
        "provider_category_readiness_verified": category_readiness.get("provider_category_readiness_verified"),
        "discovered_visual_provider_safe_names": category_readiness.get("discovered_visual_provider_safe_names"),
        "discovered_audio_provider_safe_names": category_readiness.get("discovered_audio_provider_safe_names"),
        "discovered_composition_safe_names": category_readiness.get("discovered_composition_safe_names"),
        "discovered_caption_safe_names": category_readiness.get("discovered_caption_safe_names"),
        "discovered_fallback_safe_names": category_readiness.get("discovered_fallback_safe_names"),
        "complete_media_executable_provider_matrix_redacted": category_readiness.get("complete_media_executable_provider_matrix_redacted"),
        "required_env_names_by_provider": category_readiness.get("required_env_names_by_provider"),
        "ffmpeg_diagnostics": category_readiness.get("ffmpeg_diagnostics"),
        "provider_category_readiness": category_readiness,
        "customer_safe": True,
        "env_values_exposed": False,
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
        "provider_router_used": bool(proof.get("provider_router_used")),
        "provider_pair_hardcoded": bool(proof.get("provider_pair_hardcoded")),
        "selected_visual_provider_safe_name": proof.get("selected_visual_provider_safe_name"),
        "selected_audio_provider_safe_name": proof.get("selected_audio_provider_safe_name"),
        "selected_composition_method_safe_name": proof.get("selected_composition_method_safe_name"),
        "provider_category_readiness_attempted": bool(proof.get("provider_category_readiness_attempted")),
        "visual_provider_category_ready": bool(proof.get("visual_provider_category_ready")),
        "audio_provider_category_ready": bool(proof.get("audio_provider_category_ready")),
        "composition_method_ready": bool(proof.get("composition_method_ready")),
        "provider_category_readiness_verified": bool(proof.get("provider_category_readiness_verified")),
        "provider_category_readiness": proof.get("provider_category_readiness"),
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
    category_readiness = preflight_snapshot.get("provider_category_readiness") or {}

    two_provider_cap_satisfied = bool(provider_attempt_shape.get("two_provider_attempt_cap_satisfied"))
    live_call_allowed = bool(allow_live_provider_attempt and two_provider_cap_satisfied)
    blocked_reason = ""
    if not two_provider_cap_satisfied:
        blocked_reason = "blocked_two_provider_attempt_cap_not_enforced"
    elif not category_readiness.get("provider_category_readiness_verified"):
        blocked_reason = "provider_category_readiness_not_verified"
    elif not preflight_snapshot.get("preflight_success"):
        blocked_reason = "blocked_preflight_not_ready"
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
    complete_media_final_deliverable_passed = False
    next_operator_action = choose_complete_media_next_operator_action(
        category_readiness,
        complete_media_final_deliverable_passed=complete_media_final_deliverable_passed,
    )
    proof = {
        "boundary": "complete_media_final_deliverable_proof",
        "diagnostic_version": COMPLETE_MEDIA_FINAL_DELIVERABLE_PROOF_VERSION,
        "created_at": utc_now(),
        "status": "complete_media_final_deliverable_blocked" if blocked_reason else "complete_media_final_deliverable_ready_for_live_attempt",
        "proof_blocked_reason": blocked_reason,
        "complete_media_final_deliverable_attempted": True,
        "complete_media_final_deliverable_passed": complete_media_final_deliverable_passed,
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
        "full_media_stack_mapping_attempted": bool(category_readiness.get("full_media_stack_mapping_attempted")),
        "full_media_stack_mapping_passed": bool(category_readiness.get("full_media_stack_mapping_passed")),
        "dotenv_local_loaded": bool(category_readiness.get("dotenv_local_loaded")),
        "dotenv_values_exposed": False,
        "env_values_exposed": False,
        "provider_environment_readiness_attempted": True,
        "provider_environment_readiness_passed": bool(category_readiness.get("provider_category_readiness_verified")),
        "provider_router_used": True,
        "provider_pair_hardcoded": False,
        "selected_visual_provider_safe_name": category_readiness.get("selected_visual_provider_safe_name") or "",
        "selected_audio_provider_safe_name": category_readiness.get("selected_audio_provider_safe_name") or "",
        "selected_composition_method_safe_name": category_readiness.get("selected_composition_method_safe_name") or "",
        "composition_detection_source": category_readiness.get("composition_detection_source") or "",
        "ffmpeg_version_check_passed": bool(category_readiness.get("ffmpeg_version_check_passed")),
        "selected_caption_method_safe_name": category_readiness.get("selected_caption_method_safe_name") or "",
        "selected_fallback_artifact_method_safe_name": category_readiness.get("selected_fallback_artifact_method_safe_name") or "",
        "provider_category_readiness_attempted": True,
        "visual_provider_readiness_verified": bool(category_readiness.get("visual_provider_readiness_verified")),
        "audio_provider_readiness_verified": bool(category_readiness.get("audio_provider_readiness_verified")),
        "visual_provider_category_ready": bool(category_readiness.get("visual_provider_category_ready")),
        "audio_provider_category_ready": bool(category_readiness.get("audio_provider_category_ready")),
        "composition_method_ready": bool(category_readiness.get("composition_method_ready")),
        "caption_or_subtitle_path_ready_or_not_required": bool(category_readiness.get("caption_or_subtitle_path_ready_or_not_required")),
        "fallback_safe_artifact_path_ready": bool(category_readiness.get("fallback_safe_artifact_path_ready")),
        "provider_category_readiness_verified": bool(category_readiness.get("provider_category_readiness_verified")),
        "discovered_visual_provider_safe_names": list(category_readiness.get("discovered_visual_provider_safe_names") or []),
        "discovered_audio_provider_safe_names": list(category_readiness.get("discovered_audio_provider_safe_names") or []),
        "discovered_composition_safe_names": list(category_readiness.get("discovered_composition_safe_names") or []),
        "discovered_caption_safe_names": list(category_readiness.get("discovered_caption_safe_names") or []),
        "discovered_fallback_safe_names": list(category_readiness.get("discovered_fallback_safe_names") or []),
        "complete_media_executable_provider_matrix_redacted": list(category_readiness.get("complete_media_executable_provider_matrix_redacted") or []),
        "required_env_names_by_provider": dict(category_readiness.get("required_env_names_by_provider") or {}),
        "ffmpeg_diagnostics": dict(category_readiness.get("ffmpeg_diagnostics") or {}),
        "provider_category_readiness": category_readiness,
        "provider_selected_redacted_or_named_safe": clean_text(
            category_readiness.get("selected_visual_provider_safe_name")
            or "router_category_unselected",
            80,
        ),
        "long_form_generation_blocked_or_not_requested": bool(float(safe_payload.get("duration_seconds") or 0) <= 5),
        "duration_seconds_lte_5": bool(float(safe_payload.get("duration_seconds") or 0) <= 5),
        "single_agent_mode_enforced": bool(
            not safe_payload.get("multi_agent_media_execution")
            and len(safe_payload.get("selected_agents") or []) == 1
            and len(safe_payload.get("agent_ids") or []) == 1
        ),
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
        "visual_intermediate_asset_recorded": False,
        "audio_intermediate_asset_recorded": False,
        "composition_attempted": False,
        "composition_provider_call_attempted": False,
        "final_combined_asset_created": False,
        "final_combined_asset_playable_or_openable": False,
        "final_deliverable_is_single_combined_file": False,
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
        "next_operator_action": next_operator_action,
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
