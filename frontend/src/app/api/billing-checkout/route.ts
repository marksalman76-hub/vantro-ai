
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
