export default function RefundPolicyPage() {
  const sections = [
    {
      title: "Refund eligibility",
      body:
        "Refund requests may only be considered where the account has not been activated, used, executed, connected to integrations for execution, consumed credits, or generated deliverables, outputs, reports, media, assets, recommendations, or other platform materials.",
    },
    {
      title: "When an account becomes non-refundable",
      body:
        "An account becomes ineligible for a refund immediately upon the first successful execution of any AI agent, workflow, automation, delegated workforce task, provider action, content generation request, media generation request, deliverable creation event, credit consumption event, or integration-driven execution activity.",
    },
    {
      title: "No refund after activation or use",
      body:
        "If the system has been activated and used, all subscription fees and associated platform charges are non-refundable except where required by applicable law.",
    },
    {
      title: "Usage verification",
      body:
        "The platform may review execution logs, billing records, credit-consumption records, generated deliverables, integration activity, provider execution records, and workspace history to determine refund eligibility.",
    },
    {
      title: "Owner review",
      body:
        "All refund requests are subject to owner review, governance verification, audit-log review, and platform usage validation. Owner override may apply only in exceptional circumstances.",
    },
  ];

  return (
    <main style={{ minHeight: "100vh", background: "#050b18", color: "#f8fafc", fontFamily: "Inter, Arial, sans-serif", padding: "48px 20px" }}>
      <section style={{ maxWidth: 980, margin: "0 auto", background: "linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98))", border: "1px solid rgba(129,140,248,.24)", borderRadius: 28, padding: "clamp(24px,4vw,46px)", boxShadow: "0 24px 80px rgba(0,0,0,.34)" }}>
        <div style={{ color: "#a5b4fc", fontSize: 12, fontWeight: 900, letterSpacing: ".18em", textTransform: "uppercase", marginBottom: 10 }}>
          Billing policy
        </div>
        <h1 style={{ margin: 0, fontSize: "clamp(30px,4vw,48px)", letterSpacing: -1.4 }}>
          Refund Policy
        </h1>
        <p style={{ marginTop: 14, color: "#cbd5e1", lineHeight: 1.7, fontSize: 15 }}>
          This Refund Policy explains when refunds may be considered for the Ecommerce AI Agent Platform.
        </p>

        <div style={{ display: "grid", gap: 14, marginTop: 28 }}>
          {sections.map((section) => (
            <article key={section.title} style={{ border: "1px solid rgba(129,140,248,.20)", background: "rgba(15,23,42,.72)", borderRadius: 18, padding: 18 }}>
              <h2 style={{ margin: 0, fontSize: 18 }}>{section.title}</h2>
              <p style={{ margin: "9px 0 0", color: "#94a3b8", lineHeight: 1.65, fontSize: 14 }}>{section.body}</p>
            </article>
          ))}
        </div>

        <div style={{ marginTop: 28, display: "flex", gap: 10, flexWrap: "wrap" }}>
          <a href="/terms-of-service" style={{ color: "#c4b5fd", fontWeight: 850 }}>Terms of Service</a>
          <a href="/privacy-policy" style={{ color: "#c4b5fd", fontWeight: 850 }}>Privacy Policy</a>
          <a href="/support-request?topic=refund" style={{ color: "#c4b5fd", fontWeight: 850 }}>Contact support</a>
        </div>
      </section>
    </main>
  );
}
