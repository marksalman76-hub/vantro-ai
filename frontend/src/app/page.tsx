const plans = [
  {
    name: "Starter",
    price: "$99",
    unit: "USD/mo",
    description: "Launch your first agent workflows and validate before you scale.",
    href: "/signup?plan=starter",
    features: ["Up to 5 AI agents", "Starter workflows", "Demo-to-live upgrade"],
  },
  {
    name: "Growth",
    price: "$279",
    unit: "USD/mo",
    description: "Run a full multi-agent ecommerce operation across marketing, content, and analytics.",
    href: "/signup?plan=growth",
    featured: true,
    features: ["Up to 20 AI agents", "Advanced workflows", "Priority execution"],
  },
  {
    name: "Business",
    price: "$449",
    unit: "USD/mo",
    description: "Advanced automation with full analytics, priority execution, and premium support.",
    href: "/signup?plan=business",
    features: ["Up to 50 AI agents", "Advanced automation", "Premium support"],
  },
  {
    name: "Enterprise",
    price: "Custom",
    unit: "",
    description: "Custom agent stack, white-label deployment, and dedicated onboarding.",
    href: "/signup?plan=enterprise",
    enterprise: true,
    features: ["Custom agent stack", "White-label setup", "Dedicated onboarding"],
  },
];

const agentGroups = [
  ["Research & Strategy", ["Product Research Agent", "Competitor Intelligence Agent", "Brand Strategy Agent"]],
  ["Creative & Content", ["Product Copywriting Agent", "UGC Creative Agent", "Product Image Direction Agent", "Ad Creative Agent", "Website / Landing Page Agent"]],
  ["Campaigns & Ads", ["Campaign Launch Agent", "Creative Rotation Agent", "Analytics Optimisation Agent"]],
  ["Operations & Fulfilment", ["Store Builder Agent", "Fulfilment Agent", "Customer Support Agent", "Email Marketing Agent"]],
  ["Growth & Intelligence", ["SEO Agent", "Marketplace Agent", "Influencer Collaboration Agent", "Reporting Agent", "Quality Assurance Agent"]],
];

const workspaceAgents = [
  ["Ad Creative Agent", "Generated 3 hook variants · 94% score"],
  ["UGC Creative Agent", "Creator brief prepared · ready"],
  ["SEO Agent", "Keyword cluster built · localised"],
  ["Analytics Agent", "Campaign insight found · action ready"],
  ["Email Agent", "Recovery sequence drafted · approved"],
  ["Product Copy Agent", "Offer angle improved · 91% score"],
];

function CheckIcon() {
  return <span style={{ color: "#0D9488", fontWeight: 800 }}>✓</span>;
}

