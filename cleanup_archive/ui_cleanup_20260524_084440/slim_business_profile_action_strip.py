from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_slim_business_profile_strip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace("rows={4}", "rows={3}", 1)

start_marker = '''          <div
            style={{
              marginTop: 18,
              display: "grid",
              gridTemplateColumns: "minmax(220px, 280px) 1fr",'''

end_marker = '''          </div>
        </section>


        <section'''

start = text.find(start_marker)
if start == -1:
    raise SystemExit("ACTION_STRIP_START_NOT_FOUND")

end = text.find(end_marker, start)
if end == -1:
    raise SystemExit("ACTION_STRIP_END_NOT_FOUND")

new_block = '''          <div
            style={{
              marginTop: 18,
              borderRadius: 18,
              border: "1px solid rgba(79, 70, 229, 0.12)",
              background: "linear-gradient(135deg, rgba(238,242,255,0.72), rgba(255,255,255,0.96))",
              padding: 12,
              display: "grid",
              gridTemplateColumns: "minmax(220px, 300px) minmax(180px, 1fr) minmax(180px, 1fr)",
              gap: 12,
              alignItems: "stretch",
            }}
          >
            <button
              type="button"
              onClick={saveBusinessProfile}
              style={{
                border: 0,
                borderRadius: 14,
                padding: "14px 18px",
                background: "#4f46e5",
                color: "#ffffff",
                fontSize: 14,
                fontWeight: 900,
                cursor: "pointer",
                boxShadow: "0 14px 38px rgba(79,70,229,0.22)",
              }}
            >
              Save business profile
            </button>

            <button
              type="button"
              onClick={loadBusinessProfile}
              style={{
                border: "1px solid rgba(79,70,229,0.18)",
                borderRadius: 14,
                padding: "14px 18px",
                background: "#ffffff",
                color: "#4f46e5",
                fontSize: 14,
                fontWeight: 900,
                cursor: "pointer",
              }}
            >
              Reset to last save
            </button>

            <button
              type="button"
              onClick={() => setToastMessage("Preview will show how agents use this business profile in the next workspace pass.")}
              style={{
                border: "1px solid rgba(79,70,229,0.18)",
                borderRadius: 14,
                padding: "14px 18px",
                background: "#ffffff",
                color: "#4f46e5",
                fontSize: 14,
                fontWeight: 900,
                cursor: "pointer",
              }}
            >
              Preview profile
            </button>

            <div
              style={{
                gridColumn: "1 / -1",
                display: "flex",
                gap: 12,
                alignItems: "center",
                justifyContent: "space-between",
                padding: "8px 4px 0",
                color: "#64748b",
                fontSize: 12.5,
                fontWeight: 700,
              }}
            >
              <span>
                One workspace. One business. You can refine this profile, but changing business identity requires approval unless Enterprise multi-business access is enabled.
              </span>
              <span style={{ color: businessProfileSaved ? "#16a34a" : "#4f46e5", whiteSpace: "nowrap" }}>
                {businessProfileSaved ? "Saved" : "Not saved yet"}
              </span>
            </div>
          </div>
        </section>


        <section'''

text = text[:start] + new_block + text[end + len(end_marker):]

PAGE.write_text(text, encoding="utf-8")

print("SLIM_BUSINESS_PROFILE_ACTION_STRIP_INSTALLED")
print(f"Backup: {backup}")