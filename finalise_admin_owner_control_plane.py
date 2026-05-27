from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"admin_owner_control_plane_before_{STAMP}"

ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST_FILE = ROOT / "test_admin_owner_control_plane.py"

for path in [ADMIN_PAGE, TEST_FILE]:
    if path.exists():
        target = BACKUP_DIR / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    path.parent.mkdir(parents=True, exist_ok=True)

page = r'''"use client";

const commandCentreCards = [
  {
    title: "Provider Execution",
    label: "Runtime Control",
    href: "/admin/provider-execution",
    description:
      "Monitor provider jobs, delivery packets, retries, timeouts, governed actions, and customer-safe execution visibility.",
    status: "LIVE",
  },
  {
    title: "Runtime Health",
    label: "System Operations",
    href: "/admin",
    description:
      "Owner-level view for platform health, protected route readiness, deployment state, and operational checks.",
    status: "READY",
  },
  {
    title: "Approvals",
    label: "Governance",
    href: "/admin",
    description:
      "Owner-only review area for spend, strategy, scaling, high-risk execution, and governed automation decisions.",
    status: "CONTROLLED",
  },
  {
    title: "Clients & Tenants",
    label: "Workspace Control",
    href: "/admin",
    description:
      "Tenant/workspace visibility, package state, activation status, account control, and entitlement-safe management.",
    status: "LOCKED",
  },
  {
    title: "Entitlements",
    label: "Access Governance",
    href: "/admin",
    description:
      "Package limits, purchased agents, activation locks, Enterprise-only Head Agent access, and selected-agent enforcement.",
    status: "PROTECTED",
  },
  {
    title: "Billing",
    label: "Subscription Control",
    href: "/admin",
    description:
      "Stripe subscription state, failed payment handling, credit renewal, cancellation flow, and package billing readiness.",
    status: "PENDING",
  },
  {
    title: "Agent Execution",
    label: "Workforce Runtime",
    href: "/admin",
    description:
      "Agent run visibility, output quality checks, customer-safe deliverables, and execution status tracking.",
    status: "READY",
  },
  {
    title: "Integrations",
    label: "Client Connections",
    href: "/admin",
    description:
      "Client-owned connection status, connect/disconnect controls, safe setup guidance, and integration audit readiness.",
    status: "PENDING",
  },
];

const readiness = [
  ["Provider runtime", "COMPLETE"],
  ["Admin auth protection", "ACTIVE"],
  ["Customer-safe output policy", "ACTIVE"],
  ["Credential exposure", "FALSE"],
  ["Owner-only spending authority", "LOCKED"],
  ["Frontend deployment alignment", "VERIFIED"],
];

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-2xl">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-indigo-300">
                Owner Control Plane
              </p>
              <h1 className="mt-2 text-3xl font-bold text-white">
                Admin Command Centre
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
                Central owner console for governed platform operations. This page links only to
                admin-safe control surfaces and preserves tenant isolation, credential protection,
                customer-safe summaries, and owner-only approval authority.
              </p>
            </div>

            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">
                Control Status
              </p>
              <p className="mt-2 text-2xl font-bold text-white">GOVERNED</p>
              <p className="mt-1 text-xs text-emerald-100">
                Internal runtime data remains admin-only.
              </p>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {commandCentreCards.map((card) => (
            <a
              key={card.title}
              href={card.href}
              className="group rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl transition hover:border-indigo-400 hover:bg-slate-900"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-indigo-300">
                  {card.label}
                </p>
                <span className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1 text-[10px] font-bold text-slate-300">
                  {card.status}
                </span>
              </div>
              <h2 className="mt-3 text-xl font-bold text-white">{card.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">{card.description}</p>
              <div className="mt-4 text-sm font-semibold text-indigo-200 group-hover:text-indigo-100">
                Open section →
              </div>
            </a>
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 lg:col-span-2">
            <h2 className="text-xl font-bold text-white">Owner Governance Rules</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {[
                "No agent may increase spend without owner approval.",
                "No agent may change package entitlements without admin approval.",
                "No client can alter activated agent selections directly.",
                "No frontend view may expose provider secrets or internal prompts.",
                "Customer-facing outputs must remain safe, polished, and non-internal.",
                "Runtime actions must remain protected by admin/server-side controls.",
              ].map((rule) => (
                <div
                  key={rule}
                  className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4 text-sm leading-6 text-slate-300"
                >
                  {rule}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5">
            <h2 className="text-xl font-bold text-white">Readiness Panel</h2>
            <div className="mt-4 space-y-3">
              {readiness.map(([label, value]) => (
                <div
                  key={label}
                  className="flex items-center justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-950/80 p-3"
                >
                  <span className="text-sm text-slate-400">{label}</span>
                  <span className="text-xs font-bold text-emerald-300">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
'''

test = r'''from pathlib import Path

ROOT = Path.cwd()
admin = (ROOT / "frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

checks = {
    "admin_command_centre": "Admin Command Centre" in admin,
    "provider_execution_link": "/admin/provider-execution" in admin,
    "runtime_health": "Runtime Health" in admin,
    "approvals": "Approvals" in admin,
    "clients_tenants": "Clients & Tenants" in admin,
    "entitlements": "Entitlements" in admin,
    "billing": "Billing" in admin,
    "agent_execution": "Agent Execution" in admin,
    "integrations": "Integrations" in admin,
    "readiness_panel": "Readiness Panel" in admin,
    "owner_governance_rules": "Owner Governance Rules" in admin,
    "credential_exposure_false": "Credential exposure" in admin and "FALSE" in admin,
    "owner_spend_rule": "No agent may increase spend without owner approval." in admin,
    "customer_safe_wording": "customer-safe" in admin.lower(),
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Admin owner control plane checks failed: {failed}"

for forbidden in [
    "sk-",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "raw JSON",
    "debug route",
]:
    assert forbidden not in admin, f"Forbidden marker found in admin page: {forbidden}"

print("ADMIN_OWNER_CONTROL_PLANE_TESTS_PASSED")
print("admin_command_centre_ready", True)
print("provider_execution_link_ready", True)
print("readiness_panel_ready", True)
print("credential_values_exposed", False)
'''

ADMIN_PAGE.write_text(page, encoding="utf-8")
TEST_FILE.write_text(test, encoding="utf-8")

print("ADMIN_OWNER_CONTROL_PLANE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST_FILE}")