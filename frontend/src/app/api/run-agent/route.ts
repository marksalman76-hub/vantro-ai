import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://api.trance-formation.com.au";

const BACKEND_AUTH_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  process.env.ADMIN_AUTH_TOKEN ||
  process.env.BACKEND_AUTH_TOKEN ||
  "";

const AGENT_WORKFLOW_STAGE_MAP: Record<string, string> = {
  head_agent: "head_agent_review",
  strategist_agent: "strategic_planning",
  business_growth_partnerships_agent: "business_growth",
  lead_generator_appointment_setter_agent: "sales_follow_up",
  marketing_specialist_agent: "marketing_campaign",
  social_media_manager_content_creator_agent: "content_generation",
  seo_agent: "seo_strategy",
  email_reply_agent: "content_generation",
  crm_ai_agent: "crm_optimisation",
  sales_closer_agent: "sales_follow_up",
  receptionist_agent: "reception_intake",
  customer_support_agent: "customer_support",
  ecommerce_agent: "store_optimisation",
  product_research_agent: "product_research",
  competitor_intelligence_agent: "competitor_analysis",
  brand_strategy_agent: "brand_strategy",
  store_builder_agent: "store_optimisation",
  website_landing_apps_agent: "website_landing_page",
  product_development_agent: "product_development",
  product_copywriting_agent: "product_copywriting",
  ugc_creative_agent: "ugc_creative",
  product_image_agent: "product_image_direction",
  paid_ads_agent: "paid_ads_strategy",
  analytics_optimisation_agent: "analytics_optimisation",
  influencer_collaboration_agent: "influencer_outreach",
  orchestration_agent: "orchestration_review",
  operations_manager_agent: "store_optimisation",
};

const AGENT_ACTION_TYPE_MAP: Record<string, string> = {
  head_agent: "analysis_generation",
  strategist_agent: "strategy_generation",
  business_growth_partnerships_agent: "strategy_generation",
  lead_generator_appointment_setter_agent: "sales_follow_up_generation",
  marketing_specialist_agent: "marketing_campaign_execution",
  social_media_manager_content_creator_agent: "content_generation",
  seo_agent: "seo_plan_generation",
  email_reply_agent: "draft_generation",
  crm_ai_agent: "crm_recommendation",
  sales_closer_agent: "sales_follow_up_generation",
  receptionist_agent: "support_response_generation",
  customer_support_agent: "support_response_generation",
  ecommerce_agent: "analysis_generation",
  product_research_agent: "analysis_generation",
  competitor_intelligence_agent: "analysis_generation",
  brand_strategy_agent: "strategy_generation",
  store_builder_agent: "website_brief_generation",
  website_landing_apps_agent: "website_brief_generation",
  product_development_agent: "product_brief_generation",
  product_copywriting_agent: "content_generation",
  ugc_creative_agent: "creative_brief_generation",
  product_image_agent: "create_product_image_brief",
  paid_ads_agent: "create_ad_copy_brief",
  analytics_optimisation_agent: "analytics_report_generation",
  influencer_collaboration_agent: "influencer_outreach_generation",
  orchestration_agent: "analysis_generation",
  operations_manager_agent: "analysis_generation",
};

function getDefaultWorkflowStage(agentId: string) {
  return AGENT_WORKFLOW_STAGE_MAP[agentId] || "content_generation";
}

function getDefaultActionType(agentId: string) {
  return AGENT_ACTION_TYPE_MAP[agentId] || "analysis_generation";
}



export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const selectedAgents = Array.isArray(body?.selected_agents)
      ? body.selected_agents
      : [];

    const primaryAgent =
      String(body?.agent_id || body?.agentId || selectedAgents[0] || "").trim();

    const task = String(body?.task || body?.prompt || "Run live agent execution").trim();

    if (!primaryAgent && selectedAgents.length === 0) {
      return NextResponse.json(
        { success: false, error: "missing_agent_selection" },
        { status: 400 }
      );
    }

    const tenantId =
      request.headers.get("x-tenant-id") ||
      request.cookies.get("tenant_id")?.value ||
      body?.tenant_id ||
      "client_demo_001";

    const backendPayload = {
      ...body,
      tenant_id: body?.tenant_id || tenantId,
      agent_id: primaryAgent || selectedAgents[0],
      requested_agent: body?.requested_agent || primaryAgent || selectedAgents[0],
      selected_agents: selectedAgents.length > 0 ? selectedAgents : [primaryAgent],
      workflow_stage: body?.workflow_stage || getDefaultWorkflowStage(primaryAgent || selectedAgents[0]),
      action_type: body?.action_type || getDefaultActionType(primaryAgent || selectedAgents[0]),
      task,
      prompt: body?.prompt || task,
      source: "client_workspace",
      execution_surface: "client_page",
    };

    const actorRole =
      request.headers.get("x-actor-role") ||
      body?.actor_role ||
      "customer";

    const response = await fetch(`${BACKEND_URL.replace(/\/$/, "")}/run-agent`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-tenant-id": String(tenantId),
        "x-actor-role": String(actorRole),
        ...(BACKEND_AUTH_TOKEN
          ? { Authorization: `Bearer ${BACKEND_AUTH_TOKEN}` }
          : {}),
      },
      body: JSON.stringify(backendPayload),
      cache: "no-store",
    });

    const text = await response.text();

    let data: any;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw_response: text };
    }

    return NextResponse.json(
      {
        success: response.ok,
        proxied_to_backend: true,
        backend_status: response.status,
        backend_url: "/run-agent",
        agent_id: backendPayload.agent_id,
        selected_agents: backendPayload.selected_agents,
        result: data,
        execution: data?.execution || data,
        deliverable: data?.deliverable || data?.execution?.deliverable || data?.result?.deliverable || null,
      },
      { status: response.ok ? 200 : response.status }
    );
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "backend_execution_proxy_failed",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}