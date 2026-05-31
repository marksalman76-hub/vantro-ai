from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_final_inner_rows_integrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Ensure integration strip class exists.
s = s.replace(
    '<section\n        style={{\n          ...cardStyle,\n          padding: "14px 18px",\n          marginBottom: 18,\n        }}\n      >',
    '<section\n        className="client-integrations-strip"\n        style={{\n          ...cardStyle,\n          padding: "14px 18px",\n          marginBottom: 18,\n        }}\n      >',
    1,
)

# Ensure run flow class exists.
s = s.replace(
    '<section style={responsiveWorkspaceGridStyle}>',
    '<section className="client-run-flow-grid" style={responsiveWorkspaceGridStyle}>',
    1,
)

css = r'''
        {/* FINAL_DARK_INNER_ROWS_INTEGRATIONS_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            .client-integrations-strip button {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.28) !important;
              color: #f8fafc !important;
              opacity: 1 !important;
              filter: none !important;
              pointer-events: auto !important;
              cursor: pointer !important;
            }

            .client-integrations-strip button * {
              color: #f8fafc !important;
              opacity: 1 !important;
            }

            .client-integrations-strip button > span:first-child {
              background: rgba(79,70,229,.24) !important;
              color: #c7d2fe !important;
            }

            .client-run-flow-grid > div:nth-child(2) div[style*="background: rgb(255, 255, 255)"],
            .client-run-flow-grid > div:nth-child(2) div[style*="background: #fff"],
            .client-run-flow-grid > div:nth-child(2) div[style*="background: #ffffff"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.28) !important;
              color: #f8fafc !important;
              box-shadow: 0 10px 28px rgba(0,0,0,.22) !important;
            }

            .client-run-flow-grid > div:nth-child(2) div[style*="background: rgb(255, 255, 255)"] *,
            .client-run-flow-grid > div:nth-child(2) div[style*="background: #fff"] *,
            .client-run-flow-grid > div:nth-child(2) div[style*="background: #ffffff"] * {
              color: #f8fafc !important;
            }

            .client-run-flow-grid > div:nth-child(2) [style*="linear-gradient(135deg,#eff6ff,#ffffff)"],
            .client-run-flow-grid > div:nth-child(2) [style*="linear-gradient(135deg,#ffffff"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.28) !important;
              color: #f8fafc !important;
            }
          ` : ``}
        `}</style>
'''

marker = '<section className="client-integrations-strip"'
if "FINAL_DARK_INNER_ROWS_INTEGRATIONS_V1" not in s:
    if marker not in s:
        raise SystemExit("FAILED: integration class marker not found")
    s = s.replace(marker, css + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("FINAL_DARK_INNER_ROWS_INTEGRATIONS_FIXED")
print(f"Backup: {backup}")