from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_pipeline_integrations_dark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

css = r'''
        {/* PIPELINE_ROWS_AND_INTEGRATION_PILLS_DARK_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            .client-integrations-strip button {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.28) !important;
              color: #f8fafc !important;
              box-shadow: 0 12px 32px rgba(0,0,0,.22) !important;
              opacity: 1 !important;
              filter: none !important;
              cursor: pointer !important;
              pointer-events: auto !important;
            }

            .client-integrations-strip button span {
              color: #f8fafc !important;
              opacity: 1 !important;
            }

            .client-integrations-strip button span span {
              color: #cbd5e1 !important;
            }

            .client-integrations-strip button > span:first-child {
              background: rgba(79,70,229,.24) !important;
              color: #c7d2fe !important;
            }

            .client-run-flow-grid > div:nth-child(2) > div[style*="display: grid"] > div > div[style*="border"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.28) !important;
              color: #f8fafc !important;
              box-shadow: 0 10px 28px rgba(0,0,0,.22) !important;
            }

            .client-run-flow-grid > div:nth-child(2) > div[style*="display: grid"] > div > div[style*="border"] div {
              color: #f8fafc !important;
            }

            .client-run-flow-grid > div:nth-child(2) > div[style*="display: grid"] > div > div[style*="border"] div:nth-child(2) {
              color: #94a3b8 !important;
            }

            .client-run-flow-grid > div:nth-child(2) [style*="linear-gradient(135deg,#eff6ff,#ffffff)"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.28) !important;
              color: #f8fafc !important;
            }

            .client-run-flow-grid > div:nth-child(2) [style*="linear-gradient(135deg,#eff6ff,#ffffff)"] div {
              color: #f8fafc !important;
            }
          ` : ``}
        `}</style>
'''

marker = '''        <section className="client-run-flow-grid" style={responsiveWorkspaceGridStyle}>'''

if "PIPELINE_ROWS_AND_INTEGRATION_PILLS_DARK_V1" not in s:
    if marker not in s:
        raise SystemExit("FAILED: run flow grid marker not found")
    s = s.replace(marker, css + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("PIPELINE_ROWS_AND_INTEGRATION_PILLS_DARK_FIXED")
print(f"Backup: {backup}")