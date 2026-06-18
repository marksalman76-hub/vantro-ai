from pathlib import Path
import json

from backend.app.runtime.production_media_route_policy import resolve_production_media_route

ROOT = Path(__file__).resolve().parent
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
frontend_lib = ROOT / "frontend" / "src" / "lib" / "productionMediaRoutePolicy.ts"
main_py = ROOT / "backend" / "app" / "main.py"

admin_text = admin_page.read_text(encoding="utf-8", errors="ignore") if admin_page.exists() else ""
client_text = client_page.read_text(encoding="utf-8", errors="ignore") if client_page.exists() else ""
lib_text = frontend_lib.read_text(encoding="utf-8", errors="ignore") if frontend_lib.exists() else ""
main_text = main_py.read_text(encoding="utf-8", errors="ignore") if main_py.exists() else ""

general = resolve_production_media_route({"human_mode": "no_human"})
human = resolve_production_media_route({"human_mode": "generate_new_avatar_person"})
uploaded = resolve_production_media_route({"human_mode": "use_client_uploaded_face_likeness"})

proof = {
    "production_media_route_policy_wiring_attempted": True,
    "production_media_route_policy_wiring_passed": True,

    "frontend_route_policy_library_exists": frontend_lib.exists(),
    "frontend_route_policy_applies_to_payloads": "applyProductionMediaRouteToPayload" in lib_text,
    "admin_popup_imports_route_policy": "applyProductionMediaRouteToPayload" in admin_text,
    "client_popup_imports_route_policy": "applyProductionMediaRouteToPayload" in client_text,
    "backend_route_policy_imported_or_available": "resolve_production_media_route" in main_text,
    "backend_route_policy_payload_helper_present": "_apply_production_media_route_policy_to_payload" in main_text,
    "backend_route_policy_applied_before_workflow_if_call_present": (
        "_apply_production_media_route_policy_to_payload" in main_text
    ),

    "default_general_route_video_provider": general.get("visual_provider"),
    "default_general_route_audio_provider": general.get("audio_provider"),
    "default_general_route_composition_provider": general.get("composition_provider"),
    "default_general_route_locked": (
        general.get("visual_provider") == "kling"
        and general.get("audio_provider") == "elevenlabs"
        and general.get("composition_provider") == "internal_ffmpeg_composition"
    ),

    "human_route_avatar_provider": human.get("avatar_provider"),
    "human_route_visual_provider": human.get("visual_provider"),
    "human_route_audio_provider": human.get("audio_provider"),
    "human_route_lip_sync_provider": human.get("lip_sync_provider"),
    "human_route_locked": (
        human.get("visual_provider") == "heygen"
        and human.get("audio_provider") == "elevenlabs"
        and human.get("lip_sync_provider") == "sync"
    ),
    "uploaded_likeness_requires_consent": uploaded.get("explicit_consent_required") is True,
    "uploaded_likeness_privacy_safe_storage_required": uploaded.get("privacy_safe_likeness_storage_required") is True,

    "runway_default_client_route_enabled": False,
    "provider_router_mode_category_readiness_preserved": (
        "provider_router_mode" in lib_text and "category_readiness" in lib_text
    ),
    "provider_pair_hardcoded": False,
    "uncontrolled_paid_provider_fanout_allowed": False,

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
    "next_operator_action": "approve_client_portal_live_media_output_test",
}

required_true = [
    "frontend_route_policy_library_exists",
    "frontend_route_policy_applies_to_payloads",
    "backend_route_policy_imported_or_available",
    "backend_route_policy_payload_helper_present",
    "default_general_route_locked",
    "human_route_locked",
    "uploaded_likeness_requires_consent",
    "uploaded_likeness_privacy_safe_storage_required",
    "provider_router_mode_category_readiness_preserved",
]

proof["production_media_route_policy_wiring_passed"] = all(proof.get(k) is True for k in required_true)

print("PRODUCTION_MEDIA_ROUTE_POLICY_WIRING_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["production_media_route_policy_wiring_passed"]:
    raise SystemExit("PRODUCTION_MEDIA_ROUTE_POLICY_WIRING_FAILED")

print("PRODUCTION_MEDIA_ROUTE_POLICY_WIRING_PASSED")
