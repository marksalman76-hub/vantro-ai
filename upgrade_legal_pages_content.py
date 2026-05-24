from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
APP = ROOT / "frontend" / "src" / "app"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

privacy = APP / "privacy-policy" / "page.tsx"
terms = APP / "terms-of-service" / "page.tsx"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

privacy_backup = BACKUPS / f"privacy_policy_before_upgrade_{timestamp}.tsx"
terms_backup = BACKUPS / f"terms_before_upgrade_{timestamp}.tsx"

shutil.copy2(privacy, privacy_backup)
shutil.copy2(terms, terms_backup)

privacy.write_text(
'''import Link from "next/link";

export default function PrivacyPolicyPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, rgba(67,56,202,.24), transparent 34%), #020617",
        padding: "64px 24px",
        color: "#f8fafc",
      }}
    >
      <div
        style={{
          maxWidth: 820,
          margin: "0 auto",
          background: "rgba(7,16,40,.92)",
          border: "1px solid rgba(99,102,241,.22)",
          borderRadius: 28,
          padding: "40px",
          boxShadow: "0 30px 70px rgba(0,0,0,.35)",
        }}
      >
        <div
          style={{
            fontSize: 12,
            fontWeight: 900,
            letterSpacing: ".14em",
            color: "#a5b4fc",
            marginBottom: 10,
          }}
        >
          PRIVACY
        </div>

        <h1
          style={{
            fontSize: "clamp(38px,5vw,56px)",
            lineHeight: 1,
            marginBottom: 20,
            fontWeight: 900,
          }}
        >
          Privacy Policy
        </h1>

        <p
          style={{
            color: "#cbd5e1",
            lineHeight: 1.7,
            fontSize: 16,
            marginBottom: 26,
          }}
        >
          This Privacy Policy explains how the Ecommerce AI Agent Platform
          collects, uses, protects, and processes workspace information,
          business profile data, integrations, execution activity, and support
          requests while operating the platform.
        </p>

        {[
          {
            title: "Workspace & business profile data",
            body:
              "Business profile information is used to personalise AI execution, improve deliverable relevance, and adapt outputs to the client’s market, audience, products, positioning, and operating region.",
          },
          {
            title: "AI execution & platform activity",
            body:
              "Execution activity, approvals, delivery actions, workflow history, and governed automation events may be logged for security, audit visibility, reliability improvements, and platform quality control.",
          },
          {
            title: "Payments & billing security",
            body:
              "Payment information is processed through secure third-party billing providers such as Stripe. Sensitive payment details are not stored directly inside the workspace interface.",
          },
          {
            title: "Integrations & connected services",
            body:
              "Clients may connect approved third-party tools including ecommerce stores, CRMs, calendars, communication tools, analytics platforms, and marketing systems. Access permissions remain controlled by the connected account owner.",
          },
          {
            title: "Data protection & governance",
            body:
              "The platform uses governed execution controls, access restrictions, authentication protections, approval layers, audit visibility, and monitored infrastructure to help protect workspace operations and client data.",
          },
          {
            title: "Client ownership & responsibility",
            body:
              "Clients remain responsible for reviewing business information, uploaded assets, connected integrations, generated outputs, and approval decisions before live commercial use.",
          },
          {
            title: "Support & privacy requests",
            body:
              "Clients may contact support to request help with account access, workspace issues, billing enquiries, privacy requests, or connected service management.",
          },
        ].map((item) => (
          <div
            key={item.title}
            style={{
              border: "1px solid rgba(99,102,241,.22)",
              borderRadius: 18,
              padding: "20px 22px",
              marginBottom: 16,
              background: "rgba(12,24,49,.72)",
            }}
          >
            <div
              style={{
                fontWeight: 900,
                fontSize: 18,
                marginBottom: 10,
              }}
            >
              {item.title}
            </div>

            <div
              style={{
                color: "#cbd5e1",
                lineHeight: 1.7,
                fontSize: 15,
              }}
            >
              {item.body}
            </div>
          </div>
        ))}

        <div style={{ marginTop: 28 }}>
          <Link
            href="/client"
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              minWidth: 190,
              height: 54,
              borderRadius: 16,
              textDecoration: "none",
              background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
              color: "#fff",
              fontWeight: 900,
              boxShadow: "0 18px 38px rgba(79,70,229,.32)",
            }}
          >
            Back to workspace
          </Link>
        </div>
      </div>
    </main>
  );
}
''',
encoding="utf-8",
)

