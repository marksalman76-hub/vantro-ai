import { NextRequest, NextResponse } from "next/server";

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

function safeText(value: unknown, fallback = ""): string {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return fallback;

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  if (typeof value === "object") {
    const item = value as any;

    const preferred =
      item?.provider_execution?.generated_content ||
      item?.provider_connector?.generated_content ||
      item?.provider_connector?.safe_client_message ||
      item?.live_execution_gate?.client_safe_message ||
      item?.generated_content ||
      item?.safe_client_message ||
      item?.message ||
      item?.summary ||
      item?.title ||
      "";

    if (typeof preferred === "string" && preferred.trim()) {
      return preferred;
    }

    if (typeof item?.content === "string" && item.content.trim()) {
      return item.content;
    }

    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return fallback;
    }
  }

  return String(value);
}

function firstString(...values: unknown[]): string {
  for (const value of values) {
    const text = safeText(value).trim();
    if (text) return text;
  }

  return "";
}

function extractGeneratedContent(source: any): string {
  return firstString(
    source?.provider_execution?.generated_content,
    source?.provider_execution?.metadata?.governed_live_call?.generated_content,
    source?.provider_execution?.provider_connector?.generated_content,
    source?.provider_connector?.generated_content,
    source?.output?.provider_execution?.generated_content,
    source?.output?.provider_execution?.metadata?.governed_live_call?.generated_content,
    source?.output?.provider_execution?.provider_connector?.generated_content,
    source?.output?.provider_connector?.generated_content,
    source?.output?.generated_content,
    source?.generated_content,
    source?.content
  );
}

function getRawDeliverable(latest: any) {
  return (
    latest?.deliverable ||
    latest?.result ||
    latest?.execution_result ||
    latest?.payload ||
    latest?.output ||
    {}
  );
}

function flattenDeliverable(latest: any) {
  const raw = getRawDeliverable(latest);
  const generatedContent =
    extractGeneratedContent(raw) ||
    extractGeneratedContent(latest) ||
    safeText(raw);

  const outputText =
    generatedContent ||
    safeText(raw?.content) ||
    safeText(raw?.output) ||
    safeText(raw?.summary) ||
    "Client-safe governed deliverable generated from the latest execution.";

  const mediaPack =
    raw?.media_pack && typeof raw.media_pack === "object" && !Array.isArray(raw.media_pack)
      ? raw.media_pack
      : {};

  const generationJobs = Array.isArray(raw?.generation_jobs)
    ? raw.generation_jobs.map((job: any) => ({
        job_type: safeText(job?.job_type || job?.type || "generation"),
        status: safeText(job?.status || "queued"),
        provider: safeText(job?.provider || ""),
        asset_url: safeText(job?.asset_url || job?.url || ""),
      }))
    : [];

  const tags = Array.isArray(raw?.tags)
    ? raw.tags.map((tag: unknown) => safeText(tag)).filter(Boolean)
    : ["Live execution", "Client-safe", "Generated output"];

  return {
    title:
      firstString(raw?.title, latest?.title) ||
      "Latest client deliverable",

    summary:
      firstString(raw?.summary, latest?.summary, raw?.safe_client_message, latest?.safe_client_message) ||
      "Client-safe governed deliverable generated from the latest execution.",

    output: outputText,
    generated_output: outputText,
    content: outputText,

    image_url: safeText(raw?.image_url),
    asset_url: safeText(raw?.asset_url),
    preview_url: safeText(raw?.preview_url),

    media_pack: mediaPack,
    generation_jobs: generationJobs,

    voiceover_script: safeText(raw?.voiceover_script),
    video_prompt: safeText(raw?.video_prompt),
    avatar_prompt: safeText(raw?.avatar_prompt),

    supports_audio: Boolean(raw?.supports_audio),
    supports_video: Boolean(raw?.supports_video),
    supports_avatar_video: Boolean(raw?.supports_avatar_video),

    tags,
    created_at: firstString(raw?.created_at, latest?.created_at, latest?.created_at_iso),
  };
}

function flattenExecution(latest: any) {
  if (!latest || typeof latest !== "object") return null;

  return {
    id: safeText(latest?.id || latest?.execution_id || ""),
    status: safeText(latest?.status || latest?.execution_status || "completed"),
    task: safeText(latest?.task || latest?.workflow?.task || ""),
    created_at: firstString(latest?.created_at, latest?.created_at_iso),
    tenant_id: safeText(latest?.tenant_id || latest?.workflow?.tenant_id || ""),
    requested_agent: safeText(latest?.requested_agent || latest?.workflow?.requested_agent || ""),
    deliverable: flattenDeliverable(latest),
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

    const execution = flattenExecution(latest);
    const deliverable = execution?.deliverable || null;

    return NextResponse.json({
      success: true,
      source: "backend_runtime_fully_flattened",
      execution,
      deliverable,
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: "client_latest_deliverable_proxy_failed",
      detail: String(error),
      execution: null,
      deliverable: null,
    });
  }
}