from pathlib import Path

ROOT = Path.cwd()

base = r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_URL || "https://api.trance-formation.com.au";

function adminHeaders(req: NextRequest): Record<string, string> {
  return {
    "Content-Type": "application/json",
    "x-actor-role": req.headers.get("x-actor-role") || "owner_admin",
    "x-admin-token": req.headers.get("x-admin-token") || process.env.ADMIN_TOKEN || "",
    "authorization": req.headers.get("authorization") || "",
  };
}
'''

def write(path: str, content: str):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"WROTE {path}")

write("frontend/src/app/api/admin-industry-agent-store-status/route.ts", base + r'''
export async function GET(req: NextRequest) {
  const upstream = await fetch(`${BACKEND_URL}/admin/industry-agent-store/status`, {
    method: "GET",
    cache: "no-store",
    headers: adminHeaders(req),
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
''')

write("frontend/src/app/api/admin-industry-agent-store-packs/route.ts", base + r'''
export async function GET(req: NextRequest) {
  const qs = new URLSearchParams();
  const industry = req.nextUrl.searchParams.get("industry");
  const limit = req.nextUrl.searchParams.get("limit") || "100";
  if (industry) qs.set("industry", industry);
  qs.set("limit", limit);

  const upstream = await fetch(`${BACKEND_URL}/admin/industry-agent-store/packs?${qs.toString()}`, {
    method: "GET",
    cache: "no-store",
    headers: adminHeaders(req),
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}

export async function POST(req: NextRequest) {
  const body = await req.text();
  const upstream = await fetch(`${BACKEND_URL}/admin/industry-agent-store/pack`, {
    method: "POST",
    cache: "no-store",
    headers: adminHeaders(req),
    body,
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
''')

write("frontend/src/app/api/admin-learning-vault-records/route.ts", base + r'''
export async function GET(req: NextRequest) {
  const qs = new URLSearchParams();
  const industry = req.nextUrl.searchParams.get("industry");
  const agentId = req.nextUrl.searchParams.get("agent_id");
  const limit = req.nextUrl.searchParams.get("limit") || "100";
  if (industry) qs.set("industry", industry);
  if (agentId) qs.set("agent_id", agentId);
  qs.set("limit", limit);

  const upstream = await fetch(`${BACKEND_URL}/admin/learning-vault/records?${qs.toString()}`, {
    method: "GET",
    cache: "no-store",
    headers: adminHeaders(req),
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
''')

write("frontend/src/app/api/admin-learning-vault-capture/route.ts", base + r'''
export async function POST(req: NextRequest) {
  const body = await req.text();
  const upstream = await fetch(`${BACKEND_URL}/admin/learning-vault/capture`, {
    method: "POST",
    cache: "no-store",
    headers: adminHeaders(req),
    body,
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
''')

print("ADMIN_INDUSTRY_STORE_FRONTEND_PROXIES_INSTALLED")