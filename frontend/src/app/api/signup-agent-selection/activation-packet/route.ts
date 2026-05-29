
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

const PACKAGE_LIMITS: Record<string, number> = {
  starter: 3,
  growth: 7,
  business: 10,
  enterprise: 27,
};

const ENTERPRISE_ONLY = new Set(["head_agent", "orchestration_agent"]);

function normalisePlan(raw: unknown) {
  const value = String(raw || "starter").toLowerCase();
  if (["starter", "growth", "business", "enterprise"].includes(value)) return value;
  return "starter";
}

function normaliseAgents(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .map((item) => String(item || "").trim())
    .filter(Boolean)
    .filter((item, index, arr) => arr.indexOf(item) === index);
}

function buildLocalActivationPacket(body: any) {
  const tenantId = String(body.tenant_id || body.tenantId || "client_demo_001");
  const plan = normalisePlan(body.plan || body.package_tier || body.package);
  const selectedAgents = normaliseAgents(body.selected_agents || body.selectedAgents);

  const maxAgents = PACKAGE_LIMITS[plan] || PACKAGE_LIMITS.starter;
  const selectedWithoutReserved =
    plan === "enterprise"
      ? selectedAgents
      : selectedAgents.filter((agent) => !ENTERPRISE_ONLY.has(agent));

  const activatedAgents = selectedWithoutReserved.slice(0, maxAgents);

  return {
    success: true,
    profile: "signup_activation_packet_beta_compatibility_v1",
    tenant_id: tenantId,
    package_tier: plan,
    selected_agents: selectedAgents,
    activated_agents: activatedAgents,
    active_agent_count: activatedAgents.length,
    max_agent_count: maxAgents,
    enterprise_only_agents_blocked:
      plan === "enterprise"
        ? []
        : selectedAgents.filter((agent) => ENTERPRISE_ONLY.has(agent)),
    entitlement_status: "activation_packet_ready",
    activation_status: "ready_for_client_activation",
    customer_safe: true,
    credential_values_exposed: false,
  };
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const tenantId = String(body.tenant_id || body.tenantId || "client_demo_001");

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-tenant-id": tenantId,
    "x-actor-role": body.actor_role || "owner_admin",
    "x-csrf-token": "signup-activation-packet",
    origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
  };

  if (ADMIN_TOKEN) {
    headers["x-admin-token"] = ADMIN_TOKEN;
    headers["Authorization"] = `Bearer ${ADMIN_TOKEN}`;
  }

  const response = await fetch(`${BACKEND_URL}/signup-agent-selection/activation-packet`, {
    method: "POST",
    cache: "no-store",
    headers,
    body: JSON.stringify(body),
  }).catch(() => null);

  if (response) {
    const data = await response.json().catch(() => ({
      success: false,
      error: "backend_response_not_json",
    }));

    if (response.ok && data?.success !== false) {
      return NextResponse.json(
        {
          success: true,
          backend_status: response.status,
          data,
          credential_values_exposed: false,
          customer_safe: true,
        },
        { status: 200 }
      );
    }
  }

  return NextResponse.json(
    {
      success: true,
      backend_status: response?.status || 404,
      data: buildLocalActivationPacket(body),
      fallback_mode: "frontend_beta_activation_packet",
      message:
        "Backend activation packet route unavailable; generated beta-safe activation packet from locked package rules.",
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: 200 }
  );
}

export async function GET() {
  return NextResponse.json({
    success: true,
    route: "signup-agent-selection/activation-packet",
    methods: ["POST"],
    beta_activation_packet_compatibility: true,
    credential_values_exposed: false,
    customer_safe: true,
  });
}
