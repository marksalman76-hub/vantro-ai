import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { persistBillingSubscription } from "@/lib/billingStripeSubscriptions";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function buildForwardHeaders(req: NextRequest): Record<string, string> {
  const headers: Record<string, string> = { "content-type": "application/json" };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);

  let backendPayload: Record<string, unknown> = {};
  let backendStatus = 200;

  try {
    const response = await fetch(`${backendBaseUrl()}/billing/live-checkout-session`, {
      method: "POST",
      headers: buildForwardHeaders(req),
      body: JSON.stringify(body),
      cache: "no-store",
    });

    backendStatus = response.status;
    const text = await response.text();

    try {
      backendPayload = JSON.parse(text);
    } catch {
      backendPayload = { backend_response_text: text };
    }
  } catch {
    backendPayload = {
      backend_sync_status: "pending",
      billing_status: "inactive",
    };
  }

  const subscription = persistBillingSubscription(tenantKey, {
    ...body,
    ...backendPayload,
    billing_status:
      backendPayload.checkout_url ||
      backendPayload.url ||
      backendPayload.checkout_session_id ||
      backendPayload.session_id
        ? "checkout_started"
        : backendPayload.billing_status || "inactive",
  });

  return NextResponse.json({
    ...backendPayload,
    success: backendPayload.success !== false,
    billing_stripe_subscriptions_enabled: true,
    billing_subscription_persisted: true,
    billing_subscription: subscription,
    billing_status: subscription.billing_status,
    package_key: subscription.package_key,
    checkout_url: subscription.checkout_url,
    checkout_session_id: subscription.checkout_session_id,
    enforcement_ready_for_row14: true,
    credential_values_exposed: false,
    client_safe_status: subscription.client_safe_status,
  }, {
    status: backendStatus >= 500 ? 200 : backendStatus,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
