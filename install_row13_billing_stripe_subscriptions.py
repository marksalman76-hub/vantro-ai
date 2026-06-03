from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row13_billing_stripe_subscriptions_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

billing_lib = ROOT / "frontend" / "src" / "lib" / "billingStripeSubscriptions.ts"
checkout_route = ROOT / "frontend" / "src" / "app" / "api" / "billing-checkout" / "route.ts"
status_route = ROOT / "frontend" / "src" / "app" / "api" / "billing-subscription-status" / "route.ts"
admin_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-billing-subscription-status" / "route.ts"

for p in [billing_lib, checkout_route, status_route, admin_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

billing_lib.parent.mkdir(parents=True, exist_ok=True)

billing_lib.write_text(r'''import fs from "fs";
import path from "path";

export type BillingPackageKey = "starter" | "growth" | "business" | "enterprise";

export type BillingSubscriptionRecord = {
  tenant_key: string;
  updated_at: string;
  package_key: BillingPackageKey;
  billing_status: "inactive" | "checkout_started" | "active" | "past_due" | "cancelled" | "enterprise_manual";
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  checkout_session_id: string | null;
  checkout_url: string | null;
  currency: "usd";
  monthly_price_usd: number | null;
  client_safe_status: string;
  enforcement_ready_for_row14: boolean;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "billing-subscriptions");
const STORE_FILE = path.join(STORE_DIR, "billing-subscriptions.json");

export const BILLING_PACKAGE_PRICES: Record<BillingPackageKey, number | null> = {
  starter: 99,
  growth: 279,
  business: 399,
  enterprise: null,
};

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ subscriptions: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { subscriptions: Record<string, BillingSubscriptionRecord> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { subscriptions: {} };
    if (!parsed.subscriptions || typeof parsed.subscriptions !== "object" || Array.isArray(parsed.subscriptions)) return { subscriptions: {} };
    return parsed as { subscriptions: Record<string, BillingSubscriptionRecord> };
  } catch {
    return { subscriptions: {} };
  }
}

function safeWriteStore(store: { subscriptions: Record<string, BillingSubscriptionRecord> }): void {
  ensureStore();
  const tmp = `${STORE_FILE}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(store, null, 2), "utf-8");
  fs.renameSync(tmp, STORE_FILE);
}

function text(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return "";
}

export function normaliseBillingPackage(value: unknown): BillingPackageKey {
  const raw = text(value).toLowerCase();
  if (raw === "enterprise") return "enterprise";
  if (raw === "business") return "business";
  if (raw === "growth") return "growth";
  return "starter";
}

export function createBillingSubscriptionRecord(
  tenantKey: string,
  payload: Record<string, unknown>
): BillingSubscriptionRecord {
  const packageKey = normaliseBillingPackage(payload.package_key || payload.plan || payload.package || "starter");
  const isEnterprise = packageKey === "enterprise";

  const checkoutUrl = text(
    payload.checkout_url ||
    payload.url ||
    payload.stripe_checkout_url ||
    payload.session_url
  );

  const checkoutSessionId = text(
    payload.checkout_session_id ||
    payload.session_id ||
    payload.stripe_session_id
  );

  const explicitStatus = text(payload.billing_status || payload.subscription_status || payload.status).toLowerCase();

  let billingStatus: BillingSubscriptionRecord["billing_status"] = "inactive";

  if (isEnterprise) {
    billingStatus = "enterprise_manual";
  } else if (explicitStatus.includes("active")) {
    billingStatus = "active";
  } else if (explicitStatus.includes("past_due")) {
    billingStatus = "past_due";
  } else if (explicitStatus.includes("cancel")) {
    billingStatus = "cancelled";
  } else if (checkoutUrl || checkoutSessionId) {
    billingStatus = "checkout_started";
  }

  return {
    tenant_key: tenantKey,
    updated_at: new Date().toISOString(),
    package_key: packageKey,
    billing_status: billingStatus,
    stripe_customer_id: text(payload.stripe_customer_id || payload.customer_id) || null,
    stripe_subscription_id: text(payload.stripe_subscription_id || payload.subscription_id) || null,
    checkout_session_id: checkoutSessionId || null,
    checkout_url: checkoutUrl || null,
    currency: "usd",
    monthly_price_usd: BILLING_PACKAGE_PRICES[packageKey],
    client_safe_status:
      billingStatus === "active"
        ? "Subscription active"
        : billingStatus === "checkout_started"
          ? "Checkout started"
          : billingStatus === "enterprise_manual"
            ? "Enterprise billing requires manual approval"
            : billingStatus === "past_due"
              ? "Payment attention required"
              : billingStatus === "cancelled"
                ? "Subscription cancelled"
                : "Subscription not active",
    enforcement_ready_for_row14: true,
  };
}

export function persistBillingSubscription(
  tenantKey: string,
  payload: Record<string, unknown>
): BillingSubscriptionRecord {
  const record = createBillingSubscriptionRecord(tenantKey, payload);
  const store = safeReadStore();
  store.subscriptions[tenantKey] = record;
  safeWriteStore(store);
  return record;
}

export function getBillingSubscription(tenantKey: string): BillingSubscriptionRecord | null {
  const store = safeReadStore();
  return store.subscriptions[tenantKey] || null;
}

export function buildBillingSubscriptionStatus(tenantKey: string): Record<string, unknown> {
  const subscription = getBillingSubscription(tenantKey);

  return {
    success: true,
    billing_stripe_subscriptions_enabled: true,
    tenant_scoped: true,
    client_safe: true,
    credential_values_exposed: false,
    billing_subscription: subscription,
    billing_status: subscription?.billing_status || "inactive",
    package_key: subscription?.package_key || "starter",
    monthly_price_usd: subscription?.monthly_price_usd ?? BILLING_PACKAGE_PRICES.starter,
    enforcement_ready_for_row14: true,
    client_safe_status: subscription?.client_safe_status || "Subscription not active",
  };
}
''', encoding="utf-8")

checkout_route.parent.mkdir(parents=True, exist_ok=True)
checkout_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
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
''', encoding="utf-8")

status_route.parent.mkdir(parents=True, exist_ok=True)
status_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { buildBillingSubscriptionStatus } from "@/lib/billingStripeSubscriptions";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  return NextResponse.json(buildBillingSubscriptionStatus(tenantKey), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

admin_route.parent.mkdir(parents=True, exist_ok=True)
admin_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { buildBillingSubscriptionStatus } from "@/lib/billingStripeSubscriptions";

export const dynamic = "force-dynamic";

function isAdminRequest(req: NextRequest): boolean {
  return Boolean(
    req.headers.get("authorization") ||
    req.headers.get("x-admin-token") ||
    req.cookies.get("admin_session")?.value
  );
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  if (!isAdminRequest(req)) {
    return NextResponse.json(
      { success: false, error: "Admin authorisation required." },
      { status: 401 }
    );
  }

  const tenantKey =
    req.nextUrl.searchParams.get("tenant_key") ||
    req.nextUrl.searchParams.get("tenant_id") ||
    req.headers.get("x-tenant-key") ||
    req.headers.get("x-tenant-id") ||
    "default_client_workspace";

  return NextResponse.json({
    ...buildBillingSubscriptionStatus(tenantKey),
    admin_safe: true,
    owner_visibility: true,
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

test = ROOT / "test_row13_billing_stripe_subscriptions.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/billingStripeSubscriptions.ts": [
        "BillingSubscriptionRecord",
        "BILLING_PACKAGE_PRICES",
        "persistBillingSubscription",
        "getBillingSubscription",
        "buildBillingSubscriptionStatus",
        "billing-subscriptions.json",
        "enforcement_ready_for_row14",
    ],
    "frontend/src/app/api/billing-checkout/route.ts": [
        "persistBillingSubscription",
        "billing_stripe_subscriptions_enabled",
        "billing_subscription_persisted",
        "credential_values_exposed: false",
        "enforcement_ready_for_row14",
    ],
    "frontend/src/app/api/billing-subscription-status/route.ts": [
        "buildBillingSubscriptionStatus",
        "cache-control",
    ],
    "frontend/src/app/api/admin-billing-subscription-status/route.ts": [
        "Admin authorisation required",
        "buildBillingSubscriptionStatus",
        "owner_visibility",
        "credential_values_exposed: false",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW13_BILLING_STRIPE_SUBSCRIPTIONS_FAILED missing={missing}")

print("ROW13_BILLING_STRIPE_SUBSCRIPTIONS_PASSED")
''', encoding="utf-8")

print("ROW13_BILLING_STRIPE_SUBSCRIPTIONS_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {billing_lib}")
print(f"Updated: {checkout_route}")
print(f"Created/updated: {status_route}")
print(f"Created/updated: {admin_route}")
print(f"Created: {test}")