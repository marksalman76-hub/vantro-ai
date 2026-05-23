from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_editable_profile_settings_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

# 1. Ensure account panel state exists.
state_anchor = '  const [integrationMessage, setIntegrationMessage] = useState("");'
if state_anchor not in text:
    raise RuntimeError("State anchor not found.")

if 'const [activeAccountPanel, setActiveAccountPanel] = useState("");' not in text:
    text = text.replace(
        state_anchor,
        state_anchor + '\n  const [activeAccountPanel, setActiveAccountPanel] = useState("");',
        1,
    )

# 2. Ensure URL hash opens real account panel on refresh/direct hash.
hash_effect = '''  useEffect(() => {
    const syncAccountPanelFromHash = () => {
      const hash = window.location.hash.replace("#", "");
      if (["settings", "profile", "password-reset", "two-factor-authentication"].includes(hash)) {
        setActiveAccountPanel(hash);
      }
    };

    syncAccountPanelFromHash();
    window.addEventListener("hashchange", syncAccountPanelFromHash);
    return () => window.removeEventListener("hashchange", syncAccountPanelFromHash);
  }, []);

'''

if "syncAccountPanelFromHash" not in text:
    insert_after = '  }, []);\n\n  const creditsRemaining = account?.credits_remaining ?? 0;'
    if insert_after not in text:
        raise RuntimeError("Could not find first useEffect end marker.")
    text = text.replace(insert_after, '  }, []);\n\n' + hash_effect + '  const creditsRemaining = account?.credits_remaining ?? 0;', 1)

# 3. Ensure menu clicks update state as well as hash.
menu_replacements = {
'''window.location.hash = "settings";''': '''setActiveAccountPanel("settings");
                    window.location.hash = "settings";''',
'''window.location.hash = "profile";''': '''setActiveAccountPanel("profile");
                    window.location.hash = "profile";''',
'''window.location.hash = "password-reset";''': '''setActiveAccountPanel("password-reset");
                    window.location.hash = "password-reset";''',
'''window.location.hash = "two-factor-authentication";''': '''setActiveAccountPanel("two-factor-authentication");
                    window.location.hash = "two-factor-authentication";''',
}

for old, new in menu_replacements.items():
    if old in text and new not in text:
        text = text.replace(old, new, 1)

# 4. Make Business Profile cards visibly editable.
old_textarea = '''<textarea placeholder={String(value)} value={businessProfile[String(key)] || ""} onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))} rows={2} style={{ width: "100%", resize: "none", border: 0, background: "transparent", padding: 0, fontSize: 12.2, lineHeight: 1.38, color: "var(--color-dark)", outline: "none", boxSizing: "border-box", fontFamily: "inherit" }} />'''

new_textarea = '''<textarea
                  placeholder={String(value)}
                  value={businessProfile[String(key)] || ""}
                  onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))}
                  rows={String(key) === "business_name" ? 1 : 2}
                  style={{
                    width: "100%",
                    resize: "vertical",
                    minHeight: String(key) === "business_name" ? 38 : 52,
                    border: "1px solid rgba(79,70,229,.14)",
                    background: "#fff",
                    padding: "9px 10px",
                    borderRadius: 10,
                    fontSize: 12.4,
                    lineHeight: 1.38,
                    color: "var(--color-dark)",
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                    marginTop: 8,
                  }}
                />'''

if old_textarea not in text:
    raise RuntimeError("Business Profile textarea block not found.")

text = text.replace(old_textarea, new_textarea, 1)

# 5. Add account panel if missing.
business_section_anchor = '''        <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>'''

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
                  {activeAccountPanel === "settings" ? "Manage workspace preferences and display controls." : activeAccountPanel === "profile" ? "Review the business identity and account attached to this workspace." : activeAccountPanel === "password-reset" ? "Password reset controls will connect to the secure account flow." : "Two-factor authentication controls will connect to the secure login flow."}
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
    if business_section_anchor not in text:
        raise RuntimeError("Business Profile anchor not found.")
    text = text.replace(business_section_anchor, account_panel, 1)

PAGE.write_text(text, encoding="utf-8")

print("EDITABLE_BUSINESS_PROFILE_AND_SETTINGS_FLOW_FIXED")
print(f"Backup: {backup}")