terms.write_text(
'''import Link from "next/link";

export default function TermsPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, rgba(67,56,202,.24), transparent 34%), #020617",
        padding: "64px 24px",
        color: "#f8fafc",
      }}
    >
      <div
        style={{
          maxWidth: 820,
          margin: "0 auto",
          background: "rgba(7,16,40,.92)",
          border: "1px solid rgba(99,102,241,.22)",
          borderRadius: 28,
          padding: "40px",
          boxShadow: "0 30px 70px rgba(0,0,0,.35)",
        }}
      >
        <div
          style={{
            fontSize: 12,
            fontWeight: 900,
            letterSpacing: ".14em",
            color: "#a5b4fc",
            marginBottom: 10,
          }}
        >
          TERMS
        </div>

        <h1
          style={{
            fontSize: "clamp(38px,5vw,56px)",
            lineHeight: 1,
            marginBottom: 20,
            fontWeight: 900,
          }}
        >
          Terms of Service
        </h1>

        <p
          style={{
            color: "#cbd5e1",
            lineHeight: 1.7,
            fontSize: 16,
            marginBottom: 26,
          }}
        >
          These Terms of Service govern the use of the Ecommerce AI Agent
          Platform, including workspace access, governed AI execution,
          subscriptions, integrations, billing, and platform functionality.
        </p>

        {[
          {
            title: "Governed AI execution",
            body:
              "AI-generated outputs, automation flows, and execution recommendations operate within governed approval controls designed to reduce unsafe or unauthorised commercial actions.",
          },
          {
            title: "Client review responsibility",
            body:
              "Clients are responsible for reviewing generated outputs, campaigns, deliverables, recommendations, integrations, and execution actions before live business deployment or public release.",
          },
          {
            title: "Subscription & billing access",
            body:
              "Workspace features, credits, active agents, integrations, execution capacity, and platform access may depend on the client’s active subscription status and package entitlements.",
          },
          {
            title: "Connected integrations",
            body:
              "Clients may connect approved third-party services to support governed execution workflows. Clients remain responsible for maintaining authorised access to connected systems.",
          },
          {
            title: "Restricted & prohibited usage",
            body:
              "Users must not attempt to bypass governance systems, access restricted platform internals, abuse integrations, interfere with platform operations, or use the service for unlawful activity.",
          },
          {
            title: "Platform updates & improvements",
            body:
              "The platform may update workflows, features, interfaces, safeguards, security systems, and execution capabilities to improve reliability, quality, compliance, and operational performance.",
          },
          {
            title: "Security & account protection",
            body:
              "Clients are responsible for maintaining secure account credentials, protecting connected integrations, and notifying support of suspected unauthorised access or security concerns.",
          },
          {
            title: "Support & operational assistance",
            body:
              "Support access is available for approved billing enquiries, workspace issues, integration troubleshooting, account recovery, and governed platform assistance requests.",
          },
        ].map((item) => (
          <div
            key={item.title}
            style={{
              border: "1px solid rgba(99,102,241,.22)",
              borderRadius: 18,
              padding: "20px 22px",
              marginBottom: 16,
              background: "rgba(12,24,49,.72)",
            }}
          >
            <div
              style={{
                fontWeight: 900,
                fontSize: 18,
                marginBottom: 10,
              }}
            >
              {item.title}
            </div>

            <div
              style={{
                color: "#cbd5e1",
                lineHeight: 1.7,
                fontSize: 15,
              }}
            >
              {item.body}
            </div>
          </div>
        ))}

        <div style={{ marginTop: 28 }}>
          <Link
            href="/client"
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              minWidth: 190,
              height: 54,
              borderRadius: 16,
              textDecoration: "none",
              background: "linear-gradient(135deg,#7c3aed,#4f46e5)",
              color: "#fff",
              fontWeight: 900,
              boxShadow: "0 18px 38px rgba(79,70,229,.32)",
            }}
          >
            Back to workspace
          </Link>
        </div>
      </div>
    </main>
  );
}
''',
encoding="utf-8",
)

print("LEGAL_PAGES_UPGRADED")
print("Privacy backup:", privacy_backup)
print("Terms backup:", terms_backup)