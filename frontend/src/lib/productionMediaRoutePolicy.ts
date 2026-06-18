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
