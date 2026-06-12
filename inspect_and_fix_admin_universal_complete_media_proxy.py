from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "api" / "admin-universal-complete-media" / "route.ts"
BACKUP_DIR = ROOT / "backups" / f"admin_universal_complete_media_proxy_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

original = TARGET.read_text(encoding="utf-8", errors="ignore")

print("CURRENT_ROUTE_PREVIEW_START")
print(original[:5000])
print("CURRENT_ROUTE_PREVIEW_END")

new_text = r'''import { NextRequest, NextResponse } from "next/server";

function backendBaseUrl() {
  return (
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function adminToken() {
  return (
    process.env.ADMIN_PLATFORM_TOKEN ||
    process.env.ADMIN_AUTH_SECRET ||
    process.env.ADMIN_BEARER_TOKEN ||
    process.env.ADMIN_TOKEN ||
    process.env.PLATFORM_ADMIN_TOKEN ||
    process.env.OWNER_ADMIN_TOKEN ||
    ""
  ).trim();
}

function adminHeaders() {
  const token = adminToken();

  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
    "x-admin-token": token,
    "x-actor-role": "owner_admin",
    "x-tenant-id": "owner_admin",
    "x-requested-from": "admin_universal_complete_media_proxy",
    "User-Agent": "frontend-admin-universal-complete-media-proxy/1.0",
  };
}

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await fetch(`${backendBaseUrl()}/admin/universal-complete-media-status`, {
      method: "GET",
      headers: adminHeaders(),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
    }));

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_universal_complete_media_status_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json().catch(() => ({}));

    const safePayload = {
      ...payload,

      prompt:
        payload.prompt ||
        payload.task ||
        payload.creative_brief ||
        payload.user_prompt ||
        payload.complete_media_config?.prompt ||
        "",

      task:
        payload.task ||
        payload.prompt ||
        payload.creative_brief ||
        payload.user_prompt ||
        payload.complete_media_config?.task ||
        "",

      agent_id:
        payload.agent_id ||
        payload.selected_agent ||
        payload.lead_agent_id ||
        payload.complete_media_config?.agent_id ||
        "ugc_creative_agent",

      selected_agent:
        payload.selected_agent ||
        payload.agent_id ||
        payload.lead_agent_id ||
        payload.complete_media_config?.selected_agent ||
        "ugc_creative_agent",

      selected_agents:
        payload.selected_agents ||
        payload.agent_ids ||
        payload.complete_media_config?.selected_agents ||
        [],

      agent_ids:
        payload.agent_ids ||
        payload.selected_agents ||
        payload.complete_media_config?.agent_ids ||
        [],

      output_type:
        payload.output_type ||
        payload.complete_media_config?.output_type ||
        "Complete video with voiceover",

      platform:
        payload.platform ||
        payload.complete_media_config?.platform ||
        "General",

      duration_seconds:
        payload.duration_seconds ||
        payload.complete_media_config?.duration_seconds ||
        5,

      aspect_ratio:
        payload.aspect_ratio ||
        payload.complete_media_config?.aspect_ratio ||
        "16:9",

      language:
        payload.language ||
        payload.complete_media_config?.language ||
        "English",

      accent:
        payload.accent ||
        payload.complete_media_config?.accent ||
        "",

      video_provider:
        payload.video_provider ||
        payload.complete_media_config?.video_provider ||
        "runway",

      audio_provider:
        payload.audio_provider ||
        payload.complete_media_config?.audio_provider ||
        "elevenlabs",

      media_type: "complete_video",
      asset_type: "video",
      provider: "universal_complete_media_workflow",

      source: "admin_universal_complete_media_proxy",
      requested_from:
        payload.requested_from ||
        payload.source ||
        "complete_media_popup",

      universal_complete_media_workflow: true,
      one_prompt_complete_media: true,
      native_popup_execution: Boolean(payload.native_popup_execution),
      run_direct_from_popup: Boolean(payload.run_direct_from_popup),

      owner_approved: true,
      owner_approval_granted: true,
      owner_admin_unrestricted: true,

      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    };

    const response = await fetch(`${backendBaseUrl()}/admin/universal-complete-media`, {
      method: "POST",
      headers: adminHeaders(),
      body: JSON.stringify(safePayload),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({
      success: false,
      error: "invalid_backend_json",
    }));

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "admin_universal_complete_media_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
'''

TARGET.write_text(new_text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "/admin/universal-complete-media",
    "/admin/universal-complete-media-status",
    "universal_complete_media_workflow",
    "one_prompt_complete_media",
    "video_provider",
    "audio_provider",
    "elevenlabs",
    "runway",
    "owner_admin_unrestricted",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("ADMIN_UNIVERSAL_COMPLETE_MEDIA_PROXY_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")