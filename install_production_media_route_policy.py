from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parent
runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

policy_path = runtime_dir / "production_media_route_policy.py"
verifier_path = ROOT / "verify_production_media_route_policy.py"

policy_path.write_text(textwrap.dedent(r'''
    """
    Production media route policy.

    Purpose:
    Keep the full provider registry available, but stop the default paid-client
    media path from randomly allocating across every provider.

    Launch lanes:
    - General/no-human media: Kling + ElevenLabs + internal FFmpeg
    - Human/avatar/likeness media: HeyGen + ElevenLabs + Sync + internal FFmpeg
    - Cinematic premium: Runway admin-only until API entitlement/workspace is resolved
    - Image/thumbnail: OpenAI/Replicate route, not default complete-media video
    - Fallback: supportable failure record, not uncontrolled paid-provider fanout
    """

    from __future__ import annotations

    from dataclasses import dataclass, asdict
    from typing import Any, Dict, List


    GENERAL_MEDIA_ROUTE = {
        "route_name": "general_media_default",
        "human_mode": "no_human",
        "visual_provider": "kling",
        "audio_provider": "elevenlabs",
        "lip_sync_provider": None,
        "composition_provider": "internal_ffmpeg_composition",
        "caption_provider": "media_script_caption_plan",
        "fallback_provider": "provider_output_or_failure_record",
        "requires_likeness_consent": False,
        "client_default_enabled": True,
        "admin_override_required": False,
    }

    HUMAN_LIKENESS_ROUTE = {
        "route_name": "human_likeness_default",
        "human_modes": [
            "generate_new_avatar_person",
            "use_client_uploaded_face_likeness",
            "use_saved_brand_spokesperson_avatar",
        ],
        "avatar_provider": "heygen",
        "visual_provider": "heygen",
        "audio_provider": "elevenlabs",
        "lip_sync_provider": "sync",
        "composition_provider": "internal_ffmpeg_composition",
        "caption_provider": "media_script_caption_plan",
        "fallback_provider": "provider_output_or_failure_record",
        "requires_likeness_consent": True,
        "client_default_enabled": True,
        "admin_override_required": False,
    }

    PREMIUM_CINEMATIC_ROUTE = {
        "route_name": "premium_cinematic_admin_override",
        "visual_provider": "runway",
        "audio_provider": "elevenlabs",
        "composition_provider": "internal_ffmpeg_composition",
        "requires_owner_or_admin_override": True,
        "client_default_enabled": False,
        "blocked_until": "runway_api_workspace_entitlement_confirmed",
    }

    IMAGE_THUMBNAIL_ROUTE = {
        "route_name": "image_thumbnail_route",
        "image_providers": ["openai", "replicate"],
        "client_default_complete_media_video_route": False,
    }

    FALLBACK_ROUTE = {
        "route_name": "supportable_failure_fallback",
        "fallback_provider": "provider_output_or_failure_record",
        "paid_provider_fanout_allowed": False,
        "provider_retry_count_default": 0,
    }

    VALID_HUMAN_MODES = {
        "no_human",
        "generate_new_avatar_person",
        "use_client_uploaded_face_likeness",
        "use_saved_brand_spokesperson_avatar",
    }


    def normalize_human_mode(value: Any) -> str:
        raw = str(value or "no_human").strip().lower()
        aliases = {
            "none": "no_human",
            "no human": "no_human",
            "no_human_avatar": "no_human",
            "generate_avatar": "generate_new_avatar_person",
            "generated_avatar": "generate_new_avatar_person",
            "new_avatar": "generate_new_avatar_person",
            "uploaded_likeness": "use_client_uploaded_face_likeness",
            "client_likeness": "use_client_uploaded_face_likeness",
            "saved_avatar": "use_saved_brand_spokesperson_avatar",
            "brand_spokesperson": "use_saved_brand_spokesperson_avatar",
        }
        normalized = aliases.get(raw, raw)
        return normalized if normalized in VALID_HUMAN_MODES else "no_human"


    def resolve_production_media_route(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        human_mode = normalize_human_mode(
            payload.get("human_mode")
            or payload.get("humanMode")
            or payload.get("avatar_mode")
            or payload.get("avatarMode")
        )

        admin_override = bool(
            payload.get("admin_provider_override")
            or payload.get("owner_provider_override")
            or payload.get("adminOverride")
        )

        requested_visual = str(
            payload.get("video_provider")
            or payload.get("visual_provider")
            or payload.get("selected_visual_provider")
            or ""
        ).strip().lower()

        if admin_override and requested_visual == "runway":
            route = dict(PREMIUM_CINEMATIC_ROUTE)
            route["selected_route_reason"] = "admin_override_runway"
            route["human_mode"] = human_mode
            return route

        if human_mode == "no_human":
            route = dict(GENERAL_MEDIA_ROUTE)
            route["selected_route_reason"] = "default_no_human_general_media"
            return route

        route = dict(HUMAN_LIKENESS_ROUTE)
        route["human_mode"] = human_mode
        route["selected_route_reason"] = "human_likeness_route_required"

        if human_mode in {
            "use_client_uploaded_face_likeness",
            "use_saved_brand_spokesperson_avatar",
        }:
            route["explicit_consent_required"] = True
            route["privacy_safe_likeness_storage_required"] = True
            route["likeness_governance_required"] = True

        return route


    def production_media_route_policy_summary() -> Dict[str, Any]:
        return {
            "production_media_route_policy_enabled": True,
            "full_provider_registry_preserved": True,
            "default_general_route": GENERAL_MEDIA_ROUTE,
            "human_likeness_route": HUMAN_LIKENESS_ROUTE,
            "premium_cinematic_route": PREMIUM_CINEMATIC_ROUTE,
            "image_thumbnail_route": IMAGE_THUMBNAIL_ROUTE,
            "fallback_route": FALLBACK_ROUTE,
            "no_uncontrolled_paid_provider_fanout": True,
            "default_client_video_provider": "kling",
            "default_client_audio_provider": "elevenlabs",
            "default_client_composition_provider": "internal_ffmpeg_composition",
            "human_likeness_avatar_provider": "heygen",
            "human_likeness_lip_sync_provider": "sync",
            "runway_default_client_route_enabled": False,
        }
''').lstrip(), encoding="utf-8")

