from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_pd_menu_actions_logout_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

old = '''                {["Settings", "Profile", "Password reset", "2FA"].map((item) => (
                  <button key={item} style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}>
                    {item}
                  </button>
                ))}

                <button
                  onClick={() => document.documentElement.classList.toggle("dark")}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  Toggle dark / light mode
                </button>'''

new = '''                <button
                  onClick={() => {
                    window.location.hash = "settings";
                    alert("Settings panel selected.");
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  ⚙️ Settings
                </button>

                <button
                  onClick={() => {
                    window.location.hash = "profile";
                    alert("Profile panel selected.");
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  👤 Profile
                </button>

                <button
                  onClick={() => {
                    window.location.hash = "password-reset";
                    alert("Password reset selected.");
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  🔐 Password reset
                </button>

                <button
                  onClick={() => {
                    window.location.hash = "two-factor-authentication";
                    alert("2FA selected.");
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  🛡️ 2FA
                </button>

                <button
                  onClick={() => document.documentElement.classList.toggle("dark")}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  🌙 Toggle dark / light mode
                </button>

                <button
                  onClick={async () => {
                    try {
                      await fetch("/api/logout", { method: "POST" });
                    } finally {
                      window.location.href = "/login";
                    }
                  }}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "#ef4444" }}
                >
                  🚪 Logout
                </button>'''

if old not in text:
    raise RuntimeError("PD menu block not found. No changes written.")

text = text.replace(old, new, 1)
PAGE.write_text(text, encoding="utf-8")

print("PD_MENU_ACTIONS_LOGOUT_FIXED")
print(f"Backup: {backup}")