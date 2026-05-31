from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FRONTEND = ROOT / "frontend"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

login_route_dir = FRONTEND / "src" / "app" / "api" / "client-login"
me_route_dir = FRONTEND / "src" / "app" / "api" / "client-me"

login_route_dir.mkdir(parents=True, exist_ok=True)
me_route_dir.mkdir(parents=True, exist_ok=True)

login_route = login_route_dir / "route.ts"
me_route = me_route_dir / "route.ts"

for file in [login_route, me_route]:
    if file.exists():
        backup = BACKUPS / f"{file.parent.name}_route_before_step267c_{timestamp}.ts"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup: {backup}")

login_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";

const DEMO_EMAIL = "demo@client.local";
const DEMO_PASSWORD = "Demo123!";

export async function POST(request: NextRequest) {
  const form = await request.formData();

  const email = String(form.get("email") || "").trim().toLowerCase();
  const password = String(form.get("password") || "");
  const nextPath = String(form.get("next") || "/client");

  if (email !== DEMO_EMAIL || password !== DEMO_PASSWORD) {
    return NextResponse.redirect(new URL(`/login?next=${encodeURIComponent(nextPath)}&error=invalid_login`, request.url));
  }

  const response = NextResponse.redirect(new URL(nextPath || "/client", request.url));

  response.cookies.set("client_demo_session", "active", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  response.cookies.set("client_session", "demo_client_session", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });

  return response;
}
''', encoding="utf-8")

me_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const demoSession = request.cookies.get("client_demo_session")?.value;
  const clientSession = request.cookies.get("client_session")?.value;

  if (demoSession !== "active" && clientSession !== "demo_client_session") {
    return NextResponse.json(
      { success: false, error: "not_authenticated" },
      { status: 401 }
    );
  }

  return NextResponse.json({
    success: true,
    account: {
      company_name: "Premium Demo Ecommerce Store",
      contact_name: "Demo Client",
      contact_email: "demo@client.local",
      package_name: "Premium Demo",
      package_status: "active",
      billing_status: "demo_active",
      credits_remaining: 500,
      credits_monthly: 500,
      active_agents: [
        "product_copywriting_agent",
        "ugc_creative_agent",
        "product_image_agent",
        "influencer_collaboration_agent",
        "analytics_optimisation_agent",
        "general_ecommerce_agent",
        "competitor_intelligence_agent"
      ],
      paid_agents: [
        "product_copywriting_agent",
        "ugc_creative_agent",
        "product_image_agent",
        "influencer_collaboration_agent",
        "analytics_optimisation_agent",
        "general_ecommerce_agent",
        "competitor_intelligence_agent"
      ]
    }
  });
}
''', encoding="utf-8")

print("STEP_267C_DEMO_CLIENT_LOGIN_INSTALLED")
print("Demo email: demo@client.local")
print("Demo password: Demo123!")
print("STEP_267C_OK")