import { NextRequest, NextResponse } from "next/server";

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
    "User-Agent": "frontend-universal-complete-media-proxy/1.0",
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

    const data = await response.json().catch(() => ({ success: false, error: "invalid_backend_json" }));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "universal_complete_media_status_proxy_failed",
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
      prompt: payload.prompt || payload.task || "",
      agent_id: payload.agent_id || payload.assigned_agent || "social_media_manager_content_creator_agent",
      output_type: payload.output_type || "complete_video",
      industry: payload.industry || "",
      target_audience: payload.target_audience || "",
      platform: payload.platform || "general",
      duration_seconds: payload.duration_seconds || payload.duration || "5",
      aspect_ratio: payload.aspect_ratio || "9:16",
      language: payload.language || "English",
      accent: payload.accent || "",
      tone: payload.tone || "natural, polished, human",
      voice_style: payload.voice_style || "natural conversational voice",
      age_range: payload.age_range || "",
      gender_presentation: payload.gender_presentation || "",
      ethnicity_or_cultural_appearance: payload.ethnicity_or_cultural_appearance || payload.ethnicity || "",
      avatar_likeness: payload.avatar_likeness || payload.ultra_human_likeness || "",
      face_shape: payload.face_shape || "",
      skin_tone: payload.skin_tone || "",
      facial_features: payload.facial_features || "",
      hair_style: payload.hair_style || "",
      hair_colour: payload.hair_colour || payload.hair_color || "",
      eye_colour: payload.eye_colour || payload.eye_color || "",
      wardrobe: payload.wardrobe || "",
      expressions: payload.expressions || payload.facial_expressions || "",
      emotion: payload.emotion || "",
      eye_contact: payload.eye_contact || "",
      gestures: payload.gestures || payload.hand_gestures || "",
      body_language: payload.body_language || "",
      lip_sync_accuracy: payload.lip_sync_accuracy || "high when avatar or talking-head output is requested",
      speaking_pace: payload.speaking_pace || "natural, not rushed",
      camera_framing: payload.camera_framing || "",
      lighting_style: payload.lighting_style || "",
      background_setting: payload.background_setting || payload.setting || "",
      brand_style: payload.brand_style || "",
      product_or_service_details: payload.product_or_service_details || "",
      offer: payload.offer || payload.promotion || "",
      call_to_action: payload.call_to_action || payload.cta || "",
      captions: payload.captions || payload.subtitles || "",
      music_style: payload.music_style || "",
      sound_effects: payload.sound_effects || payload.sfx || "",
      pacing: payload.pacing || "smooth, clear, premium",
      visual_style: payload.visual_style || "",
      camera_movement: payload.camera_movement || "",
      compliance_notes: payload.compliance_notes || "",
      number_of_variations: payload.number_of_variations || "1",
      final_delivery_format: payload.final_delivery_format || "mp4",
      video_provider: payload.video_provider || "runway",
      audio_provider: payload.audio_provider || "elevenlabs",
      owner_approved: true,
      owner_approval_granted: true,
    };

    const response = await fetch(`${backendBaseUrl()}/admin/universal-complete-media`, {
      method: "POST",
      headers: adminHeaders(),
      body: JSON.stringify(safePayload),
      cache: "no-store",
    });

    const data = await response.json().catch(() => ({ success: false, error: "invalid_backend_json" }));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "universal_complete_media_proxy_failed",
        message: error instanceof Error ? error.message : "Unknown proxy error",
        customer_safe: true,
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
