from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step286_minimal_header_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''          <div
            style={{
              background: "white",
              borderRadius: 999,
              padding: "18px 28px",
              boxShadow: "0 8px 30px rgba(15,23,42,.06)",
              border: "1px solid rgba(226,232,240,.9)",
              fontWeight: 700,
              fontSize: 14.5,
            }}
          >
            ● Local workspace
          </div>'''

new = '''          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              justifyContent: "flex-end",
            }}
          >
            <button
              style={{
                border: "none",
                borderRadius: 14,
                padding: "11px 16px",
                background: "#0f172a",
                color: "#ffffff",
                fontWeight: 800,
                fontSize: 13,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#ffffff",
                borderRadius: 999,
                padding: "11px 16px",
                border: "1px solid rgba(226,232,240,.9)",
                fontWeight: 700,
                fontSize: 13,
                color: "#0f172a",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
              }}
            >
              <span style={{ color: "#2563eb", marginRight: 8 }}>●</span>
              Local workspace
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 42,
                height: 42,
                borderRadius: 999,
                border: "1px solid rgba(226,232,240,.9)",
                background: "#ffffff",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                fontSize: 16,
                position: "relative",
              }}
            >
              🔔
              <span
                style={{
                  position: "absolute",
                  top: 6,
                  right: 7,
                  width: 8,
                  height: 8,
                  borderRadius: 999,
                  background: "#2563eb",
                  border: "2px solid #ffffff",
                }}
              />
            </button>

            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: 999,
                background: "#ffffff",
                border: "1px solid rgba(226,232,240,.9)",
                color: "#0f172a",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
              }}
            >
              PD
            </div>
          </div>'''

if old not in text:
    raise SystemExit("ERROR: Current header block not found. Do not continue.")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_286_MINIMAL_HEADER_UTILITY_INSTALLED")
print(f"Backup: {backup}")
print("STEP_286_OK")