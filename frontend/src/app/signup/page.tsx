"use client";

import { Suspense, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

const plans = {
  starter: { name: "Starter", price: "$99", limit: 3, summary: "For small teams testing AI execution." },
  growth: { name: "Growth", price: "$279", limit: 7, summary: "For growing businesses using multiple agents." },
  business: { name: "Business", price: "$429", limit: 10, summary: "For advanced automation and scale." },
  enterprise: { name: "Enterprise", price: "Custom", limit: 37, summary: "Full orchestration, white-label, and enterprise controls." },
};

const agents = [
  ["marketing_specialist_agent", "Marketing Specialist Agent", "Growth & Marketing", "Campaigns, offers, positioning, promotions, and execution-ready marketing plans."],
  ["seo_agent", "SEO Agent", "Growth & Marketing", "SEO strategy, content optimisation, technical SEO, local SEO, rankings, and visibility."],
  ["social_media_manager_content_creator_agent", "Social Media Manager / Content Creator Agent", "Content & Creative", "Social content, captions, calendars, engagement ideas, and platform-specific creative direction."],
  ["email_reply_agent", "Email Reply Agent", "Sales & CRM", "Email replies, inbox handling, customer responses, and follow-up drafting."],
  ["crm_ai_agent", "CRM AI Agent", "Sales & CRM", "CRM workflows, lead notes, customer records, pipeline updates, and follow-up support."],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent", "Analytics", "Analytics reviews, conversion insights, optimisation recommendations, and performance reporting."],
  ["ugc_creative_agent", "Content Strategy Agent", "Content & Creative", "Content strategy, campaign ideas, messaging angles, planning support, and execution-ready content direction."],
  ["product_image_agent", "Visual Brand Asset Agent", "Ecommerce", "Brand visual concepts, asset planning, image direction, and campaign-ready creative support."],
  ["influencer_collaboration_agent", "Influencer Collaboration Agent", "Growth & Marketing", "Influencer shortlist, outreach angles, collaboration planning, and creator partnership support."],
  ["product_copywriting_agent", "Product Copywriting Agent", "Ecommerce", "Product descriptions, product page copy, conversion messaging, and offer copy."],
  ["customer_service_agent", "Customer Service Agent", "Operations", "Customer support replies, FAQs, issue handling, service tone, and resolution workflows."],
  ["sales_closer_agent", "Sales / Closer Agent", "Sales & CRM", "Quote follow-up, proposal follow-up, objection handling, deal progression, and closing support."],
  ["lead_generator_appointment_setter_agent", "Lead Generator / Appointment Setter Agent", "Sales & CRM", "Lead generation, appointment setting, outreach sequences, qualification, and booking support."],
  ["business_growth_partnerships_agent", "Business Growth & Partnerships Agent", "Strategy", "Growth opportunities, partnership ideas, collaboration strategy, and revenue expansion support."],
  ["strategist_agent", "Strategist Agent", "Strategy", "Business strategy, planning, positioning, priorities, and commercial decision support."],
  ["ecommerce_manager_agent", "Ecommerce Manager Agent", "Ecommerce", "Store operations, product merchandising, conversion support, and ecommerce execution planning."],
  ["product_research_agent", "Product Research Agent", "Ecommerce", "Product research, market gaps, product opportunities, trend review, and competitor product analysis."],
  ["pricing_profit_agent", "Pricing & Profit Agent", "Ecommerce", "Pricing recommendations, margin review, offer economics, bundles, and profit optimisation."],
  ["inventory_operations_agent", "Inventory & Operations Agent", "Operations", "Inventory planning, stock movement, operational workflows, and fulfilment coordination support."],
  ["ads_campaign_agent", "Ads Campaign Agent", "Growth & Marketing", "Paid ad strategy, campaign briefs, audience targeting, creative direction, and optimisation recommendations."],
  ["website_app_developer_agent", "Custom Websites, Landing Pages & Apps Developer Agent", "Content & Creative", "Website, landing page, portal, app, and interface planning for client-ready digital experiences."],
  ["brand_manager_agent", "Brand Manager Agent", "Strategy", "Brand voice, positioning, messaging consistency, visual direction, and premium brand presentation."],
  ["content_strategy_agent", "Content Strategy Agent", "Content & Creative", "Content planning, topics, calendars, channel strategy, and long-form content direction."],
  ["market_research_agent", "Market Research Agent", "Strategy", "Market insights, competitor review, buyer behaviour, positioning, and opportunity analysis."],
  ["workflow_automation_agent", "Workflow Automation Agent", "Operations", "Automation ideas, workflow mapping, process improvement, and operational efficiency recommendations."],
  ["head_agent", "Head Agent", "Enterprise", "Enterprise-only cross-agent leadership, review, escalation, and owner-level coordination."],
  ["orchestration_agent", "Orchestration Agent", "Enterprise", "Enterprise-only multi-agent task coordination, sequencing, and execution orchestration."],
];

function SignupContent() {
  const params = useSearchParams();
  const rawPlan = (params.get("plan") || "growth").toLowerCase();
  const planKey = (rawPlan in plans ? rawPlan : "growth") as keyof typeof plans;
  const plan = plans[planKey];
  const isEnterprise = planKey === "enterprise";

  const [email, setEmail] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [category, setCategory] = useState("All Agents");
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const categories = ["All Agents", "Growth & Marketing", "Sales & CRM", "Content & Creative", "Ecommerce", "Operations", "Strategy", "Analytics", "Enterprise"];

  const visibleAgents = useMemo(() => {
    return agents.filter(([id, name, cat, desc]) => {
      const enterpriseOnly = id === "head_agent" || id === "orchestration_agent";
      if (enterpriseOnly && !isEnterprise) return false;
      if (category !== "All Agents" && cat !== category) return false;
      const q = search.toLowerCase();
      return !q || name.toLowerCase().includes(q) || desc.toLowerCase().includes(q) || cat.toLowerCase().includes(q);
    });
  }, [category, search, isEnterprise]);

  function toggleAgent(id: string) {
    setMessage("");

    if (selected.includes(id)) {
      setSelected(selected.filter((x) => x !== id));
      return;
    }

    if (selected.length >= plan.limit) {
      setMessage(`${plan.name} allows up to ${plan.limit} selected agents.`);
      return;
    }

    setSelected([...selected, id]);
  }

  async function startCheckout() {
    setBusy(true);
    setMessage("");

    try {
      if (!email.includes("@")) {
        setMessage("Enter a valid work email.");
        return;
      }

      if (selected.length === 0) {
        setMessage("Select at least one agent.");
        return;
      }

      const response = await fetch("/api/billing-checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_email: email, target_package: planKey, selected_agents: selected }),
      });

      const data = await response.json();
      const checkoutUrl = data.checkout_url || data.url || data.session_url || data.stripe_checkout_url;

      if (checkoutUrl) {
        window.location.href = checkoutUrl;
        return;
      }

      setMessage(data.reason || data.error || "Checkout did not return a Stripe URL.");
    } catch {
      setMessage("Checkout could not be started.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ minHeight: "100vh", background: "radial-gradient(circle at 12% 10%, rgba(99,91,255,.14), transparent 28%), linear-gradient(180deg,#fff 0%,#f8f9ff 100%)", fontFamily: "Inter,Arial,sans-serif", color: "#111827", padding: 20 }}>
      <section style={{ maxWidth: 1560, margin: "0 auto", display: "grid", gridTemplateColumns: "360px 1fr", gap: 24 }}>
        <aside style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 28, padding: 28, boxShadow: "0 24px 60px rgba(15,23,42,.06)", position: "sticky", top: 20, height: "calc(100vh - 40px)" }}>
          <a href="/" style={{ color: "#4f46e5", textDecoration: "none", fontWeight: 900 }}>← Back to home</a>

          <div style={{ marginTop: 28, padding: 18, borderRadius: 22, background: "#f8f7ff", border: "1px solid #ddd6fe" }}>
            <div style={{ color: "#635BFF", fontWeight: 950 }}>Step 2 of 3</div>
            <h1 style={{ fontSize: 30, lineHeight: 1.08, margin: "12px 0 8px" }}>Start your <span style={{ color: "#635BFF" }}>{plan.name}</span> plan</h1>
            <p style={{ color: "#667085", lineHeight: 1.55, margin: 0 }}>{plan.summary}</p>
          </div>

          <div style={{ marginTop: 20, padding: 18, borderRadius: 20, border: "1px solid #e5e7eb" }}>
            <div style={{ color: "#667085", fontWeight: 850 }}>Plan summary</div>
            <div style={{ fontSize: 36, fontWeight: 950, marginTop: 8 }}>
              {plan.price}
              {plan.price !== "Custom" && <span style={{ fontSize: 14, color: "#667085" }}> USD / mo</span>}
            </div>
            <div style={{ marginTop: 12, color: "#16a34a", fontWeight: 800 }}>✓ Up to {plan.limit} agents</div>
            <div style={{ marginTop: 8, color: "#16a34a", fontWeight: 800 }}>✓ Cancel anytime</div>
            <div style={{ marginTop: 8, color: "#16a34a", fontWeight: 800 }}>✓ Secure Stripe checkout</div>
          </div>

          <label style={{ display: "block", marginTop: 22, fontWeight: 900 }}>Work email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="you@company.com" style={{ width: "100%", boxSizing: "border-box", marginTop: 10, padding: "14px 15px", borderRadius: 14, border: "1px solid #d1d5db", fontSize: 15 }} />

          <button onClick={startCheckout} disabled={busy || !email.includes("@") || selected.length === 0} style={{ width: "100%", marginTop: 18, border: "none", borderRadius: 15, padding: "15px 18px", fontWeight: 950, color: "#fff", background: busy || !email.includes("@") || selected.length === 0 ? "#9ca3af" : "linear-gradient(135deg,#635BFF,#4F46E5)", cursor: busy || !email.includes("@") || selected.length === 0 ? "not-allowed" : "pointer" }}>
            {busy ? "Starting checkout..." : "Continue to secure checkout"}
          </button>

          {message && <p style={{ color: "#b45309", lineHeight: 1.5 }}>{message}</p>}

          <div style={{ marginTop: 22, padding: 18, borderRadius: 18, background: "#f8f7ff", color: "#635BFF", fontWeight: 850, textAlign: "center" }}>
            Head Agent and Orchestration Agent are Enterprise-only.
          </div>
        </aside>

        <section>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0,1fr))", gap: 14, marginBottom: 20 }}>
            {Object.entries(plans).map(([key, item]) => (
              <a key={key} href={`/signup?plan=${key}`} style={{ textDecoration: "none", color: "#111827", background: "#fff", border: key === planKey ? "2px solid #635BFF" : "1px solid #e5e7eb", borderRadius: 20, padding: 18, boxShadow: "0 12px 32px rgba(15,23,42,.045)" }}>
                <div style={{ fontWeight: 950, fontSize: 20 }}>{item.name}</div>
                <div style={{ color: "#4f46e5", fontSize: 24, fontWeight: 950, marginTop: 5 }}>{item.price}</div>
                <div style={{ color: "#667085", fontSize: 13, marginTop: 5 }}>{`Up to ${item.limit} agents`}</div>
              </a>
            ))}
          </div>

          <div style={{ background: "rgba(255,255,255,.86)", border: "1px solid #e5e7eb", borderRadius: 28, padding: 22, boxShadow: "0 24px 60px rgba(15,23,42,.05)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 20, flexWrap: "wrap" }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 30 }}>Select your agents</h2>
                <p style={{ color: "#667085", margin: "6px 0 0" }}>{selected.length}/{plan.limit} selected</p>
              </div>

              <div style={{ display: "flex", gap: 10 }}>
                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search agents..." style={{ padding: "12px 14px", borderRadius: 13, border: "1px solid #d1d5db", minWidth: 260 }} />
                <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ padding: "12px 14px", borderRadius: 13, border: "1px solid #d1d5db" }}>
                  {categories.map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 18 }}>
              {categories.map((c) => (
                <button key={c} onClick={() => setCategory(c)} style={{ border: "none", borderRadius: 999, padding: "9px 12px", fontWeight: 850, color: category === c ? "#fff" : "#4f46e5", background: category === c ? "#635BFF" : "#eef2ff", cursor: "pointer" }}>{c}</button>
              ))}
            </div>

            <div style={{ marginTop: 20, display: "grid", gridTemplateColumns: "repeat(4, minmax(0,1fr))", gap: 14 }}>
              {visibleAgents.map(([id, name, cat, desc]) => {
                const isSelected = selected.includes(id);
                return (
                  <button key={id} onClick={() => toggleAgent(id)} style={{ textAlign: "left", minHeight: 150, border: isSelected ? "2px solid #635BFF" : "1px solid #e5e7eb", background: isSelected ? "#f5f3ff" : "#fff", borderRadius: 18, padding: 16, cursor: "pointer" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                      <strong>{name}</strong>
                      <span style={{ color: isSelected ? "#4f46e5" : "#9ca3af", fontWeight: 900 }}>{isSelected ? "Selected" : "Select"}</span>
                    </div>
                    <div style={{ color: "#635BFF", fontSize: 12, fontWeight: 900, marginTop: 8 }}>{cat}</div>
                    <p style={{ color: "#667085", lineHeight: 1.45, fontSize: 13 }}>{desc}</p>
                  </button>
                );
              })}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={<div style={{ padding: 40, fontFamily: "Inter,Arial" }}>Loading...</div>}>
      <SignupContent />
    </Suspense>
  );
}
