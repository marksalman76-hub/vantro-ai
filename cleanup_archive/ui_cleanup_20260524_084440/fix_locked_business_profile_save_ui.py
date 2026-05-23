from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_locked_business_profile_ui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Remove any previous profile save button block to prevent duplicates.
text = re.sub(
    r'\s*<button\s+type="button"\s+onClick=\{saveBusinessProfile\}[\s\S]*?</button>',
    '',
    text,
    count=3
)

# Restore useful placeholder wording inside fields.
text = text.replace(
    '<textarea\n                  value={businessProfile[String(key)] || ""}',
    '<textarea\n                  placeholder={String(value)}\n                  value={businessProfile[String(key)] || ""}'
)

# Insert locked-business save panel directly after business profile grid.
target = '''            ))}
          </div>'''

insert = '''            ))}
          </div>

          <div
            style={{
              marginTop: 18,
              display: "grid",
              gridTemplateColumns: "minmax(220px, 280px) 1fr",
              gap: 16,
              alignItems: "stretch",
            }}
          >
            <button
              type="button"
              onClick={saveBusinessProfile}
              style={{
                border: 0,
                borderRadius: 18,
                padding: "18px 22px",
                background: "#4f46e5",
                color: "#ffffff",
                fontSize: 15,
                fontWeight: 900,
                cursor: "pointer",
                boxShadow: "0 18px 50px rgba(79,70,229,0.22)",
              }}
            >
              Save business profile
            </button>

            <div
              style={{
                borderRadius: 18,
                border: "1px solid rgba(15, 23, 42, 0.08)",
                background: "#ffffff",
                padding: "16px 18px",
                boxShadow: "0 18px 55px rgba(15, 23, 42, 0.06)",
              }}
            >
              <div style={{ fontWeight: 900, color: "#0f172a", marginBottom: 6 }}>
                One workspace. One business.
              </div>
              <div style={{ color: "#64748b", fontSize: 13, lineHeight: 1.55 }}>
                You can refine this profile for the same business. Changing this workspace to a different
                business or business type requires owner approval, unless Enterprise multi-business access is enabled.
              </div>
              <div style={{ marginTop: 10, color: businessProfileSaved ? "#16a34a" : "#64748b", fontSize: 12.5, fontWeight: 800 }}>
                {businessProfileSaved ? "Saved to execution context" : "Not saved yet"}
              </div>
            </div>
          </div>'''

if target not in text:
    raise SystemExit("BUSINESS_PROFILE_GRID_END_NOT_FOUND")

text = text.replace(target, insert, 1)

PAGE.write_text(text, encoding="utf-8")

print("LOCKED_BUSINESS_PROFILE_SAVE_UI_FIXED")
print(f"Backup: {backup}")