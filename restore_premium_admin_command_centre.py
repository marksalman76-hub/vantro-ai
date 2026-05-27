from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = root / "backups" / f"admin_command_centre_restore_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

if target.exists():
    shutil.copy2(target, backup_dir / "page.tsx")

content = r'''const adminCards = [
  {
    eyebrow: "Control Status",
    status: "GOVERNED",
    title: "Runtime Control",
    copy: "Owner-level control for runtime health, deployment readiness, protected routes, and operational checks.",
    href: "/admin",
  },
  {
    eyebrow: "Provider Execution",
    status: "LIVE",
    title: "Provider Execution",
    copy: "Monitor provider jobs, delivery packets, retries, timeouts, governed actions, and customer-safe execution visibility.",
    href: "/admin/provider-execution",
  },
  {
    eyebrow: "System Operations",
    status: "READY",
    title: "Runtime Health",
    copy: "Protected platform health, provider readiness, billing readiness, database state, and execution controls.",
    href: "/admin",
  },
  {
    eyebrow: "Governance",
    status: "CONTROLLED",
    title: "Approvals",
    copy: "Owner-only review area for spend, strategy, scaling, high-risk execution, and governed automation decisions.",
    href: "/admin",
  },
  {
    eyebrow: "Workspace Control",
    status: "LOCKED",
    title: "Clients & Tenants",
    copy: "Tenant/workspace visibility, package state, activation status, account control, and entitlement-safe management.",
    href: "/admin",
  },
  {
    eyebrow: "Security",
    status: "PROTECTED",
    title: "Secret Protection",
    copy: "Admin-safe surfaces, protected provider details, private request instructions, and credential exposure controls.",
    href: "/admin",
  },
];

const readinessRows = [
  ["Provider runtime", "COMPLETE"],
  ["Admin API protection", "COMPLETE"],
  ["Customer portal", "COMPLETE"],
  ["Signup activation", "COMPLETE"],
  ["Billing readiness", "COMPLETE"],
  ["Security governance", "COMPLETE"],
  ["Database persistence", "COMPLETE"],
  ["Production deployment", "COMPLETE"],
];

export default function AdminCommandCentrePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, rgba(99,102,241,.22), transparent 34%), linear-gradient(135deg,#06111f 0%,#0f172a 45%,#111827 100%)",
        color: "#f8fafc",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        padding: "34px",
      }}
    >
      <section
        style={{
          maxWidth: 1240,
          margin: "0 auto",
        }}
      >
        <div
          style={{
            border: "1px solid rgba(148,163,184,.22)",
            background: "rgba(15,23,42,.72)",
            borderRadius: 30,
            padding: 28,
            boxShadow: "0 30px 90px rgba(0,0,0,.34)",
            backdropFilter: "blur(16px)",
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
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "8px 12px",
                  borderRadius: 999,
                  border: "1px solid rgba(129,140,248,.35)",
                  background: "rgba(79,70,229,.16)",
                  color: "#c7d2fe",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: ".08em",
                  textTransform: "uppercase",
                }}
              >
                Owner Control Plane
              </div>

              <h1
                style={{
                  margin: "18px 0 8px",
                  fontSize: "clamp(34px, 5vw, 62px)",
                  lineHeight: 0.95,
                  letterSpacing: "-.06em",
                  fontWeight: 950,
                }}
              >
                Admin Command Centre
              </h1>

              <p
                style={{
                  maxWidth: 860,
                  color: "#cbd5e1",
                  fontSize: 18,
                  lineHeight: 1.55,
                  margin: 0,
                }}
              >
                Central owner console for governed platform operations. This page links only to
                admin-safe control surfaces and preserves tenant isolation, credential protection,
                customer-safe summaries, and owner-only approval authority.
              </p>
            </div>

            <div
              style={{
                minWidth: 230,
                border: "1px solid rgba(34,197,94,.32)",
                borderRadius: 22,
                padding: 18,
                background: "rgba(20,83,45,.22)",
              }}
            >
              <div style={{ color: "#86efac", fontWeight: 950, fontSize: 13 }}>
                FINALISATION STATUS
              </div>
              <div style={{ fontSize: 34, fontWeight: 950, marginTop: 4 }}>15 / 15</div>
              <div style={{ color: "#bbf7d0", fontSize: 13, marginTop: 4 }}>
                Matrix rows verified live
              </div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
              gap: 16,
              marginTop: 28,
            }}
          >
            {adminCards.map((card) => (
              <a
                key={card.title}
                href={card.href}
                style={{
                  textDecoration: "none",
                  color: "inherit",
                  display: "block",
                  border: "1px solid rgba(148,163,184,.20)",
                  borderRadius: 24,
                  padding: 20,
                  background:
                    "linear-gradient(180deg, rgba(30,41,59,.86), rgba(15,23,42,.92))",
                  boxShadow: "0 18px 48px rgba(0,0,0,.24)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                  <div
                    style={{
                      color: "#a5b4fc",
                      fontSize: 11,
                      fontWeight: 950,
                      letterSpacing: ".08em",
                      textTransform: "uppercase",
                    }}
                  >
                    {card.eyebrow}
                  </div>
                  <div
                    style={{
                      color: "#bbf7d0",
                      background: "rgba(34,197,94,.12)",
                      border: "1px solid rgba(34,197,94,.22)",
                      borderRadius: 999,
                      padding: "4px 8px",
                      fontSize: 10,
                      fontWeight: 950,
                    }}
                  >
                    {card.status}
                  </div>
                </div>

                <h2
                  style={{
                    fontSize: 24,
                    lineHeight: 1.08,
                    margin: "18px 0 8px",
                    fontWeight: 950,
                    letterSpacing: "-.03em",
                  }}
                >
                  {card.title}
                </h2>

                <p style={{ color: "#cbd5e1", fontSize: 14, lineHeight: 1.55, margin: 0 }}>
                  {card.copy}
                </p>

                <div
                  style={{
                    marginTop: 18,
                    color: "#c4b5fd",
                    fontWeight: 900,
                    fontSize: 13,
                  }}
                >
                  Open section →
                </div>
              </a>
            ))}
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(0, 1.1fr) minmax(300px, .9fr)",
            gap: 18,
            marginTop: 18,
          }}
        >
          <section
            style={{
              border: "1px solid rgba(148,163,184,.20)",
              background: "rgba(15,23,42,.76)",
              borderRadius: 26,
              padding: 22,
              boxShadow: "0 20px 60px rgba(0,0,0,.22)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 26, fontWeight: 950 }}>Governance Rules</h2>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: 12,
                marginTop: 16,
              }}
            >
              {[
                "No agent may increase spend or scale campaigns without owner approval.",
                "No agent may change package entitlements without admin approval.",
                "No client can alter activated agent selections directly.",
                "No frontend view may expose protected provider details or private request instructions.",
                "Customer-facing outputs must remain safe, polished, and non-internal.",
                "Runtime actions must remain protected by admin/server-side controls.",
              ].map((rule) => (
                <div
                  key={rule}
                  style={{
                    border: "1px solid rgba(148,163,184,.18)",
                    borderRadius: 18,
                    padding: 14,
                    background: "rgba(2,6,23,.48)",
                    color: "#cbd5e1",
                    fontSize: 14,
                    lineHeight: 1.5,
                  }}
                >
                  {rule}
                </div>
              ))}
            </div>
          </section>

          <section
            style={{
              border: "1px solid rgba(148,163,184,.20)",
              background: "rgba(15,23,42,.76)",
              borderRadius: 26,
              padding: 22,
              boxShadow: "0 20px 60px rgba(0,0,0,.22)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 26, fontWeight: 950 }}>Readiness Panel</h2>
            <div style={{ marginTop: 16, display: "grid", gap: 10 }}>
              {readinessRows.map(([label, value]) => (
                <div
                  key={label}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 12,
                    border: "1px solid rgba(148,163,184,.18)",
                    borderRadius: 16,
                    padding: "12px 14px",
                    background: "rgba(2,6,23,.46)",
                  }}
                >
                  <span style={{ color: "#cbd5e1", fontSize: 14 }}>{label}</span>
                  <span style={{ color: "#86efac", fontSize: 12, fontWeight: 950 }}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
'''

target.write_text(content, encoding="utf-8")

print("PREMIUM_ADMIN_COMMAND_CENTRE_RESTORED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")