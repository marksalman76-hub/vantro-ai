from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "api" / "billing-checkout" / "route.ts"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"billing_checkout_route_before_customer_fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"
shutil.copy2(TARGET, backup)

TARGET.write_text(r'''import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function safeString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

async function getClientAccount(request: NextRequest) {
  try {
    const response = await fetch(new URL("/api/client-me", request.url), {
      method: "GET",
      cache: "no-store",
      headers: { cookie: request.headers.get("cookie") || "" },
    });
    const data = await response.json().catch(() => null);
    return data?.account || data || null;
  } catch {
    return null;
  }
}

function findStripeCustomerId(body: any, account: any): string {
  return (
    safeString(body?.stripe_customer_id) ||
    safeString(body?.customer_id) ||
    safeString(account?.stripe_customer_id) ||
    safeString(account?.stripeCustomerId) ||
    safeString(account?.billing_customer_id) ||
    safeString(account?.customer_id) ||
    safeString(account?.subscription?.customer) ||
    ""
  );
}

function findCustomerEmail(body: any, account: any): string {
  return (
    safeString(body?.email) ||
    safeString(body?.customer_email) ||
    safeString(account?.email) ||
    safeString(account?.contact_email) ||
    ""
  );
}

async function createStripeCustomer(stripeSecret: string, body: any, account: any): Promise<string> {
  const form = new URLSearchParams();
  const email = findCustomerEmail(body, account);
  const name =
    safeString(body?.name) ||
    safeString(account?.company_name) ||
    safeString(account?.business_name) ||
    safeString(account?.client_name) ||
    "Client";

  if (email) form.set("email", email);
  form.set("name", name);
  form.set("metadata[source]", "client_payment_update_fallback");
  form.set("metadata[tenant_id]", safeString(account?.tenant_id || account?.client_id || body?.tenant_id || "unknown_client"));

  const response = await fetch("https://api.stripe.com/v1/customers", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${stripeSecret}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || !data?.id) return "";
  return data.id;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const mode = safeString(body?.mode || body?.checkout_type);
    const stripeSecret = safeString(process.env.STRIPE_SECRET_KEY);

    if (!stripeSecret) {
      return NextResponse.json({
        success: false,
        error: "stripe_not_configured",
        message: "Secure payment update is not connected yet.",
      });
    }

    const account = await getClientAccount(request);
    const returnUrl = safeString(body?.return_url) || `${new URL(request.url).origin}/client`;

    if (mode === "payment_update" || mode === "billing_portal" || mode === "portal") {
      let customerId = findStripeCustomerId(body, account);

      if (!customerId) {
        customerId = await createStripeCustomer(stripeSecret, body, account);
      }

      if (!customerId) {
        return NextResponse.json({
          success: false,
          error: "stripe_customer_create_failed",
          message: "Could not create or locate the secure billing customer record.",
        });
      }

      const form = new URLSearchParams();
      form.set("customer", customerId);
      form.set("return_url", returnUrl);

      const stripeResponse = await fetch("https://api.stripe.com/v1/billing_portal/sessions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${stripeSecret}`,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: form,
      });

      const stripeData = await stripeResponse.json().catch(() => ({}));

      if (!stripeResponse.ok || !stripeData?.url) {
        return NextResponse.json({
          success: false,
          error: "stripe_portal_session_failed",
          message: stripeData?.error?.message || "Could not open secure payment update.",
        });
      }

      return NextResponse.json({
        success: true,
        url: stripeData.url,
        portal_url: stripeData.url,
        stripe_customer_id: customerId,
      });
    }

    return NextResponse.json({
      success: false,
      error: "unsupported_billing_action",
      message: "Unsupported billing action.",
    });
  } catch {
    return NextResponse.json({
      success: false,
      error: "billing_checkout_route_failed",
      message: "Billing action could not be started.",
    });
  }
}
''', encoding="utf-8")

print("PAYMENT_UPDATE_CUSTOMER_FALLBACK_FIXED")
print(f"Backup: {backup}")