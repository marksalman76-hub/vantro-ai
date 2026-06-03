export type RealMediaProviderKey =
  | "runway"
  | "kling"
  | "heygen"
  | "elevenlabs"
  | "replicate"
  | "openai";

export type RealMediaProviderCapability =
  | "image_generation"
  | "video_generation"
  | "avatar_video"
  | "voice_generation"
  | "dubbing"
  | "lip_sync"
  | "image_to_video"
  | "text_to_video";

export type RealMediaProviderConfig = {
  key: RealMediaProviderKey;
  label: string;
  configured: boolean;
  enabled: boolean;
  live_dispatch_allowed: boolean;
  owner_approval_required: boolean;
  supported_capabilities: RealMediaProviderCapability[];
  client_safe_status: string;
  reason: string;
};

export type MediaGenerationRequest = {
  tenant_key: string;
  requested_capability: RealMediaProviderCapability;
  prompt: string;
  asset_type?: string;
  owner_approved?: boolean;
  dry_run?: boolean;
};

export type MediaGenerationProviderDecision = {
  success: boolean;
  provider_selected: RealMediaProviderKey | null;
  provider_label: string | null;
  requested_capability: RealMediaProviderCapability;
  live_external_call_executed: false;
  external_action_performed: false;
  owner_approval_required: boolean;
  owner_approved: boolean;
  dry_run: boolean;
  client_safe_status: string;
  reason: string;
  available_providers: RealMediaProviderConfig[];
};

function envFlag(name: string): boolean {
  return String(process.env[name] || "").toLowerCase() === "true";
}

function hasEnv(name: string): boolean {
  return Boolean(String(process.env[name] || "").trim());
}

export function getRealMediaProviderRegistry(): RealMediaProviderConfig[] {
  const globalLiveDispatch =
    envFlag("REAL_MEDIA_PROVIDER_HTTP_DISPATCH_ENABLED") &&
    envFlag("OWNER_APPROVED_REAL_MEDIA_PROVIDER_EXECUTION");

  const configs: RealMediaProviderConfig[] = [
    {
      key: "runway",
      label: "Runway",
      configured: hasEnv("RUNWAY_API_KEY"),
      enabled: envFlag("ENABLE_RUNWAY_PROVIDER"),
      live_dispatch_allowed: false,
      owner_approval_required: true,
      supported_capabilities: ["video_generation", "image_to_video", "text_to_video"],
      client_safe_status: "Provider available after configuration",
      reason: "Runway is reserved for governed video/image-to-video generation.",
    },
    {
      key: "kling",
      label: "Kling",
      configured: hasEnv("KLING_API_KEY"),
      enabled: envFlag("ENABLE_KLING_PROVIDER"),
      live_dispatch_allowed: false,
      owner_approval_required: true,
      supported_capabilities: ["video_generation", "image_to_video", "text_to_video"],
      client_safe_status: "Provider available after configuration",
      reason: "Kling is reserved for governed video generation.",
    },
    {
      key: "heygen",
      label: "HeyGen",
      configured: hasEnv("HEYGEN_API_KEY"),
      enabled: envFlag("ENABLE_HEYGEN_PROVIDER"),
      live_dispatch_allowed: false,
      owner_approval_required: true,
      supported_capabilities: ["avatar_video", "dubbing", "lip_sync"],
      client_safe_status: "Provider available after configuration",
      reason: "HeyGen is reserved for governed avatar, dubbing, and lip-sync generation.",
    },
    {
      key: "elevenlabs",
      label: "ElevenLabs",
      configured: hasEnv("ELEVENLABS_API_KEY"),
      enabled: envFlag("ENABLE_ELEVENLABS_PROVIDER"),
      live_dispatch_allowed: false,
      owner_approval_required: true,
      supported_capabilities: ["voice_generation", "dubbing"],
      client_safe_status: "Provider available after configuration",
      reason: "ElevenLabs is reserved for governed voice and dubbing generation.",
    },
    {
      key: "replicate",
      label: "Replicate",
      configured: hasEnv("REPLICATE_API_TOKEN"),
      enabled: envFlag("ENABLE_REPLICATE_PROVIDER"),
      live_dispatch_allowed: false,
      owner_approval_required: true,
      supported_capabilities: ["image_generation", "video_generation"],
      client_safe_status: "Provider available after configuration",
      reason: "Replicate is reserved for governed image/video model routing.",
    },
    {
      key: "openai",
      label: "OpenAI",
      configured: hasEnv("OPENAI_API_KEY"),
      enabled: envFlag("ENABLE_OPENAI_MEDIA_PROVIDER"),
      live_dispatch_allowed: false,
      owner_approval_required: true,
      supported_capabilities: ["image_generation"],
      client_safe_status: "Provider available after configuration",
      reason: "OpenAI is reserved for governed image generation.",
    },
  ];

  return configs.map((provider) => ({
    ...provider,
    live_dispatch_allowed:
      globalLiveDispatch &&
      provider.configured &&
      provider.enabled,
    client_safe_status:
      provider.configured && provider.enabled
        ? "Provider configured and gated by owner approval"
        : provider.client_safe_status,
    reason:
      provider.configured && provider.enabled
        ? `${provider.label} is configured. Live dispatch remains owner-gated.`
        : provider.reason,
  }));
}

