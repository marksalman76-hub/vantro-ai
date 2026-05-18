from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step267j_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

if "BUSINESS PROFILE INTELLIGENCE" in text:
    print("Business profile panel already exists. No changes applied.")
    raise SystemExit(0)

panel = '''
            <div style={{ marginTop: 22 }}>
              <div
                style={{
                  color: "#38bdf8",
                  fontSize: 13,
                  fontWeight: 800,
                  letterSpacing: 1,
                  marginBottom: 12,
                }}
              >
                BUSINESS PROFILE INTELLIGENCE
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 12,
                }}
              >
                {[
                  ["Business niche", "niche"],
                  ["Products & services", "products_services"],
                  ["Target audience", "target_audience"],
                  ["Competitors", "competitors"],
                  ["Offers", "offers"],
                  ["Brand voice", "brand_voice"],
                ].map(([label, key]) => (
                  <div key={key}>
                    <div
                      style={{
                        fontSize: 12,
                        color: "#94a3b8",
                        marginBottom: 6,
                      }}
                    >
                      {label}
                    </div>

                    <textarea
                      value={(businessProfile as any)[key]}
                      onChange={(event) =>
                        setBusinessProfile({
                          ...businessProfile,
                          [key]: event.target.value,
                        })
                      }
                      rows={3}
                      placeholder={label}
                      style={{
                        width: "100%",
                        padding: 12,
                        borderRadius: 14,
                        border: "1px solid rgba(148,163,184,.18)",
                        background: "#020617",
                        color: "#fff",
                        resize: "vertical",
                        fontSize: 13,
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
'''

marker = '''
            <div style={{ marginTop: 18 }}>
              <div
                style={{
                  color: "#94a3b8",
                  fontSize: 13,
                  marginBottom: 8,
                }}
              >
                Task
              </div>
'''

if marker not in text:
    raise SystemExit("ERROR: Could not find Task section marker.")

text = text.replace(marker, panel + "\n" + marker)

PAGE.write_text(text, encoding="utf-8")

print("STEP_267J_SAFE_INTEGRATED_BUSINESS_PROFILE_INSTALLED")
print(f"Backup: {backup}")
print("STEP_267J_OK")