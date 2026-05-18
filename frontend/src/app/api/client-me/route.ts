import { NextRequest, NextResponse } from "next/server";

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
