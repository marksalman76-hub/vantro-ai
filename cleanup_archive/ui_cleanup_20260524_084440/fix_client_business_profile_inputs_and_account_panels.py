from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_business_profile_input_account_panel_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

account_start = text.find("        {activeAccountPanel ? (")
business_start = text.find('        <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>\n          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>')
if account_start == -1 or business_start == -1:
    raise SystemExit("Could not find account panel / business profile boundary.")

new_account_panel = r'''        {activeAccountPanel ? (
          <section style={{ ...cardStyle, padding: 18, marginBottom: 18, position: "relative", zIndex: 3 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 12, fontWeight: 900, letterSpacing: .6, textTransform: "uppercase", marginBottom: 6 }}>
                  Account centre
                </div>
                <h2 style={{ margin: 0, color: "var(--color-dark)", fontSize: 22, letterSpacing: -.4 }}>
                  {activeAccountPanel === "settings" ? "Settings" : activeAccountPanel === "profile" ? "Profile" : activeAccountPanel === "password-reset" ? "Password reset" : "Two-factor authentication"}
                </h2>
                <p style={{ margin: "7px 0 0", color: "var(--color-muted)", fontSize: 13, lineHeight: 1.45 }}>
                  Manage client account controls without leaving the workspace.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setActiveAccountPanel("");
                  window.location.hash = "";
                }}
                style={{ border: "1px solid #e5eaf2", background: "#fff", borderRadius: 999, padding: "9px 13px", fontWeight: 850, cursor: "pointer", color: "var(--color-dark)" }}
              >
                Close
              </button>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
              {[
                ["settings", "⚙️ Settings"],
                ["profile", "👤 Profile"],
                ["password-reset", "🔐 Password reset"],
                ["two-factor-authentication", "🛡️ 2FA"],
              ].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => {
                    setActiveAccountPanel(key);
                    window.location.hash = key;
                  }}
                  style={{
                    border: activeAccountPanel === key ? "1px solid rgba(79,70,229,.35)" : "1px solid #e5eaf2",
                    background: activeAccountPanel === key ? "rgba(238,242,255,.95)" : "#fff",
                    color: activeAccountPanel === key ? "#4f46e5" : "#334155",
                    borderRadius: 999,
                    padding: "9px 12px",
                    fontWeight: 850,
                    cursor: "pointer",
                    fontSize: 12,
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
              {activeAccountPanel === "settings" ? (
                <>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Theme</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Display mode</div>
                    <button
                      type="button"
                      onClick={() => document.documentElement.classList.toggle("dark")}
                      style={{ marginTop: 10, border: "1px solid rgba(79,70,229,.18)", background: "#fff", color: "#4f46e5", borderRadius: 12, padding: "9px 11px", fontWeight: 850, cursor: "pointer" }}
                    >
                      Toggle dark / light mode
                    </button>
                  </div>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Workspace</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{accountPackage}</div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>Status: {accountStatus}</div>
                  </div>
                </>
              ) : null}

              {activeAccountPanel === "profile" ? (
                <>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{clientDisplayName}</div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>{clientEmail || "No email shown"}</div>
                  </div>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Business profile</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{businessProfile.business_name || "Not saved yet"}</div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>Edit the Business Profile Intelligence section below.</div>
                  </div>
                </>
              ) : null}

              {activeAccountPanel === "password-reset" ? (
                <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                  <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Password reset</div>
                  <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Secure reset request</div>
                  <p style={{ color: "var(--color-muted)", fontSize: 12, lineHeight: 1.45 }}>Use this panel to trigger the secure password reset flow once the backend route is connected.</p>
                  <button type="button" onClick={() => setToastMessage("Password reset request panel opened. Secure email flow is ready for backend connection.")} style={{ border: 0, background: "var(--color-dark)", color: "#fff", borderRadius: 12, padding: "10px 12px", fontWeight: 850, cursor: "pointer" }}>
                    Send reset link
                  </button>
                </div>
              ) : null}

              {activeAccountPanel === "two-factor-authentication" ? (
                <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                  <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Two-factor authentication</div>
                  <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Extra account protection</div>
                  <p style={{ color: "var(--color-muted)", fontSize: 12, lineHeight: 1.45 }}>2FA setup panel is now functional in the workspace UI and ready for secure backend connection.</p>
                  <button type="button" onClick={() => setToastMessage("2FA setup panel opened. Secure setup flow is ready for backend connection.")} style={{ border: 0, background: "var(--color-dark)", color: "#fff", borderRadius: 12, padding: "10px 12px", fontWeight: 850, cursor: "pointer" }}>
                    Start 2FA setup
                  </button>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

'''

text = text[:account_start] + new_account_panel + text[business_start:]

business_start = text.find('        <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>\n          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>')
integrations_start = text.find('        <section\n          style={{\n            ...cardStyle,\n            padding: 18,\n            marginBottom: 18,\n          }}\n        >\n          <div\n            style={{\n              display: "flex",\n              alignItems: "center",\n              justifyContent: "space-between",\n              gap: 16,\n              flexWrap: "wrap",\n            }}\n          >\n            <div>\n              <div style={{ fontSize: 13, fontWeight: 800, color: "var(--color-dark)" }}>Integrations</div>')
if business_start == -1 or integrations_start == -1 or integrations_start <= business_start:
    raise SystemExit("Could not find Business Profile section / Integrations boundary.")

