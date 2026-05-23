from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUP_DIR / f"client_page_before_visible_profile_save_button_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Remove any previous save button block to avoid duplicates.
text = re.sub(
    r'\s*<button\s+type="button"\s+onClick=\{saveBusinessProfile\}[\s\S]*?</button>',
    '',
    text,
    count=1
)

# Insert visible save button directly after the business profile grid.
target = '''            ))}
          </div>

          <section'''

button_block = '''            ))}
          </div>

          <div style={{
            marginTop: 22,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 14,
            flexWrap: "wrap"
          }}>
            <button
              type="button"
              onClick={saveBusinessProfile}
              style={{
                border: 0,
                borderRadius: 14,
                padding: "14px 24px",
                background: "var(--color-blue)",
                color: "white",
                fontWeight: 900,
                cursor: "pointer",
                boxShadow: "0 18px 45px rgba(79, 70, 229, 0.22)"
              }}
            >
              Save business profile
            </button>
            <span style={{ color: "var(--color-muted)", fontSize: 13, fontWeight: 700 }}>
              {businessProfileSaved ? "Saved to execution context" : "Save once to apply this context to future AI runs"}
            </span>
          </div>

          <section'''

if target not in text:
    raise SystemExit("BUSINESS_PROFILE_GRID_END_TARGET_NOT_FOUND")

text = text.replace(target, button_block, 1)

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_PROFILE_SAVE_BUTTON_VISIBLE_FIXED")
print(f"Backup: {backup}")