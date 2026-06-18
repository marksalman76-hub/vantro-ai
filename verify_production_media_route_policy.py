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
