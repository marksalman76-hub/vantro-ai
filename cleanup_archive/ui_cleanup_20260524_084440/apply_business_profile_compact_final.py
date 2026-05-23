
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_compact_business_profile_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

marker = "Business profile intelligence"
a = text.find(marker)
start = text.rfind("        <section", 0, a)
end = text.find("\n\n        <section", a)

if a == -1 or start == -1 or end == -1:
    raise SystemExit("BUSINESS_PROFILE_SECTION_NOT_FOUND")

replacement = r'''        <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>
            <div>
              <div style={{ color: "var(--color-brand)", fontSize: 11.5, fontWeight: 850, letterSpacing: 1.4, textTransform: "uppercase", marginBottom: 7 }}>
                Business profile intelligence ✨
              </div>
              <h2 style={{ margin: 0, fontSize: 25, letterSpacing: -0.8 }}>
                Business context for tailored AI execution
              </h2>
              <p style={{ marginTop: 9, color: "var(--color-muted)", maxWidth: 760, lineHeight: 1.5 }}>
                Add business context once so every active AI agent can produce more accurate deliverables, assets, copy, positioning, and execution recommendations.
              </p>
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <div style={{ background: "rgba(238,242,255,.95)", color: "var(--color-brand)", padding: "9px 13px", borderRadius: 14, fontWeight: 850, fontSize: 12 }}>
                ● {businessProfileSaved ? "Saved" : "Not saved yet"}
              </div>
              <button type="button" onClick={() => setToastMessage("Add business details, save the profile, then future AI executions will use this context.")} style={{ border: "1px solid rgba(79,70,229,.18)", background: "#fff", color: "#334155", padding: "9px 13px", borderRadius: 14, fontWeight: 850, fontSize: 12, cursor: "pointer" }}>
                ? How it works
              </button>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: 12 }}>
            {[
              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "normal"],
              ["products_services", "◇", "Products & services", "Main products, bundles, offers", "normal"],
              ["target_audience", "♙", "Target audience", "Customer type, location, needs", "normal"],
              ["competitors", "♕", "Competitors", "Competitor names, websites, market examples", "normal"],
              ["offers", "⌑", "Offers", "Current promotions, bundles, guarantees", "normal"],
              ["brand_voice", "◁", "Brand voice", "Premium, playful, clinical, bold, friendly", "normal"],
              ["positioning", "◎", "Positioning", "Why customers should choose you", "normal"],
              ["goals", "⚑", "Goals", "Sales, launches, retention, growth", "normal"],
              ["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "wide"],
            ].map(([key, icon, label, value, size]) => (
              <label key={label} style={{ gridColumn: size === "wide" ? "span 2" : "span 1", borderRadius: 16, border: "1px solid rgba(15,23,42,.08)", background: "#fff", padding: 13, minHeight: 104, boxShadow: "0 14px 38px rgba(15,23,42,.04)", boxSizing: "border-box" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 9 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 10, display: "grid", placeItems: "center", background: "rgba(238,242,255,.95)", color: "#4f46e5", fontWeight: 900, fontSize: 13, border: "1px solid rgba(79,70,229,.12)" }}>{icon}</div>
                  <div style={{ color: "#0f172a", fontSize: 12.5, fontWeight: 900 }}>
                    {label}{label === "Key differentiators" ? <span style={{ color: "#64748b", fontWeight: 700 }}> (optional)</span> : null}
                  </div>
                </div>
                <textarea placeholder={String(value)} value={businessProfile[String(key)] || ""} onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))} rows={2} style={{ width: "100%", resize: "none", border: 0, background: "transparent", padding: 0, fontSize: 12.2, lineHeight: 1.38, color: "var(--color-dark)", outline: "none", boxSizing: "border-box", fontFamily: "inherit" }} />
              </label>
            ))}
          </div>

          <div style={{ marginTop: 14, borderRadius: 16, border: "1px solid rgba(79,70,229,.10)", background: "#fff", padding: 10, boxShadow: "0 10px 28px rgba(15,23,42,.04)" }}>
            <div style={{ display: "grid", gridTemplateColumns: "180px 180px 180px 1fr", gap: 10, alignItems: "center" }}>
              <button type="button" onClick={saveBusinessProfile} style={{ border: 0, borderRadius: 12, padding: "10px 12px", height: 44, background: "linear-gradient(135deg,#4f46e5,#4338ca)", color: "#fff", fontSize: 12.4, fontWeight: 900, cursor: "pointer" }}>▣ Save business profile</button>
              <button type="button" onClick={loadBusinessProfile} style={{ border: "1px solid rgba(79,70,229,.18)", borderRadius: 12, padding: "10px 12px", height: 44, background: "#fff", color: "#4f46e5", fontSize: 12.4, fontWeight: 900, cursor: "pointer" }}>↻ Reset to last save</button>
              <button type="button" onClick={() => setToastMessage("Preview will show how agents use this profile in the next workspace pass.")} style={{ border: "1px solid rgba(79,70,229,.18)", borderRadius: 12, padding: "10px 12px", height: 44, background: "#fff", color: "#4f46e5", fontSize: 12.4, fontWeight: 900, cursor: "pointer" }}>◉ Preview profile</button>
              <div style={{ borderLeft: "1px solid rgba(79,70,229,.12)", paddingLeft: 14, minHeight: 44, display: "flex", flexDirection: "column", justifyContent: "center" }}>
                <div style={{ fontWeight: 900, color: "#0f172a", fontSize: 12.5, marginBottom: 2 }}>One workspace. One business.</div>
                <div style={{ color: "#64748b", fontSize: 11.4, lineHeight: 1.3 }}>You can refine this profile, but changing business identity requires approval unless Enterprise multi-business access is enabled.</div>
                <div style={{ marginTop: 2, color: businessProfileSaved ? "#16a34a" : "#4f46e5", fontSize: 11.4, fontWeight: 900 }}>Status: {businessProfileSaved ? "Saved" : "Not saved yet"}</div>
              </div>
            </div>
            <div style={{ marginTop: 8, borderRadius: 11, border: "1px solid rgba(79,70,229,.10)", background: "rgba(238,242,255,.50)", padding: "7px 11px", color: "#475569", fontSize: 11.7, lineHeight: 1.35, fontWeight: 700 }}>
              ✨ Pro tip: The more specific you are, the better your AI agents can create content, copy, and strategies tailored to your business.
            </div>
          </div>
        </section>'''

text = text[:start] + replacement + text[end:]
PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_COMPACT_FINAL_APPLIED")
print(f"Backup: {backup}")