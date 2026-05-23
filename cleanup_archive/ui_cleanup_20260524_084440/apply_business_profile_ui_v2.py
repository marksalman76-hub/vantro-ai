from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_business_profile_ui_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Tighten business profile cards and textarea height
text = text.replace('rows={3}', 'rows={3}', 1)
text = text.replace('gap: 12,', 'gap: 14,', 1)

# Replace action strip with image-1-style strip
start_marker = '''          <div
            style={{
              marginTop: 18,
              borderRadius: 18,'''

end_marker = '''          </div>
        </section>


        <section'''

start = text.find(start_marker)
if start == -1:
    raise SystemExit("BUSINESS_PROFILE_ACTION_STRIP_START_NOT_FOUND")

end = text.find(end_marker, start)
if end == -1:
    raise SystemExit("BUSINESS_PROFILE_ACTION_STRIP_END_NOT_FOUND")

new_action_strip = '''          <div
            style={{
              marginTop: 18,
              borderRadius: 18,
              border: "1px solid rgba(79,70,229,0.14)",
              background: "#ffffff",
              padding: 14,
              boxShadow: "0 18px 55px rgba(15,23,42,0.05)",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "minmax(230px, 300px) minmax(190px, 1fr) minmax(190px, 1fr) minmax(280px, 1.25fr)",
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
                  minHeight: 62,
                  background: "linear-gradient(135deg, #4f46e5, #4338ca)",
                  color: "#ffffff",
                  fontSize: 14,
                  fontWeight: 900,
                  cursor: "pointer",
                  boxShadow: "0 16px 38px rgba(79,70,229,0.22)",
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
                  minHeight: 62,
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
                onClick={() => setToastMessage("Preview will show how agents use this profile in the next workspace pass.")}
                style={{
                  border: "1px solid rgba(79,70,229,0.18)",
                  borderRadius: 14,
                  padding: "14px 18px",
                  minHeight: 62,
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
                  borderLeft: "1px solid rgba(79,70,229,0.14)",
                  padding: "8px 4px 8px 18px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  minHeight: 62,
                }}
              >
                <div style={{ fontWeight: 900, color: "#0f172a", marginBottom: 5 }}>
                  One workspace. One business.
                </div>
                <div style={{ color: "#64748b", fontSize: 12.5, lineHeight: 1.45 }}>
                  You can refine this profile, but changing business identity requires owner approval unless Enterprise multi-business access is enabled.
                </div>
                <div style={{ marginTop: 6, color: businessProfileSaved ? "#16a34a" : "#4f46e5", fontSize: 12.5, fontWeight: 900 }}>
                  Status: {businessProfileSaved ? "Saved" : "Not saved yet"}
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: 10,
                borderRadius: 12,
                border: "1px solid rgba(79,70,229,0.10)",
                background: "rgba(238,242,255,0.55)",
                padding: "10px 13px",
                color: "#475569",
                fontSize: 12.5,
                lineHeight: 1.45,
                fontWeight: 700,
              }}
            >
              Pro tip: The more specific you are, the better your AI agents can create content, copy, and strategies tailored to your business.
            </div>
          </div>
        </section>


        <section'''

text = text[:start] + new_action_strip + text[end + len(end_marker):]

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_UI_V2_APPLIED")
print(f"Backup: {backup}")