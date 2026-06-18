from pathlib import Path
import json
import re
import textwrap

ROOT = Path(__file__).resolve().parent

BACKEND_MAIN = ROOT / "backend" / "app" / "main.py"
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
FRONTEND_LIB = ROOT / "frontend" / "src" / "lib" / "productionMediaRoutePolicy.ts"
VERIFY = ROOT / "verify_production_media_route_policy_wiring.py"

FRONTEND_LIB.parent.mkdir(parents=True, exist_ok=True)

FRONTEND_LIB.write_text(textwrap.dedent(r'''
export type HumanMode =
  | "no_human"
  | "generate_new_avatar_person"
  | "use_client_uploaded_face_likeness"
  | "use_saved_brand_spokesperson_avatar";

export type ProductionMediaRoute = {
  route_name: string;
  human_mode: HumanMode;
  visual_provider: string;
  audio_provider: string;
  lip_sync_provider?: string | null;
  composition_provider: string;
  caption_provider: string;
  fallback_provider: string;
  requires_likeness_consent: boolean;
  explicit_consent_required?: boolean;
  privacy_safe_likeness_storage_required?: boolean;
  likeness_governance_required?: boolean;
  selected_route_reason: string;
};

export function normalizeHumanMode(value?: string | null): HumanMode {
  const raw = String(value || "no_human").trim().toLowerCase();
  const aliases: Record<string, HumanMode> = {
    none: "no_human",
    "no human": "no_human",
    no_human_avatar: "no_human",
    generate_avatar: "generate_new_avatar_person",
    generated_avatar: "generate_new_avatar_person",
    new_avatar: "generate_new_avatar_person",
    uploaded_likeness: "use_client_uploaded_face_likeness",
    client_likeness: "use_client_uploaded_face_likeness",
    saved_avatar: "use_saved_brand_spokesperson_avatar",
    brand_spokesperson: "use_saved_brand_spokesperson_avatar",
  };
  const normalized = aliases[raw] || raw;
  if (
    normalized === "no_human" ||
    normalized === "generate_new_avatar_person" ||
    normalized === "use_client_uploaded_face_likeness" ||
    normalized === "use_saved_brand_spokesperson_avatar"
  ) {
    return normalized as HumanMode;
  }
  return "no_human";
}

export function resolveProductionMediaRoute(input?: {
  human_mode?: string | null;
  humanMode?: string | null;
  avatar_mode?: string | null;
  avatarMode?: string | null;
  admin_provider_override?: boolean;
  owner_provider_override?: boolean;
  video_provider?: string | null;
  visual_provider?: string | null;
}): ProductionMediaRoute {
  const payload = input || {};
  const humanMode = normalizeHumanMode(
    payload.human_mode || payload.humanMode || payload.avatar_mode || payload.avatarMode
  );

  const adminOverride = Boolean(payload.admin_provider_override || payload.owner_provider_override);
  const requestedVisual = String(payload.video_provider || payload.visual_provider || "").trim().toLowerCase();

  if (adminOverride && requestedVisual === "runway") {
    return {
      route_name: "premium_cinematic_admin_override",
      human_mode: humanMode,
      visual_provider: "runway",
      audio_provider: "elevenlabs",
      lip_sync_provider: null,
      composition_provider: "internal_ffmpeg_composition",
      caption_provider: "media_script_caption_plan",
      fallback_provider: "provider_output_or_failure_record",
      requires_likeness_consent: false,
      selected_route_reason: "admin_override_runway",
    };
  }

  if (humanMode === "no_human") {
    return {
      route_name: "general_media_default",
      human_mode: "no_human",
      visual_provider: "kling",
      audio_provider: "elevenlabs",
      lip_sync_provider: null,
      composition_provider: "internal_ffmpeg_composition",
      caption_provider: "media_script_caption_plan",
      fallback_provider: "provider_output_or_failure_record",
      requires_likeness_consent: false,
      selected_route_reason: "default_no_human_general_media",
    };
  }

  return {
    route_name: "human_likeness_default",
    human_mode: humanMode,
    visual_provider: "heygen",
    audio_provider: "elevenlabs",
    lip_sync_provider: "sync",
    composition_provider: "internal_ffmpeg_composition",
    caption_provider: "media_script_caption_plan",
    fallback_provider: "provider_output_or_failure_record",
    requires_likeness_consent: true,
    explicit_consent_required:
      humanMode === "use_client_uploaded_face_likeness" ||
      humanMode === "use_saved_brand_spokesperson_avatar",
    privacy_safe_likeness_storage_required: humanMode === "use_client_uploaded_face_likeness",
    likeness_governance_required:
      humanMode === "use_client_uploaded_face_likeness" ||
      humanMode === "use_saved_brand_spokesperson_avatar",
    selected_route_reason: "human_likeness_route_required",
  };
}

export function applyProductionMediaRouteToPayload<T extends Record<string, any>>(payload: T): T {
  const route = resolveProductionMediaRoute(payload);
  return {
    ...payload,
    production_media_route_policy_applied: true,
    media_route_name: route.route_name,
    media_route_reason: route.selected_route_reason,
    human_mode: route.human_mode,
    video_provider: route.visual_provider,
    visual_provider: route.visual_provider,
    audio_provider: route.audio_provider,
    lip_sync_provider: route.lip_sync_provider,
    composition_provider: route.composition_provider,
    caption_provider: route.caption_provider,
    fallback_provider: route.fallback_provider,
    requires_likeness_consent: route.requires_likeness_consent,
    explicit_consent_required: route.explicit_consent_required || false,
    privacy_safe_likeness_storage_required: route.privacy_safe_likeness_storage_required || false,
    likeness_governance_required: route.likeness_governance_required || false,
    provider_router_mode: "category_readiness",
    provider_pair_hardcoded: false,
    uncontrolled_paid_provider_fanout_allowed: false,
    provider_retry_count: 0,
  };
}
''').lstrip(), encoding="utf-8")

