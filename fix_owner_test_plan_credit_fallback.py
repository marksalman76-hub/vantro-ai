from pathlib import Path
import json
import re
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
COMPONENT = ROOT / "frontend" / "src" / "components" / "ClientPlanCreditStatusCard.tsx"
VERIFY = ROOT / "verify_client_plan_credit_status_card.py"

backup_dir = ROOT / "backups" / f"client_plan_credit_status_card_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(CLIENT_PAGE, backup_dir / "client_page.tsx")

COMPONENT.parent.mkdir(parents=True, exist_ok=True)

COMPONENT.write_text(r'''
"use client";

import { useEffect, useMemo, useState } from "react";

type ClientBillingState = {
  planName: string;
  planStatus: string;
  creditsAvailable: number | null;
  creditsUsed: number | null;
  creditsLimit: number | null;
  creditStatus: string;
  loading: boolean;
  error: string | null;
};

function readString(source: any, keys: string[], fallback = "Not available") {
  for (const key of keys) {
    const value = source?.[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }
  return fallback;
}

function readNumber(source: any, keys: string[]) {
  for (const key of keys) {
    const value = source?.[key];
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === "string" && value.trim() && !Number.isNaN(Number(value))) {
      return Number(value);
    }
  }
  return null;
}

async function readJsonSafely(url: string) {
  try {
    const response = await fetch(url, { cache: "no-store" });
    const body = await response.json().catch(() => ({}));
    return { ok: response.ok, body };
  } catch {
    return { ok: false, body: {} };
  }
}

export default function ClientPlanCreditStatusCard() {
  const [state, setState] = useState<ClientBillingState>({
    planName: "Loading",
    planStatus: "Checking",
    creditsAvailable: null,
    creditsUsed: null,
    creditsLimit: null,
    creditStatus: "Checking",
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function loadBillingAndCredits() {
      const [billing, credits] = await Promise.all([
        readJsonSafely("/api/billing-subscription-status"),
        readJsonSafely("/api/package-credit-enforcement-status"),
      ]);

      if (cancelled) {
        return;
      }

      const billingBody = billing.body || {};
      const creditBody = credits.body || {};

      const nestedBilling = billingBody.subscription || billingBody.billing || billingBody.data || billingBody;
      const nestedCredits = creditBody.credits || creditBody.package || creditBody.enforcement || creditBody.data || creditBody;

      const planName = readString(
        nestedBilling,
        ["plan_name", "planName", "plan", "package_name", "packageName", "tier", "subscription_plan"],
        "Plan not shown",
      );

      const planStatus = readString(
        nestedBilling,
        ["status", "subscription_status", "subscriptionStatus", "plan_status", "planStatus"],
        billing.ok ? "Active" : "Unavailable",
      );

      const creditsAvailable = readNumber(
        nestedCredits,
        ["available_credits", "availableCredits", "credits_available", "creditsAvailable", "remaining_credits", "remainingCredits", "balance", "credits"],
      );

      const creditsUsed = readNumber(
        nestedCredits,
        ["used_credits", "usedCredits", "credits_used", "creditsUsed"],
      );

      const creditsLimit = readNumber(
        nestedCredits,
        ["credit_limit", "creditLimit", "credits_limit", "creditsLimit", "monthly_credits", "monthlyCredits"],
      );

      const creditStatus = readString(
        nestedCredits,
        ["status", "credit_status", "creditStatus", "enforcement_status", "enforcementStatus"],
        credits.ok ? "Available" : "Unavailable",
      );

      setState({
        planName,
        planStatus,
        creditsAvailable,
        creditsUsed,
        creditsLimit,
        creditStatus,
        loading: false,
        error: billing.ok || credits.ok ? null : "Billing and credit status could not be loaded.",
      });
    }

    loadBillingAndCredits();

    return () => {
      cancelled = true;
    };
  }, []);

  const creditSummary = useMemo(() => {
    if (state.creditsAvailable !== null) {
      return `${state.creditsAvailable}`;
    }
    if (state.creditsLimit !== null && state.creditsUsed !== null) {
      return `${Math.max(state.creditsLimit - state.creditsUsed, 0)}`;
    }
    return "Not shown";
  }, [state.creditsAvailable, state.creditsLimit, state.creditsUsed]);

  const usageSummary = useMemo(() => {
    if (state.creditsUsed !== null && state.creditsLimit !== null) {
      return `${state.creditsUsed} used of ${state.creditsLimit}`;
    }
    if (state.creditsUsed !== null) {
      return `${state.creditsUsed} used`;
    }
    if (state.creditsLimit !== null) {
      return `${state.creditsLimit} included`;
    }
    return "Usage not shown";
  }, [state.creditsLimit, state.creditsUsed]);

  const goToBilling = (intent: "upgrade" | "credits" | "manage") => {
    const params = new URLSearchParams({ intent });
    window.location.href = `/client/billing?${params.toString()}`;
  };

  return (
    <section
      data-client-plan-credit-status-card="true"
      style={{
        margin: "18px 0 24px",
        padding: 22,
        borderRadius: 24,
        border: "1px solid rgba(99, 102, 241, 0.34)",
        background: "linear-gradient(135deg, #081226 0%, #101946 100%)",
        boxShadow: "0 18px 45px rgba(0, 0, 0, 0.24)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 18,
          flexWrap: "wrap",
          alignItems: "flex-start",
        }}
      >
        <div>
          <p
            style={{
              margin: "0 0 8px",
              color: "#8ea7ff",
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}
          >
            Plan and credits
          </p>
          <h2 style={{ margin: 0, color: "#ffffff", fontSize: 24, fontWeight: 950 }}>
            Your current access
          </h2>
          <p style={{ margin: "8px 0 0", color: "#9fb1d1", fontSize: 14, lineHeight: 1.6 }}>
            See your active plan, available credits, and billing actions before starting new work.
          </p>
        </div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            type="button"
            onClick={() => goToBilling("upgrade")}
            style={{
              border: 0,
              borderRadius: 999,
              padding: "11px 15px",
              background: "#6d5dfc",
              color: "#ffffff",
              fontWeight: 900,
              cursor: "pointer",
            }}
          >
            Upgrade plan
          </button>
          <button
            type="button"
            onClick={() => goToBilling("credits")}
            style={{
              border: "1px solid rgba(165, 180, 252, 0.45)",
              borderRadius: 999,
              padding: "11px 15px",
              background: "rgba(15, 23, 42, 0.84)",
              color: "#dbeafe",
              fontWeight: 900,
              cursor: "pointer",
            }}
          >
            Buy more credits
          </button>
          <button
            type="button"
            onClick={() => goToBilling("manage")}
            style={{
              border: "1px solid rgba(148, 163, 184, 0.32)",
              borderRadius: 999,
              padding: "11px 15px",
              background: "rgba(15, 23, 42, 0.58)",
              color: "#cbd5e1",
              fontWeight: 850,
              cursor: "pointer",
            }}
          >
            Manage billing
          </button>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
          gap: 12,
          marginTop: 18,
        }}
      >
        <div style={{ padding: 15, borderRadius: 18, background: "rgba(3, 7, 18, 0.58)", border: "1px solid rgba(148, 163, 184, 0.22)" }}>
          <p style={{ margin: "0 0 6px", color: "#94a3b8", fontSize: 12, fontWeight: 850 }}>Current plan</p>
          <strong style={{ color: "#ffffff", fontSize: 20 }}>{state.loading ? "Loading" : state.planName}</strong>
          <p style={{ margin: "6px 0 0", color: "#9fb1d1", fontSize: 12 }}>Status: {state.planStatus}</p>
        </div>

        <div style={{ padding: 15, borderRadius: 18, background: "rgba(3, 7, 18, 0.58)", border: "1px solid rgba(148, 163, 184, 0.22)" }}>
          <p style={{ margin: "0 0 6px", color: "#94a3b8", fontSize: 12, fontWeight: 850 }}>Available credits</p>
          <strong style={{ color: "#ffffff", fontSize: 20 }}>{state.loading ? "Loading" : creditSummary}</strong>
          <p style={{ margin: "6px 0 0", color: "#9fb1d1", fontSize: 12 }}>{usageSummary}</p>
        </div>

        <div style={{ padding: 15, borderRadius: 18, background: "rgba(3, 7, 18, 0.58)", border: "1px solid rgba(148, 163, 184, 0.22)" }}>
          <p style={{ margin: "0 0 6px", color: "#94a3b8", fontSize: 12, fontWeight: 850 }}>Credit status</p>
          <strong style={{ color: "#ffffff", fontSize: 20 }}>{state.loading ? "Checking" : state.creditStatus}</strong>
          <p style={{ margin: "6px 0 0", color: "#9fb1d1", fontSize: 12 }}>
            Credits are checked before governed executions.
          </p>
        </div>
      </div>

      {state.error ? (
        <p style={{ margin: "14px 0 0", color: "#fbbf24", fontSize: 13 }}>
          {state.error}
        </p>
      ) : null}
    </section>
  );
}
'''.lstrip(), encoding="utf-8", newline="\n")

