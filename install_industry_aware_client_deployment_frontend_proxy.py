from pathlib import Path

ROOT = Path.cwd()

base = r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.BACKEND_URL || "https://api.trance-formation.com.au";
'''

def write(path: str, content: str):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"WROTE {path}")

write("frontend/src/app/api/client-industry-aware-deployment-status/route.ts", base + r'''
export async function GET() {
  const upstream = await fetch(`${BACKEND_URL}/client/industry-aware-deployment/status`, {
    method: "GET",
    cache: "no-store",
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
''')

write("frontend/src/app/api/client-industry-aware-deployment-resolve/route.ts", base + r'''
export async function POST(req: NextRequest) {
  const body = await req.text();
  const upstream = await fetch(`${BACKEND_URL}/client/industry-aware-deployment/resolve`, {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body,
  });
  const text = await upstream.text();
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
  });
}
''')

print("INDUSTRY_AWARE_CLIENT_DEPLOYMENT_FRONTEND_PROXY_INSTALLED")