export function selectRealMediaProvider(
  request: MediaGenerationRequest
): MediaGenerationProviderDecision {
  const providers = getRealMediaProviderRegistry();
  const matching = providers.find(
    (provider) =>
      provider.supported_capabilities.includes(request.requested_capability) &&
      provider.configured &&
      provider.enabled
  );

  if (!matching) {
    return {
      success: false,
      provider_selected: null,
      provider_label: null,
      requested_capability: request.requested_capability,
      live_external_call_executed: false,
      external_action_performed: false,
      owner_approval_required: true,
      owner_approved: Boolean(request.owner_approved),
      dry_run: true,
      client_safe_status: "No configured real media provider is available for this request yet.",
      reason: "Provider registry is installed, but the matching provider is not configured/enabled.",
      available_providers: providers,
    };
  }

  const ownerApproved = Boolean(request.owner_approved);
  const dryRun = request.dry_run !== false || !matching.live_dispatch_allowed || !ownerApproved;

  return {
    success: true,
    provider_selected: matching.key,
    provider_label: matching.label,
    requested_capability: request.requested_capability,
    live_external_call_executed: false,
    external_action_performed: false,
    owner_approval_required: true,
    owner_approved: ownerApproved,
    dry_run: dryRun,
    client_safe_status: dryRun
      ? `${matching.label} selected in governed dry-run mode.`
      : `${matching.label} selected and ready for governed live dispatch.`,
    reason: dryRun
      ? "Live provider dispatch is intentionally gated until owner approval and live flags are enabled."
      : "Provider is configured, enabled, and owner-approved for live dispatch. Actual HTTP dispatch is added in the provider queue/failover row.",
    available_providers: providers,
  };
}

export function inferMediaCapability(payload: Record<string, unknown>): RealMediaProviderCapability {
  const raw = String(
    payload.requested_capability ||
    payload.media_capability ||
    payload.asset_type ||
    payload.generation_type ||
    payload.task ||
    payload.prompt ||
    ""
  ).toLowerCase();

  if (raw.includes("avatar")) return "avatar_video";
  if (raw.includes("voice")) return "voice_generation";
  if (raw.includes("dub")) return "dubbing";
  if (raw.includes("lip")) return "lip_sync";
  if (raw.includes("image to video")) return "image_to_video";
  if (raw.includes("video")) return "video_generation";
  if (raw.includes("image") || raw.includes("photo") || raw.includes("picture")) return "image_generation";

  return "image_generation";
}

export function attachRealMediaProviderDecision(
  tenantKey: string,
  payload: Record<string, unknown>
): Record<string, unknown> {
  const requestedCapability = inferMediaCapability(payload);
  const decision = selectRealMediaProvider({
    tenant_key: tenantKey,
    requested_capability: requestedCapability,
    prompt: String(payload.prompt || payload.task || ""),
    asset_type: String(payload.asset_type || ""),
    owner_approved: Boolean(payload.owner_approved || payload.owner_approval_granted),
    dry_run: true,
  });

  return {
    ...payload,
    real_media_generation_providers_enabled: true,
    provider_queue_retry_failover_ready: true,
    real_media_provider_decision: decision,
    provider_selected: decision.provider_selected,
    provider_label: decision.provider_label,
    requested_media_capability: requestedCapability,
    live_external_call_executed: false,
    external_action_performed: false,
  };
}
