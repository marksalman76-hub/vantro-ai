from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_payment_update_option_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

old = '''["settings", "profile", "password-reset", "two-factor-authentication"].includes(hash)'''
new = '''["settings", "profile", "payment-update", "password-reset", "two-factor-authentication"].includes(hash)'''
if old not in s:
    raise SystemExit("FAILED: hash panel list marker not found")
s = s.replace(old, new, 1)

old = '''activeAccountPanel === "settings" ? "Settings" : activeAccountPanel === "profile" ? "Profile" : activeAccountPanel === "password-reset" ? "Password reset" : "Two-factor authentication"'''
new = '''activeAccountPanel === "settings" ? "Settings" : activeAccountPanel === "profile" ? "Profile" : activeAccountPanel === "payment-update" ? "Payment update" : activeAccountPanel === "password-reset" ? "Password reset" : "Two-factor authentication"'''
if old not in s:
    raise SystemExit("FAILED: account centre title marker not found")
s = s.replace(old, new, 1)

insert_after = '''                <button
                  onClick={() => {
                    setActiveAccountPanel("profile");
                    window.location.hash = "profile";
                    window.setTimeout(() => {
                      document.getElementById("account-centre-profile-panel")?.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                      });
                    }, 50);
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: darkModeEnabled ? "#e2e8f0" : "var(--color-dark)" }}
                >
                  👤 Profile
                </button>
'''

payment_button = '''
                <button
                  onClick={() => {
                    setActiveAccountPanel("payment-update");
                    window.location.hash = "payment-update";
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: darkModeEnabled ? "#e2e8f0" : "var(--color-dark)" }}
                >
                  💳 Update payment
                </button>
'''

if insert_after not in s:
    raise SystemExit("FAILED: profile dropdown button marker not found")
s = s.replace(insert_after, insert_after + payment_button, 1)

insert_before = '''              {activeAccountPanel === "password-reset" ? ('''

payment_panel = '''              {activeAccountPanel === "payment-update" ? (
                <>
                  <div style={{
                    border: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid #edf1f6",
                    borderRadius: 16,
                    padding: 14,
                    background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                    boxShadow: darkModeEnabled ? "0 16px 42px rgba(0,0,0,.24)" : "none",
                  }}>
                    <div style={{ fontSize: 11, color: darkModeEnabled ? "#a5b4fc" : "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Billing</div>
                    <div style={{ marginTop: 6, color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)", fontWeight: 900 }}>Payment method</div>
                    <p style={{ color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12, lineHeight: 1.45 }}>
                      Update card, billing details, invoices, and subscription payment settings.
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        window.location.href = "/client/billing";
                      }}
                      style={{ border: 0, background: "linear-gradient(135deg,#4f46e5,#7c3aed)", color: "#fff", borderRadius: 12, padding: "8px 10px", fontWeight: 850, cursor: "pointer" }}
                    >
                      Open billing centre
                    </button>
                  </div>

                  <div style={{
                    border: darkModeEnabled ? "1px solid rgba(129,140,248,.24)" : "1px solid #edf1f6",
                    borderRadius: 16,
                    padding: 14,
                    background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                    boxShadow: darkModeEnabled ? "0 16px 42px rgba(0,0,0,.24)" : "none",
                  }}>
                    <div style={{ fontSize: 11, color: darkModeEnabled ? "#a5b4fc" : "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Subscription</div>
                    <div style={{ marginTop: 6, color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)", fontWeight: 900 }}>{accountPackage}</div>
                    <div style={{ marginTop: 5, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12 }}>Status: {accountStatus}</div>
                    <div style={{ marginTop: 5, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 12 }}>Credits: {creditsRemaining} available</div>
                  </div>
                </>
              ) : null}

'''

if insert_before not in s:
    raise SystemExit("FAILED: password reset panel marker not found")
s = s.replace(insert_before, payment_panel + insert_before, 1)

TARGET.write_text(s, encoding="utf-8")

print("PROFILE_PAYMENT_UPDATE_OPTION_ADDED")
print(f"Backup: {backup}")