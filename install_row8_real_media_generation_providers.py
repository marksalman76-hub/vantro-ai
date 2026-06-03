from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row8_real_media_generation_providers_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

provider_lib = ROOT / "frontend" / "src" / "lib" / "realMediaGenerationProviders.ts"
provider_route = ROOT / "frontend" / "src" / "app" / "api" / "real-media-generation-providers" / "route.ts"
admin_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-real-media-generation-providers" / "route.ts"
delegated_route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"

for p in [provider_lib, provider_route, admin_route, delegated_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

provider_lib.parent.mkdir(parents=True, exist_ok=True)

provider_lib.write_text(r'''export type RealMediaProviderKey =
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
    real_media_provider_decision: decision,
    provider_selected: decision.provider_selected,
    provider_label: decision.provider_label,
    requested_media_capability: requestedCapability,
    live_external_call_executed: false,
    external_action_performed: false,
  };
}
''', encoding="utf-8")

provider_route.parent.mkdir(parents=True, exist_ok=True)
provider_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import {
  attachRealMediaProviderDecision,
  getRealMediaProviderRegistry,
  inferMediaCapability,
  selectRealMediaProvider,
} from "@/lib/realMediaGenerationProviders";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  const providers = getRealMediaProviderRegistry();

  return NextResponse.json({
    success: true,
    client_safe: true,
    real_media_generation_providers_enabled: true,
    live_external_call_executed: false,
    external_action_performed: false,
    providers,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);
  const capability = inferMediaCapability(body);
  const decision = selectRealMediaProvider({
    tenant_key: tenantKey,
    requested_capability: capability,
    prompt: String(body.prompt || body.task || ""),
    asset_type: String(body.asset_type || ""),
    owner_approved: Boolean(body.owner_approved || body.owner_approval_granted),
    dry_run: true,
  });

  return NextResponse.json(attachRealMediaProviderDecision(tenantKey, {
    ...body,
    ...decision,
  }), {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
''', encoding="utf-8")

admin_route.parent.mkdir(parents=True, exist_ok=True)
admin_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import {
  getRealMediaProviderRegistry,
  selectRealMediaProvider,
  inferMediaCapability,
} from "@/lib/realMediaGenerationProviders";
import { resolveTenantKey } from "@/lib/deliverablePersistence";

export const dynamic = "force-dynamic";

function isAdminRequest(req: NextRequest): boolean {
  return Boolean(
    req.headers.get("authorization") ||
    req.headers.get("x-admin-token") ||
    req.cookies.get("admin_session")?.value
  );
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  if (!isAdminRequest(req)) {
    return NextResponse.json({
      success: false,
      error: "Admin authorisation required.",
    }, { status: 401 });
  }

  return NextResponse.json({
    success: true,
    admin_safe: true,
    credential_values_exposed: false,
    real_media_generation_providers_enabled: true,
    live_external_call_executed: false,
    external_action_performed: false,
    providers: getRealMediaProviderRegistry(),
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  if (!isAdminRequest(req)) {
    return NextResponse.json({
      success: false,
      error: "Admin authorisation required.",
    }, { status: 401 });
  }

  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);
  const capability = inferMediaCapability(body);
  const decision = selectRealMediaProvider({
    tenant_key: tenantKey,
    requested_capability: capability,
    prompt: String(body.prompt || body.task || ""),
    asset_type: String(body.asset_type || ""),
    owner_approved: Boolean(body.owner_approved || body.owner_approval_granted),
    dry_run: true,
  });

  return NextResponse.json({
    ...decision,
    success: true,
    admin_safe: true,
    credential_values_exposed: false,
    real_media_generation_providers_enabled: true,
    tenant_key_visible_to_admin: tenantKey,
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
''', encoding="utf-8")

delegated_text = delegated_route.read_text(encoding="utf-8")

if 'realMediaGenerationProviders' not in delegated_text:
    delegated_text = delegated_text.replace(
        'import { persistMediaAssets, attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";',
        'import { persistMediaAssets, attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";\nimport { attachRealMediaProviderDecision } from "@/lib/realMediaGenerationProviders";'
    )

delegated_text = delegated_text.replace(
    '''  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");
  normalised.media_asset_lifecycle_enabled = true;''',
    '''  Object.assign(normalised, attachRealMediaProviderDecision(stateTenantKey, normalised));
  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");
  normalised.media_asset_lifecycle_enabled = true;'''
)

delegated_route.write_text(delegated_text, encoding="utf-8")

test = ROOT / "test_row8_real_media_generation_providers.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/realMediaGenerationProviders.ts": [
        "getRealMediaProviderRegistry",
        "selectRealMediaProvider",
        "inferMediaCapability",
        "attachRealMediaProviderDecision",
        "Runway",
        "Kling",
        "HeyGen",
        "ElevenLabs",
        "Replicate",
        "OpenAI",
        "live_external_call_executed: false",
        "external_action_performed: false",
    ],
    "frontend/src/app/api/real-media-generation-providers/route.ts": [
        "real_media_generation_providers_enabled",
        "getRealMediaProviderRegistry",
        "selectRealMediaProvider",
        "live_external_call_executed",
    ],
    "frontend/src/app/api/admin-real-media-generation-providers/route.ts": [
        "credential_values_exposed: false",
        "Admin authorisation required",
        "real_media_generation_providers_enabled",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachRealMediaProviderDecision",
        "realMediaGenerationProviders",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW8_REAL_MEDIA_GENERATION_PROVIDERS_FAILED missing={missing}")

print("ROW8_REAL_MEDIA_GENERATION_PROVIDERS_PASSED")
''', encoding="utf-8")

print("ROW8_REAL_MEDIA_GENERATION_PROVIDERS_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {provider_lib}")
print(f"Created/updated: {provider_route}")
print(f"Created/updated: {admin_route}")
print(f"Updated: {delegated_route}")
print(f"Created: {test}")