from pathlib import Path

p = Path("frontend/src/app/api/client-latest-deliverable/route.ts")

p.write_text("""import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

function getBearer(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";

  if (auth.toLowerCase().startsWith("bearer ")) {
    return auth;
  }

  const cookieToken =
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    "";

  return cookieToken ? "Bearer " + cookieToken : "";
}

function safeText(value: any, fallback = ""): string {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return fallback;

  if (typeof value === "object") {
    const preferred =
      value?.provider_execution?.generated_content ||
      value?.provider_connector?.generated_content ||
      value?.generated_content ||
      value?.content ||
      value?.summary ||
      value?.message ||
      value?.safe_client_message ||
      "";

    if (typeof preferred === "string" && preferred.trim()) {
      return preferred;
    }

    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return fallback;
    }
  }

  return String(value);
}

function flattenDeliverable(latest: any) {
  const raw =
    latest?.deliverable ||
    latest?.result ||
    latest?.output ||
    latest?.execution_result ||
    latest?.payload ||
    {};

  const outputText = safeText(raw);

  return {
    title:
      safeText(raw?.title) ||
      safeText(latest?.title) ||
      "Latest client deliverable",
    summary:
      safeText(raw?.summary) ||
      safeText(latest?.summary) ||
      "Client-safe governed deliverable generated from the latest execution.",
    output: outputText,
    generated_output: outputText,
    content: outputText,
    image_url: safeText(raw?.image_url),
    asset_url: safeText(raw?.asset_url),
    preview_url: safeText(raw?.preview_url),
    media_pack: raw?.media_pack || {},
    generation_jobs: Array.isArray(raw?.generation_jobs) ? raw.generation_jobs : [],
    voiceover_script: safeText(raw?.voiceover_script),
    video_prompt: safeText(raw?.video_prompt),
    avatar_prompt: safeText(raw?.avatar_prompt),
    supports_audio: Boolean(raw?.supports_audio),
    supports_video: Boolean(raw?.supports_video),
    supports_avatar_video: Boolean(raw?.supports_avatar_video),
    tags: Array.isArray(raw?.tags) ? raw.tags : ["Live execution", "Client-safe", "Generated output"],
    created_at: safeText(raw?.created_at || latest?.created_at || latest?.created_at_iso),
  };
}

export async function GET(req: NextRequest) {
  try {
    const bearer = getBearer(req);

    const tenantId =
      req.headers.get("x-tenant-id") ||
      req.cookies.get("tenant_id")?.value ||
      "owner_managed_demo_client";

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "x-actor-role": req.headers.get("x-actor-role") || "client",
      "x-tenant-id": tenantId,
    };

    if (bearer) {
      headers.Authorization = bearer;
    }

    const url =
      BACKEND_URL +
      "/client/execution-events?tenant_id=" +
      encodeURIComponent(tenantId) +
      "&project_id=default_project&limit=20";

    const response = await fetch(url, {
      method: "GET",
      headers,
      cache: "no-store",
    });

    const data = await response.json();

    const latest =
      data?.events?.[0] ||
      data?.executions?.[0] ||
      data?.records?.[0] ||
      null;

    return NextResponse.json({
      success: true,
      source: "backend_runtime_flattened",
      execution: latest,
      deliverable: latest ? flattenDeliverable(latest) : null,
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: "client_latest_deliverable_proxy_failed",
      detail: String(error),
    });
  }
}
""", encoding="utf-8")

print("CLIENT_LATEST_DELIVERABLE_FLATTENED")