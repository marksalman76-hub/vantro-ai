const plans = [
  {
    name: "Starter",
    price: "$99",
    description: "For small teams testing AI execution.",
    href: "/signup?plan=starter",
    icon: "✦",
    features: ["Up to 5 AI agents", "Starter workflows", "Demo-to-live upgrade"],
  },
  {
    name: "Growth",
    price: "$279",
    description: "For growing businesses using multiple agents.",
    href: "/signup?plan=growth",
    icon: "◆",
    featured: true,
    features: ["Up to 20 AI agents", "Advanced workflows", "Priority execution"],
  },
  {
    name: "Business",
    price: "$449",
    description: "For teams ready for advanced automation.",
    href: "/signup?plan=business",
    icon: "▣",
    features: ["Up to 50 AI agents", "Advanced automation", "Premium support"],
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "Tailored enterprise and white-label deployment.",
    href: "/admin-login",
    icon: "◇",
    features: ["Custom agent stack", "White-label setup", "Dedicated onboarding"],
  },
];

const agents = [
  ["Marketing", "Campaigns and offers"],
  ["UGC Creative", "Scripts and creator briefs"],
  ["SEO", "Content and rankings"],
  ["CRM", "Follow-up and conversion"],
  ["Analytics", "Insights and optimisation"],
  ["Outreach", "Influencer workflows"],
];