new_business_section = r'''        <section style={{ ...cardStyle, padding: 18, marginBottom: 18, position: "relative", zIndex: 2, overflow: "visible" }}>
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

          <div style={{ marginBottom: 12, borderRadius: 14, border: "1px solid rgba(79,70,229,.12)", background: "rgba(238,242,255,.45)", padding: "10px 12px", color: "#334155", fontSize: 12.4, fontWeight: 750 }}>
            Start with <strong>Business name</strong>. This controls the client initials and account name shown in the top-right profile menu.
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: 12, position: "relative", zIndex: 20, pointerEvents: "auto" }}>
            {[
              ["business_name", "◆", "Business name", "Type business name here", "input", "normal"],
              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "textarea", "normal"],
              ["products_services", "◇", "Products & services", "Main products, bundles, offers", "textarea", "normal"],
              ["target_audience", "♙", "Target audience", "Customer type, location, needs", "textarea", "normal"],
              ["competitors", "♕", "Competitors", "Competitor names, websites, market examples", "textarea", "normal"],
              ["offers", "⌑", "Offers", "Current promotions, bundles, guarantees", "textarea", "normal"],
              ["brand_voice", "◁", "Brand voice", "Premium, playful, clinical, bold, friendly", "textarea", "normal"],
              ["positioning", "◎", "Positioning", "Why customers should choose you", "textarea", "normal"],
              ["goals", "⚑", "Goals", "Sales, launches, retention, growth", "textarea", "normal"],
              ["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "wide"],
            ].map(([key, icon, label, placeholder, fieldType, size]) => (
              <div
                key={String(key)}
                style={{
                  gridColumn: size === "wide" ? "span 2" : "span 1",
                  borderRadius: 16,
                  border: "1px solid rgba(15,23,42,.08)",
                  background: "#fff",
                  padding: 13,
                  minHeight: 104,
                  boxShadow: "0 14px 38px rgba(15,23,42,.04)",
                  boxSizing: "border-box",
                  position: "relative",
                  zIndex: 21,
                  pointerEvents: "auto",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 9, pointerEvents: "none" }}>
                  <div style={{ width: 28, height: 28, borderRadius: 10, display: "grid", placeItems: "center", background: "rgba(238,242,255,.95)", color: "#4f46e5", fontWeight: 900, fontSize: 13, border: "1px solid rgba(79,70,229,.12)" }}>{icon}</div>
                  <div style={{ color: "#0f172a", fontSize: 12.5, fontWeight: 900 }}>
                    {label}{label === "Key differentiators" ? <span style={{ color: "#64748b", fontWeight: 700 }}> (optional)</span> : null}
                  </div>
                </div>

                {fieldType === "input" ? (
                  <input
                    type="text"
                    aria-label={String(label)}
                    placeholder={String(placeholder)}
                    value={businessProfile[String(key)] || ""}
                    onChange={(e) => {
                      const nextValue = e.target.value;
                      setBusinessProfile((prev) => ({ ...prev, [String(key)]: nextValue }));
                      setBusinessProfileSaved(false);
                    }}
                    autoComplete="organization"
                    style={{
                      width: "100%",
                      height: 42,
                      border: "1.5px solid rgba(79,70,229,.35)",
                      background: "#fff",
                      padding: "9px 11px",
                      borderRadius: 10,
                      fontSize: 13,
                      color: "#0f172a",
                      outline: "none",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      marginTop: 8,
                      cursor: "text",
                      position: "relative",
                      zIndex: 50,
                      pointerEvents: "auto",
                      userSelect: "text",
                    }}
                  />
                ) : (
                  <textarea
                    aria-label={String(label)}
                    placeholder={String(placeholder)}
                    value={businessProfile[String(key)] || ""}
                    onChange={(e) => {
                      const nextValue = e.target.value;
                      setBusinessProfile((prev) => ({ ...prev, [String(key)]: nextValue }));
                      setBusinessProfileSaved(false);
                    }}
                    rows={2}
                    style={{
                      width: "100%",
                      resize: "vertical",
                      minHeight: 52,
                      border: "1px solid rgba(79,70,229,.18)",
                      background: "#fff",
                      padding: "9px 10px",
                      borderRadius: 10,
                      fontSize: 12.4,
                      lineHeight: 1.38,
                      color: "#0f172a",
                      outline: "none",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      marginTop: 8,
                      cursor: "text",
                      position: "relative",
                      zIndex: 50,
                      pointerEvents: "auto",
                      userSelect: "text",
                    }}
                  />
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: 14, borderRadius: 16, border: "1px solid rgba(79,70,229,.10)", background: "#fff", padding: 10, boxShadow: "0 10px 28px rgba(15,23,42,.04)", position: "relative", zIndex: 25 }}>
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
        </section>

'''

text = text[:business_start] + new_business_section + text[integrations_start:]

required = [
    'pointerEvents: "auto"',
    'setBusinessProfileSaved(false)',
    'Start 2FA setup',
    'Send reset link',
    'aria-label={String(label)}',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"Missing required markers: {missing}")

path.write_text(text, encoding="utf-8")
print("CLIENT_BUSINESS_PROFILE_INPUTS_AND_ACCOUNT_PANELS_FIXED")
print(f"Backup: {backup}")