text = CLIENT_PAGE.read_text(encoding="utf-8-sig", errors="ignore").replace("\ufeff", "")
text = re.sub(r'(?m)^\s*[\'"]use client[\'"];\s*\r?\n?', "", text)
text = '"use client";\n\n' + text.strip() + "\n"

import_line = 'import ClientPlanCreditStatusCard from "../../components/ClientPlanCreditStatusCard";'
if import_line not in text:
    lines = text.splitlines()
    insert_at = 1
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].strip() == ""):
        insert_at += 1
    lines.insert(insert_at, import_line)
    text = "\n".join(lines) + "\n"

if "<ClientPlanCreditStatusCard" not in text:
    media_card_marker = "<ClientCreateMediaProductionCard"
    marker_index = text.find(media_card_marker)
    if marker_index >= 0:
      insert_at = text.find("/>", marker_index)
      if insert_at >= 0:
          insert_at += 2
          text = text[:insert_at] + "\n\n      <ClientPlanCreditStatusCard />" + text[insert_at:]
    else:
        main_match = re.search(r'(<main[^>]*>)', text)
        if main_match:
            text = text[:main_match.end()] + "\n      <ClientPlanCreditStatusCard />\n" + text[main_match.end():]

CLIENT_PAGE.write_text("\n".join(line.rstrip() for line in text.splitlines()).strip() + "\n", encoding="utf-8", newline="\n")