export default function HomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 12% 12%, rgba(99,91,255,0.16), transparent 30%), radial-gradient(circle at 92% 18%, rgba(59,130,246,0.13), transparent 32%), linear-gradient(180deg,#ffffff 0%,#f7f8ff 52%,#ffffff 100%)",
        color: "#0f172a",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <header
        style={{
          background: "rgba(255,255,255,0.82)",
          borderBottom: "1px solid #eef1f6",
          backdropFilter: "blur(18px)",
          position: "sticky",
          top: 0,
          zIndex: 20,
        }}
      >
        <div
          style={{
            maxWidth: 1320,
            margin: "0 auto",
            padding: "18px 32px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 18,
                background: "linear-gradient(135deg,#635BFF,#2563EB)",
                color: "#fff",
                display: "grid",
                placeItems: "center",
                fontWeight: 950,
                fontSize: 22,
                boxShadow: "0 16px 40px rgba(99,91,255,0.24)",
              }}
            >
              AI
            </div>
            <div>
              <div style={{ fontWeight: 950, fontSize: 22 }}>AI Commerce Platform</div>
              <div style={{ color: "#667085", fontSize: 14 }}>Premium AI workforce</div>
            </div>
          </div>

          <nav style={{ display: "flex", gap: 28, alignItems: "center", fontWeight: 800 }}>
            <a href="#agents" style={{ color: "#344054", textDecoration: "none" }}>Agents</a>
            <a href="#plans" style={{ color: "#344054", textDecoration: "none" }}>Pricing</a>
            <a
              href="/client?demo=true"
              style={{
                textDecoration: "none",
                color: "#fff",
                background: "linear-gradient(135deg,#635BFF,#4F46E5)",
                padding: "13px 20px",
                borderRadius: 14,
                boxShadow: "0 16px 36px rgba(99,91,255,0.24)",
              }}
            >
              Try Temporary Demo
            </a>
          </nav>
        </div>
      </header>

      <section
        style={{
          maxWidth: 1320,
          margin: "0 auto",
          padding: "72px 32px 38px",
          display: "grid",
          gridTemplateColumns: "1.02fr 0.98fr",
          gap: 52,
          alignItems: "center",
        }}
      >
        <div>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              background: "#EEF2FF",
              color: "#4F46E5",
              border: "1px solid #dfe5ff",
              borderRadius: 999,
              padding: "10px 16px",
              fontWeight: 900,
              marginBottom: 26,
            }}
          >
            ✦ Temporary demo access available
          </div>

          <h1
            style={{
              margin: 0,
              fontSize: 74,
              lineHeight: 1.02,
              letterSpacing: "-0.055em",
              fontWeight: 950,
              maxWidth: 760,
            }}
          >
            Run your business with a{" "}
            <span
              style={{
                background: "linear-gradient(135deg,#635BFF,#2563EB)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              premium
            </span>{" "}
            AI workforce.
          </h1>

          <p
            style={{
              marginTop: 26,
              maxWidth: 690,
              color: "#4B5563",
              fontSize: 21,
              lineHeight: 1.65,
            }}
          >
            Activate expert AI agents for marketing, content, CRM, SEO, analytics,
            outreach, and execution workflows — with premium outputs, safe approvals,
            and white-label deployment.
          </p>

          <div style={{ display: "flex", gap: 16, marginTop: 34 }}>
            <a
              href="/client?demo=true"
              style={{
                color: "#fff",
                background: "linear-gradient(135deg,#635BFF,#4F46E5)",
                textDecoration: "none",
                borderRadius: 16,
                padding: "17px 24px",
                fontWeight: 950,
                boxShadow: "0 18px 42px rgba(99,91,255,0.26)",
              }}
            >
              Try Temporary Demo →
            </a>

            <a
              href="#plans"
              style={{
                color: "#111827",
                background: "#fff",
                textDecoration: "none",
                borderRadius: 16,
                padding: "17px 24px",
                fontWeight: 950,
                border: "1px solid #e5e7eb",
              }}
            >
              See Pricing →
            </a>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
              marginTop: 34,
              maxWidth: 710,
              background: "rgba(255,255,255,0.78)",
              border: "1px solid #e7eaf4",
              borderRadius: 18,
              overflow: "hidden",
              boxShadow: "0 16px 35px rgba(15,23,42,0.04)",
            }}
          >
            {["Approval-safe", "White-label ready", "Multi-agent", "Global-ready"].map((item) => (
              <div
                key={item}
                style={{
                  padding: "15px 12px",
                  textAlign: "center",
                  fontWeight: 850,
                  color: "#344054",
                  borderRight: "1px solid #eef1f6",
                  whiteSpace: "nowrap",
                }}
              >
                ✓ {item}
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            background: "rgba(255,255,255,0.88)",
            border: "1px solid rgba(228,231,236,0.88)",
            borderRadius: 34,
            padding: 30,
            boxShadow: "0 38px 90px rgba(99,91,255,0.14)",
            backdropFilter: "blur(18px)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: 24 }}>
            <div>
              <div style={{ fontSize: 30, fontWeight: 950 }}>Demo Workspace</div>
              <div style={{ color: "#667085", marginTop: 4 }}>Safe preview mode</div>
            </div>
            <div style={{ background: "#DCFCE7", color: "#15803D", borderRadius: 999, padding: "8px 13px", fontWeight: 900 }}>
              ● Ready
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0,1fr))", gap: 14 }}>
            {agents.map(([name, desc]) => (
              <div
                key={name}
                style={{
                  background: "#fff",
                  border: "1px solid #edf0f5",
                  borderRadius: 20,
                  padding: 18,
                  minHeight: 118,
                  boxShadow: "0 10px 26px rgba(15,23,42,0.035)",
                }}
              >
                <div
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: 13,
                    background: "linear-gradient(135deg,#EEF2FF,#F5F3FF)",
                    display: "grid",
                    placeItems: "center",
                    color: "#635BFF",
                    fontWeight: 950,
                    marginBottom: 14,
                  }}
                >
                  ✦
                </div>
                <div style={{ fontWeight: 950, fontSize: 16 }}>{name}</div>
                <div style={{ color: "#667085", fontSize: 13, marginTop: 5 }}>{desc}</div>
              </div>
            ))}
          </div>

          <div
            style={{
              marginTop: 18,
              background: "linear-gradient(135deg,#F5F3FF,#EEF4FF)",
              border: "1px solid #ddd6fe",
              borderRadius: 22,
              padding: 20,
              display: "flex",
              gap: 16,
              alignItems: "center",
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 16,
                background: "#fff",
                display: "grid",
                placeItems: "center",
                color: "#635BFF",
                fontWeight: 950,
              }}
            >
              🔒
            </div>
            <div>
              <div style={{ fontWeight: 950, color: "#4F46E5" }}>Capped demo. No hidden access.</div>
              <div style={{ color: "#4B5563", lineHeight: 1.55, marginTop: 4 }}>
                Test safely without internal configuration, production credentials, or restricted agents.
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        id="plans"
        style={{
          maxWidth: 1220,
          margin: "0 auto",
          padding: "44px 32px 86px",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 30 }}>
          <div style={{ color: "#4F46E5", fontWeight: 950, letterSpacing: ".08em", fontSize: 13 }}>PLANS</div>
          <h2 style={{ margin: "8px 0 8px", fontSize: 44, letterSpacing: "-0.04em" }}>
            Start with the right AI workforce.
          </h2>
          <p style={{ margin: 0, color: "#667085", fontSize: 17 }}>
            Demo first, then upgrade into a live paid plan.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0,1fr))", gap: 18 }}>
          {plans.map((plan) => (
            <div
              key={plan.name}
              style={{
                background: "#fff",
                border: plan.featured ? "2px solid #635BFF" : "1px solid #edf0f5",
                borderRadius: 22,
                padding: 22,
                boxShadow: plan.featured
                  ? "0 24px 58px rgba(99,91,255,0.14)"
                  : "0 14px 34px rgba(15,23,42,0.045)",
                minHeight: 276,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 13, marginBottom: 14 }}>
                <div
                  style={{
                    width: 46,
                    height: 46,
                    borderRadius: 16,
                    background: "linear-gradient(135deg,#EEF2FF,#F5F3FF)",
                    display: "grid",
                    placeItems: "center",
                    color: "#635BFF",
                    fontWeight: 950,
                    fontSize: 20,
                  }}
                >
                  {plan.icon}
                </div>
                <div>
                  <div style={{ fontWeight: 950, fontSize: 20 }}>{plan.name}</div>
                  {plan.featured && (
                    <div style={{ color: "#635BFF", fontSize: 12, fontWeight: 950, marginTop: 3 }}>
                      POPULAR
                    </div>
                  )}
                </div>
              </div>

              <div style={{ fontWeight: 950, fontSize: 38, letterSpacing: "-0.04em" }}>
                {plan.price}
                {plan.price !== "Custom" && (
                  <span style={{ fontSize: 13, color: "#667085", marginLeft: 6 }}>USD/mo</span>
                )}
              </div>

              <p style={{ color: "#667085", lineHeight: 1.55, minHeight: 48, marginTop: 10 }}>
                {plan.description}
              </p>

              <div style={{ marginTop: 4, display: "grid", gap: 6, color: "#344054", fontSize: 13 }}>
                {plan.features.map((feature) => (
                  <div key={feature}>✓ {feature}</div>
                ))}
              </div>

              <a
                href={plan.href}
                style={{
                  marginTop: "auto",
                  display: "block",
                  textAlign: "center",
                  textDecoration: "none",
                  background: plan.featured ? "linear-gradient(135deg,#635BFF,#4F46E5)" : "#fff",
                  color: plan.featured ? "#fff" : "#4F46E5",
                  border: plan.featured ? "none" : "1px solid #d8ddff",
                  borderRadius: 14,
                  padding: "13px 16px",
                  fontWeight: 950,
                }}
              >
                {plan.name === "Enterprise" ? "Contact Sales" : `Start ${plan.name}`}
              </a>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
