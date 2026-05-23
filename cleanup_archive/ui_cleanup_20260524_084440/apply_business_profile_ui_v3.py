from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_business_profile_ui_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

marker = "Business profile intelligence"
marker_pos = text.find(marker)
if marker_pos == -1:
    raise SystemExit("BUSINESS_PROFILE_MARKER_NOT_FOUND")

section_start = text.rfind("        <section", 0, marker_pos)
if section_start == -1:
    raise SystemExit("BUSINESS_PROFILE_SECTION_START_NOT_FOUND")

section_end = text.find("\n\n        <section", marker_pos)
if section_end == -1:
    raise SystemExit("BUSINESS_PROFILE_SECTION_END_NOT_FOUND")

replacement = r'''        <section
          style={{
            ...cardStyle,
            padding: 22,
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 16,
              alignItems: "flex-start",
              marginBottom: 22,
              flexWrap: "wrap",
            }}
          >
            <div>
              <div
                style={{
                  color: "var(--color-brand)",
                  fontSize: 11.8,
                  fontWeight: 800,
                  letterSpacing: 1.4,
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                Business profile intelligence ✨
              </div>

              <h2 style={{ margin: 0, fontSize: 28, letterSpacing: -0.9 }}>
                Business context for tailored AI execution
              </h2>

              <p style={{ marginTop: 10, color: "var(--color-muted)", maxWidth: 760, lineHeight: 1.55 }}>
                Add business context once so every active AI agent can produce more accurate
                deliverables, assets, copy, positioning, and execution recommendations.
              </p>
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <div
                style={{
                  background: "rgba(238, 242, 255, 0.95)",
                  color: "var(--color-brand)",
                  padding: "10px 14px",
                  borderRadius: 16,
                  fontWeight: 800,
                  fontSize: 12,
                }}
              >
                ● {businessProfileSaved ? "Saved" : "Not saved yet"}
              </div>

              <button
                type="button"
                onClick={() => setToastMessage("Add business details, save the profile, then future AI executions will use this context.")}
                style={{
                  border: "1px solid rgba(79,70,229,0.18)",
                  background: "#ffffff",
                  color: "#334155",
                  padding: "10px 14px",
                  borderRadius: 16,
                  fontWeight: 800,
                  fontSize: 12,
                  cursor: "pointer",
                }}
              >
                ? How it works
              </button>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, minmax(150px, 1fr))",
              gap: 14,
            }}
          >
            {[
              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "1 / span 1"],
              ["products_services", "◇", "Products & services", "Main products, bundles, offers", "1 / span 1"],
              ["target_audience", "♙", "Target audience", "Customer type, location, needs", "1 / span 1"],
              ["competitors", "♕", "Competitors", "Competitor names, websites, market examples", "1 / span 1"],
              ["offers", "⌑", "Offers", "Current promotions, bundles, guarantees", "1 / span 1"],
              ["brand_voice", "◁", "Brand voice", "Premium, playful, clinical, bold, friendly", "1 / span 1"],
              ["positioning", "◎", "Positioning", "Why customers should choose you", "1 / span 1"],
              ["goals", "⚑", "Goals", "Sales, launches, retention, growth", "1 / span 1"],
              ["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "4 / span 2"],
            ].map(([key, icon, label, value, span]) => (
              <label
                key={label}
                style={{
                  gridColumn: String(span),
                  borderRadius: 18,
                  border: "1px solid rgba(15, 23, 42, 0.08)",
                  background: "#ffffff",
                  padding: 14,
                  minHeight: 132,
                  boxShadow: "0 16px 45px rgba(15, 23, 42, 0.045)",
                  boxSizing: "border-box",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                  <div
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: 12,
                      display: "grid",
                      placeItems: "center",
                      background: "rgba(238, 242, 255, 0.95)",
                      color: "#4f46e5",
                      fontWeight: 900,
                      fontSize: 16,
                      border: "1px solid rgba(79,70,229,0.12)",
                    }}
                  >
                    {icon}
                  </div>
                  <div style={{ color: "#0f172a", fontSize: 13, fontWeight: 900 }}>
                    {label}
                    {label === "Key differentiators" ? (
                      <span style={{ color: "#64748b", fontWeight: 700 }}> (optional)</span>
                    ) : null}
                  </div>
                </div>

                <textarea
                  placeholder={String(value)}
                  value={businessProfile[String(key)] || ""}
                  onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))}
                  rows={3}
                  style={{
                    width: "100%",
                    resize: "none",
                    border: 0,
                    background: "transparent",
                    padding: 0,
                    fontSize: 13,
                    lineHeight: 1.45,
                    color: "var(--color-dark)",
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />
              </label>
            ))}
          </div>

          <div
            style={{
              marginTop: 16,
              borderRadius: 18,
              border: "1px solid rgba(79,70,229,0.10)",
              background: "#ffffff",
              padding: 12,
              boxShadow: "0 10px 30px rgba(15,23,42,0.04)",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr 1.25fr",
                gap: 10,
                alignItems: "stretch",
              }}
            >
              <button
                type="button"
                onClick={saveBusinessProfile}
                style={{
                  border: 0,
                  borderRadius: 14,
                  padding: "12px 14px",
                  minHeight: 56,
                  background: "linear-gradient(135deg, #4f46e5, #4338ca)",
                  color: "#ffffff",
                  fontSize: 13,
                  fontWeight: 900,
                  cursor: "pointer",
                  boxShadow: "0 12px 32px rgba(79,70,229,0.20)",
                }}
              >
                ▣ Save business profile
              </button>

              <button
                type="button"
                onClick={loadBusinessProfile}
                style={{
                  border: "1px solid rgba(79,70,229,0.18)",
                  borderRadius: 14,
                  padding: "12px 14px",
                  minHeight: 56,
                  background: "#ffffff",
                  color: "#4f46e5",
                  fontSize: 13,
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                ↻ Reset to last save
              </button>

              <button
                type="button"
                onClick={() => setToastMessage("Preview will show how agents use this profile in the next workspace pass.")}
                style={{
                  border: "1px solid rgba(79,70,229,0.18)",
                  borderRadius: 14,
                  padding: "12px 14px",
                  minHeight: 56,
                  background: "#ffffff",
                  color: "#4f46e5",
                  fontSize: 13,
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                ◉ Preview profile
              </button>

              <div
                style={{
                  borderLeft: "1px solid rgba(79,70,229,0.14)",
                  padding: "4px 4px 4px 16px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                }}
              >
                <div style={{ fontWeight: 900, color: "#0f172a", marginBottom: 4, fontSize: 13.5 }}>
                  One workspace. One business.
                </div>
                <div style={{ color: "#64748b", fontSize: 12, lineHeight: 1.42 }}>
                  You can refine this profile, but changing business identity requires approval unless Enterprise multi-business access is enabled.
                </div>
                <div style={{ marginTop: 5, color: businessProfileSaved ? "#16a34a" : "#4f46e5", fontSize: 12, fontWeight: 900 }}>
                  Status: {businessProfileSaved ? "Saved" : "Not saved yet"}
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: 10,
                borderRadius: 12,
                border: "1px solid rgba(79,70,229,0.10)",
                background: "rgba(238,242,255,0.50)",
                padding: "9px 12px",
                color: "#475569",
                fontSize: 12,
                lineHeight: 1.4,
                fontWeight: 700,
              }}
            >
              ✨ Pro tip: The more specific you are, the better your AI agents can create content, copy, and strategies tailored to your business.
            </div>
          </div>
        </section>'''

text = text[:section_start] + replacement + text[section_end:]

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_UI_V3_FULL_SECTION_APPLIED")
print(f"Backup: {backup}")