from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass17_responsive_motion_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# Add responsive helper marker only through CSS-safe style improvements.
# No window.innerWidth, no runtime logic change.

text = text.replace(
    'boxShadow: "0 20px 55px rgba(15,23,42,0.06)"',
    'boxShadow: "0 20px 55px rgba(15,23,42,0.06)",\n                      transition: "transform 0.18s ease, box-shadow 0.18s ease"'
)

text = text.replace(
    'cursor: "pointer",\n                    boxShadow: "0 5px 18px rgba(15,23,42,0.035)"',
    'cursor: "pointer",\n                    transition: "transform 0.16s ease, box-shadow 0.16s ease",\n                    boxShadow: "0 5px 18px rgba(15,23,42,0.035)"'
)

text = text.replace(
    'cursor: "pointer",\n                          textAlign: "left"',
    'cursor: "pointer",\n                          transition: "transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease",\n                          textAlign: "left"'
)

text = text.replace(
    'cursor: "pointer",\n                    }}\n                  >\n                    {reviewActionLoading ? "Saving..." : "👍 Approve"}',
    'cursor: "pointer",\n                      transition: "transform 0.16s ease, box-shadow 0.16s ease",\n                      boxShadow: "0 8px 20px rgba(34,197,94,0.16)",\n                    }}\n                  >\n                    {reviewActionLoading ? "Saving..." : "👍 Approve"}'
)

text = text.replace(
    'cursor: reviewActionLoading ? "not-allowed" : "pointer",\n                    }}\n                  >\n                    👎 Reject',
    'cursor: reviewActionLoading ? "not-allowed" : "pointer",\n                      transition: "transform 0.16s ease, border-color 0.16s ease",\n                    }}\n                  >\n                    👎 Reject'
)

# Add safe responsive CSS block using plain style tag in JSX.
# This does not change server/client render branches.
style_marker = "/* client_portal_responsive_motion_css */"

if style_marker not in text:
    insert_after = '<main style={shellStyle}>'
    responsive_css = r'''
        <style>{`
          /* client_portal_responsive_motion_css */
          @media (max-width: 1180px) {
            section[style*="repeat(2, minmax(0, 1fr))"] {
              grid-template-columns: 1fr !important;
            }
          }

          @media (max-width: 760px) {
            textarea {
              min-height: 96px !important;
            }

            button {
              max-width: 100%;
            }
          }
        `}</style>
'''
    text = text.replace(insert_after, insert_after + responsive_css, 1)

if "client_portal_responsive_motion_locked" not in text:
    text = text.replace(
        "// client_portal_activity_premium_polish_locked",
        "// client_portal_activity_premium_polish_locked\n// client_portal_responsive_motion_locked"
    )

if text == original:
    raise RuntimeError("No Pass 17 responsive/motion changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass17_responsive_motion.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS17_RESPONSIVE_MOTION_RESULTS")

checks = {
    "marker": "client_portal_responsive_motion_locked" in text,
    "responsive_css": "client_portal_responsive_motion_css" in text,
    "media_1180": "@media (max-width: 1180px)" in text,
    "media_760": "@media (max-width: 760px)" in text,
    "transition": "transition:" in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS17_RESPONSIVE_MOTION_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS17_RESPONSIVE_MOTION_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")