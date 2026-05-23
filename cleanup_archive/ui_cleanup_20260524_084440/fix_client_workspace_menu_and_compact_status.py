from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_menu_status_combined_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

# 1. Add active account panel state.
state_anchor = '  const [integrationMessage, setIntegrationMessage] = useState("");'
if state_anchor not in text:
    raise RuntimeError("State anchor not found.")

if "const [activeAccountPanel, setActiveAccountPanel]" not in text:
    text = text.replace(
        state_anchor,
        state_anchor + '\n  const [activeAccountPanel, setActiveAccountPanel] = useState("");',
        1,
    )

# 2. Add business name field to Business Profile if missing.
field_anchor = '              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "normal"],'
if field_anchor not in text:
    raise RuntimeError("Business profile field anchor not found.")

if '["business_name", "◆", "Business name"' not in text:
    text = text.replace(
        field_anchor,
        '              ["business_name", "◆", "Business name", "Your company, store, or brand name", "normal"],\n' + field_anchor,
        1,
    )

# 3. Make settings menu actually open visible in-page panels.
text = text.replace(
'''window.location.hash = "settings";''',
'''setActiveAccountPanel("settings");
                    window.location.hash = "settings";''',
1,
)

text = text.replace(
'''window.location.hash = "profile";''',
'''setActiveAccountPanel("profile");
                    window.location.hash = "profile";''',
1,
)

text = text.replace(
'''window.location.hash = "password-reset";''',
'''setActiveAccountPanel("password-reset");
                    window.location.hash = "password-reset";''',
1,
)

text = text.replace(
'''window.location.hash = "two-factor-authentication";''',
'''setActiveAccountPanel("two-factor-authentication");
                    window.location.hash = "two-factor-authentication";''',
1,
)

# 4. Insert account panel before locked Business Profile section.
business_section_anchor = '''        <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>'''

if business_section_anchor not in text:
    raise RuntimeError("Business Profile section anchor not found.")

account_panel = '''        {activeAccountPanel ? (
          <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 12, fontWeight: 900, letterSpacing: .6, textTransform: "uppercase", marginBottom: 6 }}>
                  Account centre
                </div>
                <h2 style={{ margin: 0, color: "var(--color-dark)", fontSize: 22, letterSpacing: -.4 }}>
                  {activeAccountPanel === "settings" ? "Settings" : activeAccountPanel === "profile" ? "Profile" : activeAccountPanel === "password-reset" ? "Password reset" : "Two-factor authentication"}
                </h2>
                <p style={{ margin: "7px 0 0", color: "var(--color-muted)", fontSize: 13, lineHeight: 1.45 }}>
                  {activeAccountPanel === "settings" ? "Manage workspace preferences and display controls." : activeAccountPanel === "profile" ? "Review the business identity and account attached to this workspace." : activeAccountPanel === "password-reset" ? "Password reset controls will be connected to the secure account flow." : "Two-factor authentication controls will be connected to the secure login flow."}
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

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10, marginTop: 14 }}>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 14, padding: 12, background: "#fff" }}>
                <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 800, textTransform: "uppercase" }}>Client</div>
                <div style={{ marginTop: 4, color: "var(--color-dark)", fontWeight: 900 }}>{clientDisplayName}</div>
              </div>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 14, padding: 12, background: "#fff" }}>
                <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 800, textTransform: "uppercase" }}>Package</div>
                <div style={{ marginTop: 4, color: "var(--color-dark)", fontWeight: 900 }}>{accountPackage}</div>
              </div>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 14, padding: 12, background: "#fff" }}>
                <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 800, textTransform: "uppercase" }}>Status</div>
                <div style={{ marginTop: 4, color: "var(--color-dark)", fontWeight: 900 }}>{accountStatus}</div>
              </div>
            </div>
          </section>
        ) : null}

''' + business_section_anchor

if "Account centre" not in text:
    text = text.replace(business_section_anchor, account_panel, 1)

# 5. Replace status cards with smoother compact linear strip.
start = text.find('        <section\n          style={{\n            display: "grid",\n            gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))"')
end = text.find(business_section_anchor, start)

if start == -1 or end == -1:
    raise RuntimeError("Status strip block not found.")

compact_status = '''        <section
          style={{
            ...cardStyle,
            padding: "13px 16px",
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
              gap: 0,
              alignItems: "center",
            }}
          >
            {[
              ["Workspace status", accountStatus === "active" ? "Ready for execution" : accountStatus, accountPackage, accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444"],
              ["Approvals", reviewStatus === "pending" && liveDeliverable ? "1 pending" : "0 pending", liveDeliverable ? "Client review" : "No pending review", "#f59e0b"],
              ["Agents", String(activeAgentCount), activeAgentCount ? "Active in this workspace" : "No active agents", "var(--color-brand)"],
              ["Credits", String(creditsRemaining), "Available balance", "var(--color-brand)"],
            ].map(([label, value, note, dot], index) => (
              <div
                key={label}
                style={{
                  padding: "4px 22px",
                  borderLeft: index === 0 ? "none" : "1px solid #e5eaf2",
                  minHeight: 54,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--color-muted)", fontSize: 12, fontWeight: 850 }}>
                  <span style={{ width: 9, height: 9, borderRadius: 999, background: String(dot), boxShadow: "0 0 0 5px rgba(79,70,229,.08)" }} />
                  {label}
                </div>
                <div style={{ marginTop: 5, color: "var(--color-dark)", fontSize: 18, lineHeight: 1.1, fontWeight: 900 }}>
                  {value}
                </div>
                <div style={{ marginTop: 4, color: "var(--color-muted)", fontSize: 12 }}>
                  {note}
                </div>
              </div>
            ))}
          </div>
        </section>

'''

text = text[:start] + compact_status + text[end:]

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_WORKSPACE_MENU_AND_COMPACT_STATUS_FIXED")
print(f"Backup: {backup}")