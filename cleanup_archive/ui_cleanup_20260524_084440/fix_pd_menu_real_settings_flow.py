from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pd_real_settings_flow_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

# Add account panel state beside existing client state area.
marker = '  const activeAgentCount = account?.active_agents?.length || 0;'
if marker not in text:
    raise RuntimeError("Could not find activeAgentCount marker.")

if 'const [activeAccountPanel, setActiveAccountPanel]' not in text:
    text = text.replace(
        marker,
        marker + '\n  const [activeAccountPanel, setActiveAccountPanel] = useState("");',
        1,
    )

# Replace alert-based menu actions with real panel actions.
replacements = {
'''window.location.hash = "settings";
                    alert("Settings panel selected.");''':
'''setActiveAccountPanel("settings");
                    window.location.hash = "settings";''',

'''window.location.hash = "profile";
                    alert("Profile panel selected.");''':
'''setActiveAccountPanel("profile");
                    window.location.hash = "profile";''',

'''window.location.hash = "password-reset";
                    alert("Password reset selected.");''':
'''setActiveAccountPanel("password-reset");
                    window.location.hash = "password-reset";''',

'''window.location.hash = "two-factor-authentication";
                    alert("2FA selected.");''':
'''setActiveAccountPanel("two-factor-authentication");
                    window.location.hash = "two-factor-authentication";''',
}

for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new, 1)

# Add real settings panel before the locked Business Profile card.
business_marker = '''        <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>'''

panel = '''        {activeAccountPanel ? (
          <section
            id={activeAccountPanel}
            style={{
              ...cardStyle,
              padding: 18,
              marginBottom: 18,
              border: "1px solid #e5eaf2",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 12, fontWeight: 800, letterSpacing: .6, textTransform: "uppercase", marginBottom: 8 }}>
                  Account settings
                </div>
                <h2 style={{ margin: 0, color: "var(--color-dark)", fontSize: 24, letterSpacing: -.6 }}>
                  {activeAccountPanel === "settings" && "Settings"}
                  {activeAccountPanel === "profile" && "Profile"}
                  {activeAccountPanel === "password-reset" && "Password reset"}
                  {activeAccountPanel === "two-factor-authentication" && "Two-factor authentication"}
                </h2>
                <p style={{ margin: "8px 0 0", color: "var(--color-muted)", maxWidth: 720, lineHeight: 1.5 }}>
                  {activeAccountPanel === "settings" && "Manage workspace preferences, display options, and account controls."}
                  {activeAccountPanel === "profile" && "Review the client profile details connected to this workspace."}
                  {activeAccountPanel === "password-reset" && "Start a secure password reset flow for this account."}
                  {activeAccountPanel === "two-factor-authentication" && "Prepare stronger login protection for this workspace."}
                </p>
              </div>

              <button
                onClick={() => {
                  setActiveAccountPanel("");
                  window.location.hash = "";
                }}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  borderRadius: 999,
                  padding: "9px 13px",
                  fontWeight: 800,
                  cursor: "pointer",
                  color: "var(--color-dark)",
                }}
              >
                Close
              </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12, marginTop: 16 }}>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 14, padding: 14, background: "#fff" }}>
                <strong style={{ color: "var(--color-dark)" }}>Client</strong>
                <div style={{ marginTop: 6, color: "var(--color-muted)", fontSize: 13 }}>{clientDisplayName}</div>
              </div>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 14, padding: 14, background: "#fff" }}>
                <strong style={{ color: "var(--color-dark)" }}>Package</strong>
                <div style={{ marginTop: 6, color: "var(--color-muted)", fontSize: 13 }}>{accountPackage}</div>
              </div>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 14, padding: 14, background: "#fff" }}>
                <strong style={{ color: "var(--color-dark)" }}>Status</strong>
                <div style={{ marginTop: 6, color: "var(--color-muted)", fontSize: 13 }}>{accountStatus}</div>
              </div>
            </div>
          </section>
        ) : null}

''' + business_marker

if business_marker not in text:
    raise RuntimeError("Business Profile section marker not found. No changes written.")

text = text.replace(business_marker, panel, 1)

PAGE.write_text(text, encoding="utf-8")

print("PD_MENU_REAL_SETTINGS_FLOW_FIXED")
print(f"Backup: {backup}")