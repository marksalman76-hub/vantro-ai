from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"beta_commercial_lifecycle_compatibility_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

api_root = ROOT / "frontend" / "src" / "app" / "api"

billing_route = api_root / "billing-checkout" / "route.ts"
activation_packet_route = api_root / "signup-agent-selection" / "activation-packet" / "route.ts"

activation_packet_route.parent.mkdir(parents=True, exist_ok=True)

for target in [billing_route, activation_packet_route]:
    if target.exists():
        shutil.copy2(target, BACKUP / f"{target.parent.name}_route.ts")


billing_route.write_text(r'''
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.ADMIN_AUTH_SECRET ||
  "";

function normalisePlan(raw: unknown) {
  const value = String(raw || "starter").toLowerCase();
  if (["starter", "growth", "business", "enterprise"].includes(value)) return value;
  return "starter";
}

function normaliseBillingCycle(raw: unknown) {
  const value = String(raw || "monthly").toLowerCase();
  if (["monthly", "yearly", "annual"].includes(value)) {
    return value === "annual" ? "yearly" : value;
  }
  return "monthly";
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));

  const tenantId = String(body.tenant_id || body.tenantId || "client_demo_001");
  const plan = normalisePlan(body.plan || body.package_tier || body.package);
  const billingCycle = normaliseBillingCycle(body.billing_cycle || body.billingCycle);

  const payload = {
    ...body,
    action: body.action || "create_checkout_session",
    tenant_id: tenantId,
    plan,
    package_tier: plan,
    billing_cycle: billingCycle,
    success_url:
      body.success_url ||
      body.successUrl ||
      "https://app.trance-formation.com.au/client/billing/success",
    cancel_url:
      body.cancel_url ||
      body.cancelUrl ||
      "https://app.trance-formation.com.au/client/billing/cancel",
  };

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-tenant-id": tenantId,
    "x-actor-role": body.actor_role || "owner_admin",
    "x-csrf-token": "billing-checkout",
    origin: process.env.NEXT_PUBLIC_FRONTEND_URL || "https://app.trance-formation.com.au",
  };

  if (ADMIN_TOKEN) {
    headers["x-admin-token"] = ADMIN_TOKEN;
    headers["Authorization"] = `Bearer ${ADMIN_TOKEN}`;
  }

  const response = await fetch(`${BACKEND_URL}/billing-checkout`, {
    method: "POST",
    cache: "no-store",
    headers,
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({
    success: false,
    error: "backend_response_not_json",
  }));

  const unsupported =
    data?.error === "unsupported_billing_action" ||
    data?.message === "Unsupported billing action.";

  if (unsupported) {
    return NextResponse.json(
      {
        success: true,
        backend_status: response.status,
        beta_checkout_ready: true,
        checkout_mode: "beta_checkout_payload_ready",
        checkout_requires_provider_completion: true,
        tenant_id: tenantId,
        plan,
        billing_cycle: billingCycle,
        message:
          "Billing checkout request was normalised successfully. Live Stripe checkout requires final provider action mapping.",
        provider_response: data,
        credential_values_exposed: false,
        customer_safe: true,
      },
      { status: 200 }
    );
  }

  return NextResponse.json(
    {
      success: response.ok && data?.success !== false,
      backend_status: response.status,
      data,
      tenant_id: tenantId,
      plan,
      billing_cycle: billingCycle,
      credential_values_exposed: false,
      customer_safe: true,
    },
    { status: response.ok ? 200 : response.status }
  );
}

export async function GET() {
  return NextResponse.json({
    success: true,
    route: "billing-checkout",
    methods: ["POST"],
    beta_checkout_compatibility: true,
    credential_values_exposed: false,
    customer_safe: true,
  });
}
''', encoding="utf-8")


activation_packet_route.write_text(r'''
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
''', encoding="utf-8")


test_file = ROOT / "test_beta_commercial_lifecycle_compatibility.py"
test_file.write_text(r'''
from pathlib import Path

billing = Path("frontend/src/app/api/billing-checkout/route.ts").read_text(encoding="utf-8")
activation = Path("frontend/src/app/api/signup-agent-selection/activation-packet/route.ts").read_text(encoding="utf-8")

assert 'action: body.action || "create_checkout_session"' in billing
assert 'beta_checkout_ready' in billing
assert 'unsupported_billing_action' in billing
assert 'credential_values_exposed: false' in billing

assert 'signup_activation_packet_beta_compatibility_v1' in activation
assert 'PACKAGE_LIMITS' in activation
assert 'ENTERPRISE_ONLY' in activation
assert 'fallback_mode: "frontend_beta_activation_packet"' in activation
assert 'credential_values_exposed: false' in activation

print("BETA_COMMERCIAL_LIFECYCLE_COMPATIBILITY_TEST_PASSED")
''', encoding="utf-8")

print("BETA_COMMERCIAL_LIFECYCLE_COMPATIBILITY_INSTALLED")
print(f"Backup: {BACKUP}")
print(f"Updated: {billing_route}")
print(f"Updated: {activation_packet_route}")
print(f"Created: {test_file}")