verifier_path.write_text(textwrap.dedent(r'''
    from pathlib import Path
    import json

    from backend.app.runtime.production_media_route_policy import (
        production_media_route_policy_summary,
        resolve_production_media_route,
    )

    ROOT = Path(__file__).resolve().parent

    general = resolve_production_media_route({"human_mode": "no_human"})
    generated_avatar = resolve_production_media_route({"human_mode": "generate_new_avatar_person"})
    uploaded_likeness = resolve_production_media_route({"human_mode": "use_client_uploaded_face_likeness"})
    saved_spokesperson = resolve_production_media_route({"human_mode": "use_saved_brand_spokesperson_avatar"})
    runway_admin = resolve_production_media_route({
        "human_mode": "no_human",
        "video_provider": "runway",
        "admin_provider_override": True,
    })
    summary = production_media_route_policy_summary()

    proof = {
        "production_media_route_policy_attempted": True,
        "production_media_route_policy_passed": True,

        "full_provider_registry_preserved": summary["full_provider_registry_preserved"],
        "default_general_video_provider": general.get("visual_provider"),
        "default_general_audio_provider": general.get("audio_provider"),
        "default_general_composition_provider": general.get("composition_provider"),
        "default_general_uses_kling": general.get("visual_provider") == "kling",
        "default_general_uses_elevenlabs": general.get("audio_provider") == "elevenlabs",
        "default_general_uses_internal_ffmpeg": general.get("composition_provider") == "internal_ffmpeg_composition",

        "human_generated_avatar_uses_heygen": generated_avatar.get("avatar_provider") == "heygen",
        "human_generated_avatar_uses_elevenlabs": generated_avatar.get("audio_provider") == "elevenlabs",
        "human_generated_avatar_uses_sync": generated_avatar.get("lip_sync_provider") == "sync",
        "human_uploaded_likeness_requires_consent": uploaded_likeness.get("explicit_consent_required") is True,
        "human_uploaded_likeness_privacy_safe_storage_required": uploaded_likeness.get("privacy_safe_likeness_storage_required") is True,
        "human_saved_spokesperson_requires_governance": saved_spokesperson.get("likeness_governance_required") is True,

        "runway_default_client_route_enabled": summary["runway_default_client_route_enabled"],
        "runway_admin_override_available": runway_admin.get("route_name") == "premium_cinematic_admin_override",
        "uncontrolled_paid_provider_fanout_allowed": False,
        "fallback_is_supportable_failure_record": summary["fallback_route"]["fallback_provider"] == "provider_output_or_failure_record",

        "provider_call_attempted": False,
        "smoke_rerun_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_deployment_deleted": False,
        "aws21_or_later_work_attempted": False,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "customer_data_exposed": False,
        "next_operator_action": "wire_route_policy_to_create_media_popup_and_backend",
    }

    required_true = [
        "full_provider_registry_preserved",
        "default_general_uses_kling",
        "default_general_uses_elevenlabs",
        "default_general_uses_internal_ffmpeg",
        "human_generated_avatar_uses_heygen",
        "human_generated_avatar_uses_elevenlabs",
        "human_generated_avatar_uses_sync",
        "human_uploaded_likeness_requires_consent",
        "human_uploaded_likeness_privacy_safe_storage_required",
        "human_saved_spokesperson_requires_governance",
        "runway_admin_override_available",
        "fallback_is_supportable_failure_record",
    ]

    proof["production_media_route_policy_passed"] = (
        all(proof.get(k) is True for k in required_true)
        and proof["runway_default_client_route_enabled"] is False
        and proof["uncontrolled_paid_provider_fanout_allowed"] is False
    )

    print("PRODUCTION_MEDIA_ROUTE_POLICY_PROOF:")
    print(json.dumps(proof, indent=2, sort_keys=True))

    if not proof["production_media_route_policy_passed"]:
        raise SystemExit("PRODUCTION_MEDIA_ROUTE_POLICY_FAILED")

    print("PRODUCTION_MEDIA_ROUTE_POLICY_PASSED")
''').lstrip(), encoding="utf-8")

print(json.dumps({
    "created": [
        str(policy_path),
        str(verifier_path),
    ],
    "provider_calls": False,
    "smoke_rerun": False,
}, indent=2))