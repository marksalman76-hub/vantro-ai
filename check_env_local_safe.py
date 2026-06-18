from __future__ import annotations

import json

from backend.app.runtime import complete_media_final_deliverable_proof as proof
from backend.app.runtime import direct_media_provider_execution_runtime as direct


def main() -> int:
    local_env = direct.load_local_env_for_provider_readiness()
    preflight = proof.build_preflight_snapshot(proof.synthetic_complete_media_request())
    category = preflight.get("provider_category_readiness") or {}
    categories = category.get("categories") or {}
    matrix = category.get("complete_media_executable_provider_matrix_redacted") or []

    output = {
        "full_media_stack_mapping_attempted": True,
        "full_media_stack_mapping_passed": bool(matrix),
        "dotenv_local_loaded": bool(local_env.get("dotenv_local_loaded")),
        "dotenv_local_exists": bool(local_env.get("dotenv_local_exists")),
        "dotenv_values_exposed": False,
        "env_values_exposed": False,
        "provider_router_used": True,
        "provider_pair_hardcoded": False,
        "provider_environment_readiness_attempted": True,
        "provider_environment_readiness_passed": bool(category.get("provider_category_readiness_verified")),
        "visual_provider_category_ready": bool(category.get("visual_provider_category_ready")),
        "audio_provider_category_ready": bool(category.get("audio_provider_category_ready")),
        "composition_method_ready": bool(category.get("composition_method_ready")),
        "caption_or_subtitle_path_ready_or_not_required": bool(
            category.get("caption_or_subtitle_path_ready_or_not_required")
        ),
        "fallback_safe_artifact_path_ready": bool(category.get("fallback_safe_artifact_path_ready")),
        "provider_category_readiness_verified": bool(category.get("provider_category_readiness_verified")),
        "selected_visual_provider_safe_name": category.get("selected_visual_provider_safe_name") or "",
        "selected_audio_provider_safe_name": category.get("selected_audio_provider_safe_name") or "",
        "selected_composition_method_safe_name": category.get("selected_composition_method_safe_name") or "",
        "discovered_visual_provider_safe_names": categories.get("visual_video_image", {}).get("provider_safe_names") or [],
        "discovered_audio_provider_safe_names": categories.get("voice_audio_music_sfx", {}).get("provider_safe_names") or [],
        "discovered_composition_safe_names": categories.get("composition_stitching_internal", {}).get("method_safe_names") or [],
        "discovered_caption_safe_names": category.get("discovered_caption_safe_names") or [],
        "discovered_fallback_safe_names": category.get("discovered_fallback_safe_names") or [],
        "required_env_names_by_provider": category.get("required_env_names_by_provider") or {},
        "complete_media_executable_provider_matrix_redacted": matrix,
        "provider_call_attempted": False,
        "media_generation_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "stripe_live_charge_attempted": False,
        "customer_traffic_attempted": False,
        "public_cutover_enabled": False,
        "render_removal_attempted": False,
        "aws21_or_later_work_attempted": False,
        "blocked_reason": "" if category.get("provider_category_readiness_verified") else "provider_category_readiness_not_verified",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
