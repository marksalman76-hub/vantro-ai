from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_header_menu_final_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

old = '''<div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button
              style={{
                border: "none",
                borderRadius: 12,
                padding: "12px 16px",
                background: "var(--color-dark)",
                color: "#fff",
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#fff",
                borderRadius: 16,
                padding: "12px 16px",
                border: "1px solid #e5eaf2",
                fontWeight: 700,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
              }}
            >
              <span style={{ color: "var(--color-brand)", marginRight: 8 }}>●</span>
              {accountStatus}
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 44,
                height: 44,
                borderRadius: 16,
                border: "1px solid #e5eaf2",
                background: "#fff",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              🔔
              <span
                style={{
                  position: "absolute",
                  top: 7,
                  right: 8,
                  width: 8,
                  height: 8,
                  borderRadius: 16,
                  background: "var(--color-brand)",
                  border: "2px solid #fff",
                }}
              />
            </button>

            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 16,
                background: "var(--color-dark)",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 760,
              }}
            >
              PD
            </div>
          </div>'''

new = '''<div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", justifyContent: "flex-end", position: "relative" }}>
            <button
              style={{
                border: "none",
                borderRadius: 12,
                padding: "12px 16px",
                background: "var(--color-dark)",
                color: "#fff",
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#fff",
                borderRadius: 16,
                padding: "12px 16px",
                border: "1px solid #e5eaf2",
                fontWeight: 800,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                textTransform: "uppercase",
              }}
            >
              <span
                style={{
                  color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444",
                  marginRight: 8,
                }}
              >
                ●
              </span>
              {accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "ACTIVE" : "INACTIVE"}
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 44,
                height: 44,
                borderRadius: 16,
                border: "1px solid #e5eaf2",
                background: "#fff",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              🔔
              <span
                style={{
                  position: "absolute",
                  top: 7,
                  right: 8,
                  width: 8,
                  height: 8,
                  borderRadius: 16,
                  background: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444",
                  border: "2px solid #fff",
                }}
              />
            </button>

            <details style={{ position: "relative" }}>
              <summary
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 16,
                  background: "var(--color-dark)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 760,
                  cursor: "pointer",
                  listStyle: "none",
                }}
              >
                PD
              </summary>

              <div
                style={{
                  position: "absolute",
                  right: 0,
                  top: 54,
                  width: 280,
                  background: "#fff",
                  border: "1px solid #e5eaf2",
                  borderRadius: 18,
                  boxShadow: "0 24px 60px rgba(15,23,42,.18)",
                  padding: 14,
                  zIndex: 50,
                }}
              >
                <div style={{ display: "flex", gap: 12, alignItems: "center", paddingBottom: 12, borderBottom: "1px solid #edf1f6" }}>
                  <div style={{ width: 46, height: 46, borderRadius: 999, background: "var(--color-dark)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>PD</div>
                  <div>
                    <div style={{ fontWeight: 800, color: "var(--color-dark)" }}>PD</div>
                    <div style={{ fontSize: 12, color: "var(--color-muted)" }}>pd@trance-formation.com.au</div>
                    <div style={{ fontSize: 12, fontWeight: 700, marginTop: 4, color: "var(--color-muted)" }}>
                      <span style={{ color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444", marginRight: 6 }}>●</span>
                      {accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "ACTIVE" : "INACTIVE"} · Paid plan
                    </div>
                  </div>
                </div>

                {["Settings", "Profile", "Password reset", "2FA"].map((item) => (
                  <button key={item} style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}>
                    {item}
                  </button>
                ))}

                <button
                  onClick={() => document.documentElement.classList.toggle("dark")}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  Toggle dark / light mode
                </button>
              </div>
            </details>
          </div>'''

if old not in text:
    raise RuntimeError("Exact header block not found. No changes written.")

text = text.replace(old, new, 1)

text = text.replace(
'''background: label === "Approvals" ? "#f59e0b" : "var(--color-brand)",
                  boxShadow:
                    label === "Approvals"
                      ? "0 0 0 5px rgba(245,158,11,.10)"
                      : "0 0 0 5px rgba(37,99,235,.08)",''',
'''background:
                    label === "Approvals"
                      ? "#f59e0b"
                      : label === "Workspace status"
                        ? accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing"
                          ? "#22c55e"
                          : "#ef4444"
                        : "var(--color-brand)",
                  boxShadow:
                    label === "Approvals"
                      ? "0 0 0 5px rgba(245,158,11,.10)"
                      : label === "Workspace status"
                        ? accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing"
                          ? "0 0 0 5px rgba(34,197,94,.12)"
                          : "0 0 0 5px rgba(239,68,68,.12)"
                        : "0 0 0 5px rgba(37,99,235,.08)",''',
1
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_HEADER_ACCOUNT_MENU_FINAL_INSTALLED")
print(f"Backup: {backup}")