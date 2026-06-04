from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_header_creative_assets_button_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(ADMIN_PAGE, BACKUP / "page.tsx")

text = ADMIN_PAGE.read_text(encoding="utf-8", errors="ignore")

if 'href="/admin/creative-assets"' not in text:
    marker = '<h1>AI Workforce Platform</h1>'
    insert = '''<div style={{ marginTop: "14px", marginBottom: "14px" }}>
              <a
                href="/admin/creative-assets"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "10px 14px",
                  borderRadius: "12px",
                  border: "1px solid rgba(34,211,238,.35)",
                  background: "rgba(8,145,178,.14)",
                  color: "#a5f3fc",
                  fontWeight: 900,
                  textDecoration: "none"
                }}
              >
                Creative Assets
              </a>
            </div>'''

    if marker not in text:
        raise RuntimeError("Could not find admin page header marker")

    text = text.replace(marker, marker + "\n            " + insert, 1)

ADMIN_PAGE.write_text(text, encoding="utf-8", newline="\n")

print("ADMIN_HEADER_CREATIVE_ASSETS_BUTTON_PATCHED")
print(f"Backup: {BACKUP}")
print(f"Updated: {ADMIN_PAGE}")