export default function HomePage() {
  return (
    <main style={{ minHeight: "100vh", background: "#F8FAFC", color: "#0F172A", fontFamily: "Inter, sans-serif" }}>
      <header style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        background: "rgba(255,255,255,.92)",
        backdropFilter: "blur(14px)",
        borderBottom: "1px solid #E2E8F0",
      }}>
        <div style={{
          maxWidth: 1480,
          margin: "0 auto",
          padding: "14px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 18,
          flexWrap: "wrap",
        }}>
          <a href="/" style={{ display: "flex", alignItems: "center", gap: 12, textDecoration: "none", color: "#0F172A" }}>
            <div style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              background: "#4F46E5",
              color: "#fff",
              display: "grid",
              placeItems: "center",
              fontWeight: 900,
            }}>
              AI
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 17 }}>AI Commerce Platform</div>
              <div style={{ color: "#64748B", fontSize: 12 }}>Premium AI workforce</div>
            </div>
          </a>

          <nav style={{ display: "flex", gap: 18, alignItems: "center", flexWrap: "wrap" }}>
            <a href="#agents" style={{ color: "#334155", textDecoration: "none", fontSize: 15, fontWeight: 500 }}>Agents</a>
            <a href="#pricing" style={{ color: "#334155", textDecoration: "none", fontSize: 15, fontWeight: 500 }}>Pricing</a>
            <a href="/login" style={{ color: "#334155", textDecoration: "none", fontSize: 15, fontWeight: 500 }}>Log in</a>
            <a href="/signup" style={{
              textDecoration: "none",
              color: "#fff",
              background: "#4F46E5",
              padding: "12px 20px",
              borderRadius: 8,
              fontSize: 15,
              fontWeight: 700,
            }}>
              Start free demo →
            </a>
          </nav>
        </div>
      </header>

      <section style={{
        background: "#fff",
        borderBottom: "1px solid #E2E8F0",
      }}>
        <div style={{
          maxWidth: 1480,
          margin: "0 auto",
          padding: "72px 24px 64px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(340px,1fr))",
          gap: 48,
          alignItems: "center",
        }}>
          <div>
            <div style={{
              color: "#0D9488",
              fontSize: 12,
              fontWeight: 700,
              letterSpacing: ".1em",
              textTransform: "uppercase",
              marginBottom: 18,
            }}>
              Ecommerce AI Workforce Platform
            </div>

            <h1 style={{
              margin: 0,
              fontSize: "clamp(42px,7vw,72px)",
              lineHeight: 1.04,
              letterSpacing: "-0.045em",
              fontWeight: 900,
              maxWidth: 760,
            }}>
              Run your ecommerce business with a premium AI workforce.
            </h1>

            <p style={{
              marginTop: 22,
              color: "#334155",
              fontSize: "clamp(16px,2vw,20px)",
              lineHeight: 1.7,
              maxWidth: 680,
            }}>
              Activate expert AI agents for marketing, content, CRM, SEO, analytics, outreach, and ecommerce execution workflows with premium outputs and white-label deployment.
            </p>

            <div style={{ display: "flex", gap: 14, marginTop: 30, flexWrap: "wrap" }}>
              <a href="/signup" style={{
                color: "#fff",
                background: "#4F46E5",
                textDecoration: "none",
                borderRadius: 8,
                padding: "14px 24px",
                fontWeight: 700,
              }}>
                Start free demo →
              </a>

              <a href="#pricing" style={{
                color: "#334155",
                background: "#fff",
                textDecoration: "none",
                borderRadius: 8,
                padding: "14px 24px",
                fontWeight: 700,
                border: "1px solid #E2E8F0",
              }}>
                See pricing →
              </a>
            </div>

            <p style={{ color: "#64748B", fontSize: 13, marginTop: 16 }}>
              No credit card required · Full feature preview · Cancel anytime
            </p>

            <div style={{
              display: "flex",
              gap: 20,
              marginTop: 30,
              flexWrap: "wrap",
              color: "#64748B",
              fontSize: 14,
            }}>
              <span>Approval-safe</span>
              <span>·</span>
              <span>White-label ready</span>
              <span>·</span>
              <span>Multi-agent</span>
              <span>·</span>
              <span>Global-ready</span>
            </div>
          </div>

          <div style={{
            background: "#fff",
            border: "1px solid #E2E8F0",
            borderRadius: 16,
            boxShadow: "0 18px 50px rgba(15,23,42,.08)",
            overflow: "hidden",
          }}>
            <div style={{
              height: 38,
              background: "#F8FAFC",
              borderBottom: "1px solid #E2E8F0",
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "0 16px",
            }}>
              <span style={{ width: 8, height: 8, borderRadius: 999, background: "#E2E8F0" }} />
              <span style={{ width: 8, height: 8, borderRadius: 999, background: "#E2E8F0" }} />
              <span style={{ width: 8, height: 8, borderRadius: 999, background: "#0D9488" }} />
            </div>

            <div style={{ padding: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "center", flexWrap: "wrap" }}>
                <div>
                  <div style={{ fontSize: 22, fontWeight: 800 }}>Live agent workspace</div>
                  <div style={{ color: "#64748B", fontSize: 13, marginTop: 4 }}>Client-ready execution preview</div>
                </div>
                <span style={{
                  background: "#F0FDF4",
                  color: "#047857",
                  borderRadius: 20,
                  padding: "5px 12px",
                  fontSize: 11,
                  fontWeight: 700,
                }}>
                  Ready
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 12, marginTop: 22 }}>
                {workspaceAgents.map(([name, output]) => (
                  <div key={name} style={{
                    position: "relative",
                    background: "#fff",
                    border: "1px solid #E2E8F0",
                    borderRadius: 12,
                    padding: 16,
                    minHeight: 108,
                  }}>
                    <span style={{ position: "absolute", top: 14, right: 14, width: 7, height: 7, borderRadius: 999, background: "#0D9488" }} />
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#0F172A", paddingRight: 14 }}>{name}</div>
                    <div style={{ color: "#64748B", fontSize: 11, lineHeight: 1.5, marginTop: 10 }}>{output}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="agents" style={{ padding: "72px 24px", background: "#F8FAFC", borderBottom: "1px solid #E2E8F0" }}>
        <div style={{ maxWidth: 1480, margin: "0 auto" }}>
          <div style={{ color: "#0D9488", fontSize: 12, fontWeight: 700, letterSpacing: ".1em", textTransform: "uppercase" }}>
            The AI Workforce
          </div>
          <h2 style={{ margin: "12px 0 0", fontSize: "clamp(32px,4vw,48px)", lineHeight: 1.1, letterSpacing: "-.03em" }}>
            24 expert agents. One unified platform.
          </h2>
          <p style={{ marginTop: 16, color: "#64748B", lineHeight: 1.7, maxWidth: 760 }}>
            Specialist ecommerce agents across strategy, content, creative, operations, analytics, growth, and governance.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 20, marginTop: 32 }}>
            {agentGroups.map(([category, agents]) => (
              <div key={category as string} style={{
                background: "#fff",
                border: "1px solid #E2E8F0",
                borderRadius: 12,
                padding: 24,
              }}>
                <div style={{ color: "#0D9488", fontSize: 12, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase" }}>
                  {category as string}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 16 }}>
                  {(agents as string[]).map((agent) => (
                    <span key={agent} style={{
                      background: "#F8FAFC",
                      border: "1px solid #E2E8F0",
                      borderRadius: 20,
                      padding: "6px 14px",
                      fontSize: 13,
                      fontWeight: 500,
                      color: "#334155",
                    }}>
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <p style={{ marginTop: 24, color: "#64748B", fontSize: 14 }}>
            Enterprise plans include Head Agent and Orchestration Agent for cross-agent coordination.
          </p>
        </div>
      </section>

      <section style={{ background: "#fff", borderBottom: "1px solid #E2E8F0", padding: "24px" }}>
        <div style={{
          maxWidth: 1480,
          margin: "0 auto",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: 18,
          flexWrap: "wrap",
          color: "#334155",
          fontSize: 14,
          fontWeight: 500,
        }}>
          <span>148 successful executions</span>
          <span style={{ color: "#64748B" }}>·</span>
          <span>8 active subscriptions</span>
          <span style={{ color: "#64748B" }}>·</span>
          <span>24 specialist agents</span>
          <span style={{ color: "#64748B" }}>·</span>
          <span>Global deployment ready</span>
        </div>
      </section>

      <section id="pricing" style={{ maxWidth: 1480, margin: "0 auto", padding: "72px 24px 88px" }}>
        <div style={{ textAlign: "center", marginBottom: 34 }}>
          <div style={{ color: "#0D9488", fontWeight: 700, letterSpacing: ".1em", fontSize: 12, textTransform: "uppercase" }}>Pricing</div>
          <h2 style={{ margin: "10px 0 10px", fontSize: "clamp(32px,4vw,48px)", letterSpacing: "-0.03em" }}>
            Start with the right AI workforce.
          </h2>
          <p style={{ margin: 0, color: "#64748B", fontSize: 16 }}>
            Try the platform free. Upgrade to a live plan when you're ready.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 20 }}>
          {plans.map((plan) => (
            <div key={plan.name} style={{
              position: "relative",
              background: plan.enterprise ? "#F0FDFA" : "#fff",
              border: plan.featured ? "2px solid #4F46E5" : plan.enterprise ? "1px solid #99F6E4" : "1px solid #E2E8F0",
              borderRadius: 12,
              padding: 24,
              minHeight: 380,
              display: "flex",
              flexDirection: "column",
            }}>
              {plan.featured ? (
                <span style={{
                  position: "absolute",
                  top: 18,
                  right: 18,
                  background: "#EEF2FF",
                  color: "#4F46E5",
                  fontSize: 11,
                  padding: "3px 10px",
                  borderRadius: 20,
                  fontWeight: 700,
                }}>
                  Most popular
                </span>
              ) : null}

              <div style={{ fontWeight: 800, fontSize: 22 }}>{plan.name}</div>
              <p style={{ color: "#64748B", lineHeight: 1.6, minHeight: 76 }}>{plan.description}</p>

              <div style={{ marginTop: 8 }}>
                <div style={{ fontWeight: 900, fontSize: 52, letterSpacing: "-.02em" }}>{plan.price}</div>
                {plan.unit ? <div style={{ color: "#64748B", fontSize: 13 }}>{plan.unit}</div> : null}
              </div>

              <div style={{ marginTop: 22, display: "grid", gap: 10, color: "#334155", fontSize: 14, lineHeight: 1.6 }}>
                {plan.features.map((feature) => (
                  <div key={feature} style={{ display: "flex", gap: 10 }}>
                    <CheckIcon />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              <a href={plan.href} style={{
                marginTop: "auto",
                display: "block",
                textAlign: "center",
                textDecoration: "none",
                background: plan.featured ? "#4F46E5" : plan.enterprise ? "#0F172A" : "#fff",
                color: plan.featured || plan.enterprise ? "#fff" : "#4F46E5",
                border: plan.featured || plan.enterprise ? "none" : "1px solid #4F46E5",
                borderRadius: 8,
                padding: "13px 16px",
                fontWeight: 700,
              }}>
                {plan.name === "Enterprise" ? "Talk to sales" : plan.name === "Growth" ? "Start with Growth" : "Get started"}
              </a>

              {plan.enterprise ? <div style={{ marginTop: 10, color: "#64748B", fontSize: 12, textAlign: "center" }}>Response within 24 hours</div> : null}
            </div>
          ))}
        </div>
      </section>

      <footer style={{ background: "#0F172A", color: "#fff", padding: "48px 24px" }}>
        <div style={{ maxWidth: 1480, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 32 }}>
          <div>
            <strong style={{ fontSize: 16 }}>Ecommerce AI Agent Platform</strong>
            <p style={{ color: "#94A3B8", fontSize: 14, lineHeight: 1.7 }}>Premium AI workforce for ecommerce businesses.</p>
          </div>
          <div>
            <div style={{ color: "#94A3B8", fontSize: 12, textTransform: "uppercase", letterSpacing: ".08em" }}>Product</div>
            <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
              <a href="#agents" style={{ color: "#fff", textDecoration: "none", fontSize: 14 }}>Agents</a>
              <a href="#pricing" style={{ color: "#fff", textDecoration: "none", fontSize: 14 }}>Pricing</a>
              <a href="/signup" style={{ color: "#fff", textDecoration: "none", fontSize: 14 }}>Demo</a>
              <a href="/login" style={{ color: "#fff", textDecoration: "none", fontSize: 14 }}>Login</a>
            </div>
          </div>
          <div>
            <div style={{ color: "#94A3B8", fontSize: 12, textTransform: "uppercase", letterSpacing: ".08em" }}>Company</div>
            <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
              <span style={{ color: "#fff", fontSize: 14 }}>Privacy Policy</span>
              <span style={{ color: "#fff", fontSize: 14 }}>Terms of Service</span>
              <span style={{ color: "#fff", fontSize: 14 }}>Contact</span>
            </div>
          </div>
        </div>
        <div style={{
          maxWidth: 1480,
          margin: "32px auto 0",
          paddingTop: 24,
          borderTop: "1px solid #2D3F55",
          display: "flex",
          justifyContent: "space-between",
          gap: 16,
          flexWrap: "wrap",
          color: "#94A3B8",
          fontSize: 13,
        }}>
          <span>© 2026 Ecommerce AI Agent Platform</span>
          <span>Built for ecommerce operators worldwide.</span>
        </div>
      </footer>
    </main>
  );
}