VERIFY.write_text(r'''
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
component = ROOT / "frontend" / "src" / "components" / "ClientPlanCreditStatusCard.tsx"

client_text = client_page.read_text(encoding="utf-8", errors="ignore")
component_text = component.read_text(encoding="utf-8", errors="ignore") if component.exists() else ""

required = [
    "Plan and credits",
    "Current plan",
    "Available credits",
    "Credit status",
    "Upgrade plan",
    "Buy more credits",
    "Manage billing",
    "/api/billing-subscription-status",
    "/api/package-credit-enforcement-status",
    "/client/billing?",
]

proof = {
    "client_plan_credit_status_attempted": True,
    "client_plan_credit_status_passed": True,
    "component_exists": component.exists(),
    "component_imported": "ClientPlanCreditStatusCard" in client_text,
    "component_mounted": "<ClientPlanCreditStatusCard" in client_text,
    "use_client_first_line_client_page": client_text.splitlines()[0].strip() == '"use client";',
    "use_client_first_line_component": component_text.splitlines()[0].strip() == '"use client";' if component_text else False,
    "required_phrases_present": {item: item in component_text for item in required},
    "stripe_live_charge_attempted": False,
    "billing_mutation_attempted": False,
    "credit_mutation_attempted": False,
    "provider_call_attempted": False,
    "media_generation_attempted": False,
    "aws21_or_later_work_attempted": False,
    "public_cutover_enabled": False,
}

proof["client_plan_credit_status_passed"] = (
    proof["component_exists"]
    and proof["component_imported"]
    and proof["component_mounted"]
    and proof["use_client_first_line_client_page"]
    and proof["use_client_first_line_component"]
    and all(proof["required_phrases_present"].values())
)

print("CLIENT_PLAN_CREDIT_STATUS_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["client_plan_credit_status_passed"]:
    raise SystemExit("CLIENT_PLAN_CREDIT_STATUS_FAILED")

print("CLIENT_PLAN_CREDIT_STATUS_PASSED")
'''.lstrip(), encoding="utf-8")

print(json.dumps({
    "client_plan_credit_status_card": True,
    "component": str(COMPONENT),
    "client_page": str(CLIENT_PAGE),
    "backup": str(backup_dir),
    "verifier": str(VERIFY),
    "stripe_live_charge": False,
    "billing_mutation": False,
    "credit_mutation": False,
    "provider_calls": False,
    "media_generation": False,
}, indent=2))
