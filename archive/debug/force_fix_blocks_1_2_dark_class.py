from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_force_blocks_1_2_dark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Force class onto the section that contains Step 01 and Step 02.
pattern = r'<section\s+style=\{responsiveWorkspaceGridStyle\}>'
if re.search(pattern, s):
    s = re.sub(pattern, '<section className="client-run-flow-grid" style={responsiveWorkspaceGridStyle}>', s, count=1)
else:
    raise SystemExit("FAILED: responsiveWorkspaceGridStyle section not found")

# Add direct class CSS if missing.
css = r'''
        {/* FORCE_BLOCKS_1_2_DARK_MODE_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            .client-run-flow-grid > div {
              background: linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 24px 80px rgba(0,0,0,.34) !important;
            }

            .client-run-flow-grid div,
            .client-run-flow-grid p,
            .client-run-flow-grid h3,
            .client-run-flow-grid span {
              color: inherit;
            }

            .client-run-flow-grid div[style*="background: #fff"],
            .client-run-flow-grid div[style*="background: #ffffff"],
            .client-run-flow-grid button[style*="background: #fff"],
            .client-run-flow-grid button[style*="background: #ffffff"],
            .client-run-flow-grid div[style*="linear-gradient(135deg,#eff6ff,#ffffff)"],
            .client-run-flow-grid div[style*="linear-gradient(135deg,#ffffff"],
            .client-run-flow-grid button[style*="linear-gradient(135deg,#eff6ff,#ffffff)"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 12px 32px rgba(0,0,0,.22) !important;
            }

            .client-run-flow-grid textarea,
            .client-run-flow-grid input {
              background: rgba(3,10,24,.88) !important;
              border-color: rgba(129,140,248,.34) !important;
              color: #f8fafc !important;
            }

            .client-run-flow-grid [style*="color: var(--color-dark)"],
            .client-run-flow-grid [style*="color: #0f172a"] {
              color: #f8fafc !important;
            }

            .client-run-flow-grid [style*="color: var(--color-muted)"],
            .client-run-flow-grid [style*="color: #64748b"] {
              color: #94a3b8 !important;
            }
          ` : ``}
        `}</style>
'''

marker = '<section className="client-run-flow-grid" style={responsiveWorkspaceGridStyle}>'
if "FORCE_BLOCKS_1_2_DARK_MODE_V1" not in s:
    s = s.replace(marker, css + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("FORCE_BLOCKS_1_2_DARK_CLASS_FIXED")
print(f"Backup: {backup}")