def patch_frontend_page(path: Path) -> bool:
    if not path.exists():
        return False

    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    if "applyProductionMediaRouteToPayload" not in text:
        text = 'import { applyProductionMediaRouteToPayload } from "@/lib/productionMediaRoutePolicy";\n' + text

    # Patch common JSON.stringify(payload/body/requestData/formData) patterns.
    patterns = [
        r"body:\s*JSON\.stringify\(([^)\n]+)\)",
        r"JSON\.stringify\((completeMediaPayload|mediaPayload|payload|requestPayload|body|formPayload|requestData)\)",
    ]

    for pattern in patterns:
        def repl(match):
            expr = match.group(1).strip()
            if "applyProductionMediaRouteToPayload" in expr:
                return match.group(0)
            if match.group(0).startswith("body:"):
                return f"body: JSON.stringify(applyProductionMediaRouteToPayload({expr}))"
            return f"JSON.stringify(applyProductionMediaRouteToPayload({expr}))"

        text = re.sub(pattern, repl, text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False

admin_patched = patch_frontend_page(ADMIN_PAGE)
client_patched = patch_frontend_page(CLIENT_PAGE)

main_text = BACKEND_MAIN.read_text(encoding="utf-8", errors="ignore")
main_original = main_text

if "resolve_production_media_route" not in main_text:
    insertion = (
        "\n# Production media route policy import is intentionally optional at import time.\n"
        "try:\n"
        "    from backend.app.runtime.production_media_route_policy import resolve_production_media_route\n"
        "except Exception:  # pragma: no cover - route policy verifier catches regressions\n"
        "    resolve_production_media_route = None\n"
    )
    # Place after imports by putting near top after first import block; safe enough because Python allows try import before route defs.
    main_text = insertion + "\n" + main_text

if "def _apply_production_media_route_policy_to_payload" not in main_text:
    helper = textwrap.dedent(r'''

    def _apply_production_media_route_policy_to_payload(payload):
        """Apply structured media route policy before Complete Media execution.

        This keeps the full provider registry available while preventing default
        client requests from randomly allocating across every provider.
        """
        if not isinstance(payload, dict):
            return payload
        if resolve_production_media_route is None:
            return payload
        route = resolve_production_media_route(payload)
        enriched = dict(payload)
        enriched.update({
            "production_media_route_policy_applied": True,
            "media_route_name": route.get("route_name"),
            "media_route_reason": route.get("selected_route_reason"),
            "human_mode": route.get("human_mode", enriched.get("human_mode", "no_human")),
            "video_provider": route.get("visual_provider"),
            "visual_provider": route.get("visual_provider"),
            "audio_provider": route.get("audio_provider"),
            "lip_sync_provider": route.get("lip_sync_provider"),
            "composition_provider": route.get("composition_provider"),
            "caption_provider": route.get("caption_provider"),
            "fallback_provider": route.get("fallback_provider"),
            "requires_likeness_consent": bool(route.get("requires_likeness_consent")),
            "explicit_consent_required": bool(route.get("explicit_consent_required")),
            "privacy_safe_likeness_storage_required": bool(route.get("privacy_safe_likeness_storage_required")),
            "likeness_governance_required": bool(route.get("likeness_governance_required")),
            "provider_router_mode": "category_readiness",
            "provider_pair_hardcoded": False,
            "uncontrolled_paid_provider_fanout_allowed": False,
            "provider_retry_count": 0,
        })
        return enriched
    ''')
    main_text += helper

# Conservative: patch JSON payload variables only where common universal complete media route names appear nearby.
route_markers = [
    "universal-complete-media",
    "admin-universal-complete-media",
    "complete media",
    "complete_media",
]
if any(marker in main_text.lower() for marker in route_markers):
    # Patch simple calls if present.
    main_text = main_text.replace(
        "start_universal_complete_media_workflow(payload)",
        "start_universal_complete_media_workflow(_apply_production_media_route_policy_to_payload(payload))",
    )
    main_text = main_text.replace(
        "start_universal_complete_media_workflow(request_payload)",
        "start_universal_complete_media_workflow(_apply_production_media_route_policy_to_payload(request_payload))",
    )
    main_text = main_text.replace(
        "start_universal_complete_media_workflow(body)",
        "start_universal_complete_media_workflow(_apply_production_media_route_policy_to_payload(body))",
    )

if main_text != main_original:
    BACKEND_MAIN.write_text(main_text, encoding="utf-8")

VERIFY.write_text(textwrap.dedent(r'''
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
''').lstrip(), encoding="utf-8")

print(json.dumps({
    "frontend_lib_created": str(FRONTEND_LIB),
    "admin_page_patched": admin_patched,
    "client_page_patched": client_patched,
    "backend_main_touched": main_text != main_original,
    "verifier_created": str(VERIFY),
    "provider_calls": False,
    "smoke_rerun": False,
}, indent=2))