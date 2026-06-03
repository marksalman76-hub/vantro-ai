import fs from "fs";
import path from "path";
import { getBillingSubscription } from "@/lib/billingStripeSubscriptions";
import { getCatalogueForPackage } from "@/lib/agentCatalogueProductionUx";

export type PackageCreditDecision = {
  success: boolean;
  package_credit_enforcement_enabled: true;
  owner_admin_bypass: boolean;
  tenant_key: string;
  package_key: string;
  billing_status: string;
  requested_agent: string;
  agent_allowed: boolean;
  credits_allowed: boolean;
  execution_allowed: boolean;
  remaining_credits: number | null;
  client_safe_status: string;
  enforcement_reason: string;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "package-credit-enforcement");
const STORE_FILE = path.join(STORE_DIR, "credit-ledger.json");

const DEFAULT_PACKAGE_CREDITS: Record<string, number> = {
  starter: 100,
  growth: 350,
  business: 750,
  enterprise: 999999,
};

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ credits: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { credits: Record<string, number> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { credits: {} };
    if (!parsed.credits || typeof parsed.credits !== "object" || Array.isArray(parsed.credits)) return { credits: {} };
    return parsed as { credits: Record<string, number> };
  } catch {
    return { credits: {} };
  }
}

function safeWriteStore(store: { credits: Record<string, number> }): void {
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

export function isOwnerAdminRequest(headers: Headers, payload: Record<string, unknown> = {}): boolean {
  return Boolean(
    headers.get("authorization") ||
    headers.get("x-admin-token") ||
    text(payload.owner_admin) === "true" ||
    text(payload.actor_type).toLowerCase() === "owner_admin"
  );
}

export function getRemainingCredits(tenantKey: string, packageKey: string): number {
  const store = safeReadStore();

  if (typeof store.credits[tenantKey] !== "number") {
    store.credits[tenantKey] = DEFAULT_PACKAGE_CREDITS[packageKey] ?? DEFAULT_PACKAGE_CREDITS.starter;
    safeWriteStore(store);
  }

  return store.credits[tenantKey];
}

export function consumeExecutionCredit(tenantKey: string, packageKey: string, amount = 1): number {
  const store = safeReadStore();

  if (typeof store.credits[tenantKey] !== "number") {
    store.credits[tenantKey] = DEFAULT_PACKAGE_CREDITS[packageKey] ?? DEFAULT_PACKAGE_CREDITS.starter;
  }

  store.credits[tenantKey] = Math.max(0, store.credits[tenantKey] - amount);
  safeWriteStore(store);
  return store.credits[tenantKey];
}

export function evaluatePackageCreditEnforcement(
  tenantKey: string,
  headers: Headers,
  payload: Record<string, unknown> = {}
): PackageCreditDecision {
  const ownerAdminBypass = isOwnerAdminRequest(headers, payload);
  const subscription = getBillingSubscription(tenantKey);
  const packageKey = text(payload.package_key || subscription?.package_key || "starter").toLowerCase();
  const billingStatus = text(subscription?.billing_status || payload.billing_status || "inactive").toLowerCase();
  const requestedAgent = text(
    payload.agent_key ||
    payload.agent ||
    payload.selected_agent ||
    payload.assigned_agent ||
    "unknown_agent"
  );

  if (ownerAdminBypass) {
    return {
      success: true,
      package_credit_enforcement_enabled: true,
      owner_admin_bypass: true,
      tenant_key: tenantKey,
      package_key: packageKey,
      billing_status: billingStatus,
      requested_agent: requestedAgent,
      agent_allowed: true,
      credits_allowed: true,
      execution_allowed: true,
      remaining_credits: null,
      client_safe_status: "Owner/admin execution unrestricted",
      enforcement_reason:
        "Owner/admin execution is not limited by client credits, package limits, selected-agent caps, business count, business type, or subscription state.",
    };
  }

  const catalogue = getCatalogueForPackage(packageKey);
  const allowedAgents = new Set(catalogue.agents.filter((agent) => agent.selectable).map((agent) => agent.agent_key));
  const agentAllowed = requestedAgent === "unknown_agent" || allowedAgents.has(requestedAgent);
  const remainingCredits = getRemainingCredits(tenantKey, packageKey);

  const billingAllowed =
    billingStatus === "active" ||
    billingStatus === "checkout_started" ||
    billingStatus === "enterprise_manual";

  const creditsAllowed = remainingCredits > 0;
  const executionAllowed = billingAllowed && agentAllowed && creditsAllowed;

  let clientSafeStatus = "Execution allowed";
  let reason = "Package, billing, agent, and credit checks passed.";

  if (!billingAllowed) {
    clientSafeStatus = "Subscription required";
    reason = "Client subscription is not active yet.";
  } else if (!agentAllowed) {
    clientSafeStatus = "Agent not included in package";
    reason = "Requested agent is not available for this package.";
  } else if (!creditsAllowed) {
    clientSafeStatus = "Credits exhausted";
    reason = "Client credit allocation has been exhausted.";
  }

  return {
    success: executionAllowed,
    package_credit_enforcement_enabled: true,
    owner_admin_bypass: false,
    tenant_key: tenantKey,
    package_key: packageKey,
    billing_status: billingStatus,
    requested_agent: requestedAgent,
    agent_allowed: agentAllowed,
    credits_allowed: creditsAllowed,
    execution_allowed: executionAllowed,
    remaining_credits: remainingCredits,
    client_safe_status: clientSafeStatus,
    enforcement_reason: reason,
  };
}

export function attachPackageCreditEnforcement(
  tenantKey: string,
  headers: Headers,
  payload: Record<string, unknown> = {},
  consumeCredit = false
): Record<string, unknown> {
  const decision = evaluatePackageCreditEnforcement(tenantKey, headers, payload);

  let remainingCredits = decision.remaining_credits;

  if (consumeCredit && decision.execution_allowed && !decision.owner_admin_bypass) {
    remainingCredits = consumeExecutionCredit(tenantKey, decision.package_key, 1);
  }

  return {
    ...payload,
    package_credit_enforcement_enabled: true,
    package_credit_decision: {
      ...decision,
      remaining_credits: remainingCredits,
    },
    package_key: decision.package_key,
    billing_status: decision.billing_status,
    execution_allowed: decision.execution_allowed,
    owner_admin_bypass: decision.owner_admin_bypass,
    remaining_credits: remainingCredits,
    client_safe_status: decision.client_safe_status,
    enforcement_reason: decision.enforcement_reason,
  };
}


// durable_runtime_storage_enabled
// This module participates in the shared .runtime durable storage layer.
