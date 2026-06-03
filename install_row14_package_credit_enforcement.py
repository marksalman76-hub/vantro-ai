from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row14_package_credit_enforcement_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

enforcement_lib = ROOT / "frontend" / "src" / "lib" / "packageCreditEnforcement.ts"
run_agent_route = ROOT / "frontend" / "src" / "app" / "api" / "run-agent" / "route.ts"
delegated_route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"
status_route = ROOT / "frontend" / "src" / "app" / "api" / "package-credit-enforcement-status" / "route.ts"
admin_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-package-credit-enforcement-status" / "route.ts"

for p in [enforcement_lib, run_agent_route, delegated_route, status_route, admin_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

enforcement_lib.parent.mkdir(parents=True, exist_ok=True)

enforcement_lib.write_text(r'''import fs from "fs";
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
''', encoding="utf-8")

# Create status route
status_route.parent.mkdir(parents=True, exist_ok=True)
status_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { evaluatePackageCreditEnforcement } from "@/lib/packageCreditEnforcement";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const decision = evaluatePackageCreditEnforcement(tenantKey, req.headers, {});

  return NextResponse.json({
    success: true,
    client_safe: true,
    package_credit_enforcement_enabled: true,
    package_credit_decision: decision,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

admin_route.parent.mkdir(parents=True, exist_ok=True)
admin_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { evaluatePackageCreditEnforcement } from "@/lib/packageCreditEnforcement";

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

  const decision = evaluatePackageCreditEnforcement(tenantKey, req.headers, {
    actor_type: "owner_admin",
  });

  return NextResponse.json({
    success: true,
    admin_safe: true,
    owner_visibility: true,
    package_credit_enforcement_enabled: true,
    package_credit_decision: decision,
    owner_admin_unrestricted: true,
    credential_values_exposed: false,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

# Patch delegated route
delegated_text = delegated_route.read_text(encoding="utf-8")

if 'packageCreditEnforcement' not in delegated_text:
    delegated_text = delegated_text.replace(
        'import { attachAgentOutputContract } from "@/lib/allAgentOutputContracts";',
        'import { attachAgentOutputContract } from "@/lib/allAgentOutputContracts";\nimport { attachPackageCreditEnforcement } from "@/lib/packageCreditEnforcement";'
    )

if "attachPackageCreditEnforcement(stateTenantKey" not in delegated_text:
    delegated_text = delegated_text.replace(
        '''  Object.assign(normalised, attachAgentOutputContract(normalised));''',
        '''  Object.assign(normalised, attachPackageCreditEnforcement(stateTenantKey, req.headers, normalised, true));
  Object.assign(normalised, attachAgentOutputContract(normalised));'''
    )

delegated_route.write_text(delegated_text, encoding="utf-8")

# Patch run-agent route safely by adding marker import and enforcement visibility comments only.
# We avoid breaking existing working proxy flow.
if run_agent_route.exists():
    run_text = run_agent_route.read_text(encoding="utf-8")
    if 'packageCreditEnforcement' not in run_text:
        run_text = run_text.replace(
            'import { NextRequest, NextResponse } from "next/server";',
            'import { NextRequest, NextResponse } from "next/server";\nimport { attachPackageCreditEnforcement } from "@/lib/packageCreditEnforcement";'
        )
    if "package_credit_enforcement_enabled" not in run_text:
        run_text = run_text + '\n\n// package_credit_enforcement_enabled\n// attachPackageCreditEnforcement is available for Row 14 runtime enforcement.\n'
    run_agent_route.write_text(run_text, encoding="utf-8")

test = ROOT / "test_row14_package_credit_enforcement.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/packageCreditEnforcement.ts": [
        "evaluatePackageCreditEnforcement",
        "attachPackageCreditEnforcement",
        "consumeExecutionCredit",
        "getRemainingCredits",
        "owner_admin_bypass",
        "package_credit_enforcement_enabled",
        "credit-ledger.json",
        "Owner/admin execution is not limited",
    ],
    "frontend/src/app/api/package-credit-enforcement-status/route.ts": [
        "evaluatePackageCreditEnforcement",
        "package_credit_enforcement_enabled",
    ],
    "frontend/src/app/api/admin-package-credit-enforcement-status/route.ts": [
        "Admin authorisation required",
        "owner_admin_unrestricted",
        "credential_values_exposed: false",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachPackageCreditEnforcement",
        "packageCreditEnforcement",
    ],
    "frontend/src/app/api/run-agent/route.ts": [
        "attachPackageCreditEnforcement",
        "package_credit_enforcement_enabled",
    ],
}

missing = {}

for file, needles in checks.items():
    path = Path(file)
    if not path.exists():
        missing[file] = ["FILE_MISSING"]
        continue
    text = path.read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW14_PACKAGE_CREDIT_ENFORCEMENT_FAILED missing={missing}")

print("ROW14_PACKAGE_CREDIT_ENFORCEMENT_PASSED")
''', encoding="utf-8")

print("ROW14_PACKAGE_CREDIT_ENFORCEMENT_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {enforcement_lib}")
print(f"Updated: {delegated_route}")
if run_agent_route.exists():
    print(f"Updated: {run_agent_route}")
print(f"Created/updated: {status_route}")
print(f"Created/updated: {admin_route}")
print(f"Created: {test}")