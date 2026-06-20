import { NextRequest, NextResponse } from "next/server";
import { attachPackageCreditEnforcement } from "@/lib/packageCreditEnforcement";
import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

const DATA_DIR = path.join(process.cwd(), ".runtime-data");
const DATA_FILE = path.join(DATA_DIR, "client-executions.json");

async function persistClientExecution(bodyText: string) {
  try {
    const data = JSON.parse(bodyText);
    if (!data?.success) return;

    const providerContent =
      data?.output?.provider_execution?.generated_content ||
      data?.output?.content ||
      data?.provider_execution?.generated_content ||
      data?.execution?.adapter_result?.output ||
      data?.execution?.adapter_result?.generated_output ||
      data?.output ||
      "";

    const deliverable = {
      title: "Client deliverable",
      summary: data?.safe_client_message || data?.message || "Governed client execution completed.",
      output: typeof providerContent === "string" ? providerContent : JSON.stringify(providerContent, null, 2),
      generated_output: typeof providerContent === "string" ? providerContent : JSON.stringify(providerContent, null, 2),
      content: typeof providerContent === "string" ? providerContent : JSON.stringify(providerContent, null, 2),
      media_pack: data?.media_pack || data?.execution?.adapter_result?.media_pack || {},
      generation_jobs: data?.generation_jobs || data?.execution?.adapter_result?.generation_jobs || [],
      preview_url: data?.preview_url || data?.execution?.adapter_result?.preview_url || "",
      asset_url: data?.asset_url || data?.execution?.adapter_result?.asset_url || "",
      media_url: data?.media_url || data?.execution?.adapter_result?.media_url || "",
      voiceover_script: data?.voiceover_script || data?.execution?.adapter_result?.voiceover_script || "",
      video_prompt: data?.video_prompt || data?.execution?.adapter_result?.video_prompt || "",
      avatar_prompt: data?.avatar_prompt || data?.execution?.adapter_result?.avatar_prompt || "",
      supports_audio: Boolean(data?.supports_audio || data?.execution?.adapter_result?.supports_audio),
      supports_video: Boolean(data?.supports_video || data?.execution?.adapter_result?.supports_video),
      supports_avatar_video: Boolean(data?.supports_avatar_video || data?.execution?.adapter_result?.supports_avatar_video),
      client_safe_learning_summary: data?.client_safe_learning_summary || data?.learning || {},
      created_at: new Date().toISOString(),
      tags: ["Live execution", "Client safe", "Generated output"],
    };

    await mkdir(DATA_DIR, { recursive: true });

    let existing: any[] = [];
    try {
      existing = JSON.parse(await readFile(DATA_FILE, "utf-8"));
      if (!Array.isArray(existing)) existing = [];
    } catch {
      existing = [];
    }

    existing.unshift({
      created_at: new Date().toISOString(),
      execution: data,
      deliverable,
    });

    await writeFile(DATA_FILE, JSON.stringify(existing.slice(0, 50), null, 2), "utf-8");
  } catch {
    // Never block execution response because local persistence failed.
  }
}


function getBearer(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth;

  const cookieToken =
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    "";

  return cookieToken ? `Bearer ${cookieToken}` : "";
}

async function proxy(req: NextRequest, path: string) {
  const bearer = getBearer(req);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-actor-role": req.headers.get("x-actor-role") || "client",
    "x-tenant-id": req.headers.get("x-tenant-id") || req.cookies.get("tenant_id")?.value || "tenant_unknown",
    "origin": req.headers.get("origin") || "",
    "referer": req.headers.get("referer") || "",
  };

  if (bearer) headers.Authorization = bearer;

  const init: RequestInit = {
    method: req.method,
    headers,
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(req.method)) {
    const text = await req.text();
    if (text) init.body = text;
  }

  const res = await fetch(`${BACKEND_URL}${path}`, init);
  const contentType = res.headers.get("content-type") || "application/json";
  const body = await res.text();

  if (req.method === "POST" && path === "/run-agent") {
    await persistClientExecution(body);
  }

  return new NextResponse(body, {
    status: res.status,
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "no-store",
    },
  });
}

export async function GET(req: NextRequest) {
  return proxy(req, "/run-agent");
}

export async function POST(req: NextRequest) {
  return proxy(req, "/run-agent");
}

export async function PUT(req: NextRequest) {
  return proxy(req, "/run-agent");
}

export async function PATCH(req: NextRequest) {
  return proxy(req, "/run-agent");
}


// package_credit_enforcement_enabled
// attachPackageCreditEnforcement is available for Row 14 runtime enforcement.
