from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
page = root / "frontend" / "src" / "app" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"page_before_business_pricing_packages_{stamp}.tsx"

s = page.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

pricing_start = s.index("const PRICING = [")
pricing_end = s.index("// ─── 3D COMPONENTS")

new_pricing = '''const PRICING = [
  {
    name: "Starter",
    price: 99,
    desc: "For small teams starting with a governed AI workforce.",
    features: ["1-3 active AI agents", "Business profile intelligence", "Governed task execution", "Client workspace access", "Email support"],
    cta: "Get Starter",
    highlight: false,
  },
  {
    name: "Growth",
    price: 279,
    desc: "For growing businesses ready to automate daily operations.",
    features: ["4-7 active AI agents", "Multi-agent workflows", "Approval-gated execution", "Business memory layer", "Priority support"],
    cta: "Get Growth",
    highlight: true,
  },
  {
    name: "Business",
    price: 429,
    desc: "For established teams scaling AI across core departments.",
    features: ["7-10 active AI agents", "Advanced workflow orchestration", "Governance and audit controls", "Premium output intelligence", "Priority onboarding"],
    cta: "Get Business",
    highlight: false,
  },
  {
    name: "Enterprise",
    price: null,
    desc: "For larger organisations needing custom deployment and control.",
    features: ["Full AI workforce catalogue", "Custom agent deployment", "White-label options", "Advanced security controls", "Dedicated implementation support"],
    cta: "Contact sales",
    highlight: false,
  },
];

// ─── 3D COMPONENTS ──────────────────────────────────────────────────────────

'''

s = s[:pricing_start] + new_pricing + s[pricing_end + len("// ─── 3D COMPONENTS ──────────────────────────────────────────────────────────\n\n"):]

function_start = s.index("function Pricing() {")
function_end = s.index("// ─── TESTIMONIALS")

new_function = '''function Pricing() {
  return (
    <section className="pricing" id="pricing">
      <div className="section-header">
        <motion.span className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <Infinity size={13} /> PRICING
        </motion.span>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
          Simple monthly pricing for every stage.
        </motion.h2>
        <motion.p className="section-subtitle" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
          Start with the workforce size you need today, then scale as your operations grow.
        </motion.p>
      </div>

      <div className="pricing__grid">
        {PRICING.map((plan, i) => (
          <motion.div
            key={plan.name}
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.7 }}
            className={`pricing-card ${plan.highlight ? "pricing-card--highlight" : ""}`}
          >
            {plan.highlight && <div className="pricing-card__popular">Most popular</div>}
            <div className="pricing-card__name">{plan.name}</div>
            <div className="pricing-card__price">
              {plan.price
                ? <><span className="pricing-card__currency">$</span>{plan.price}<span className="pricing-card__period"> USD/mo</span></>
                : <span className="pricing-card__custom">Custom</span>
              }
            </div>
            <p className="pricing-card__desc">{plan.desc}</p>
            <a href="/signup" className={`pricing-card__cta ${plan.highlight ? "pricing-card__cta--highlight" : ""}`}>
              {plan.cta} <ArrowRight size={14} />
            </a>
            <ul className="pricing-card__features">
              {plan.features.map(f => (
                <li key={f}>
                  <CheckCircle2 size={14} />
                  {f}
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

// ─── TESTIMONIALS ────────────────────────────────────────────────────────────

'''

s = s[:function_start] + new_function + s[function_end + len("// ─── TESTIMONIALS ────────────────────────────────────────────────────────────\n\n"):]

page.write_text(s, encoding="utf-8")

print("BUSINESS_PRICING_PACKAGES_UPDATED")
print("Backup:", backup)