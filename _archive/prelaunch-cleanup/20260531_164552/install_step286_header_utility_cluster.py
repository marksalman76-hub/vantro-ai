from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step286_header_cluster_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''          <div
            style={{
              background: "white",
              borderRadius: 999,
              padding: "18px 28px",
              boxShadow: "0 8px 30px rgba(15,23,42,.06)",
              border: "1px solid rgba(226,232,240,.9)",
              fontWeight: 700,
              fontSize: 15,
            }}
          >
            ● Local workspace
          </div>'''

new = '''          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              flexWrap: "wrap",
              justifyContent: "flex-end",
            }}
          >
            <button
              style={{
                border: "none",
                borderRadius: 999,
                padding: "13px 18px",
                background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                color: "#ffffff",
                fontWeight: 800,
                fontSize: 14,
                cursor: "pointer",
                boxShadow: "0 12px 28px rgba(37,99,235,.18)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#ffffff",
                borderRadius: 999,
                padding: "13px 18px",
                boxShadow: "0 8px 26px rgba(15,23,42,.05)",
                border: "1px solid rgba(226,232,240,.9)",
                fontWeight: 700,
                fontSize: 14,
                color: "#0f172a",
              }}
            >
              ● Local workspace
            </div>

            <div
              style={{
                background: "#ffffff",
                borderRadius: 999,
                padding: "13px 16px",
                boxShadow: "0 8px 26px rgba(15,23,42,.05)",
                border: "1px solid rgba(226,232,240,.9)",
                fontWeight: 800,
                fontSize: 14,
                color: "#0f172a",
              }}
            >
              Credits: {creditsRemaining}
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 48,
                height: 48,
                borderRadius: 999,
                border: "1px solid rgba(226,232,240,.9)",
                background: "#ffffff",
                boxShadow: "0 8px 26px rgba(15,23,42,.05)",
                cursor: "pointer",
                fontSize: 18,
                position: "relative",
              }}
            >
              🔔
              <span
                style={{
                  position: "absolute",
                  top: 7,
                  right: 7,
                  width: 9,
                  height: 9,
                  borderRadius: 999,
                  background: "#2563eb",
                  border: "2px solid #ffffff",
                }}
              />
            </button>

            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 999,
                background: "#0f172a",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                boxShadow: "0 8px 26px rgba(15,23,42,.08)",
              }}
            >
              PD
            </div>
          </div>'''

if old not in text:
    raise SystemExit("ERROR: Header Local workspace block not found.")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_286_HEADER_UTILITY_CLUSTER_INSTALLED")
print(f"Backup: {backup}")
print("STEP_286_OK")