import fs from "fs";
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


// durable_runtime_storage_enabled
// This module participates in the shared .runtime durable storage layer.
