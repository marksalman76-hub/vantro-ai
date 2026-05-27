from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_exact_dark_sections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Remove earlier fragile section-number dark overrides.
s = re.sub(
    r'\n\s*\{/\* TARGETED_DARK_MODE_BLOCKS_1_2_POLISH_V1 \*/\}\s*<style>\{`.*?`\}</style>\s*',
    "\n",
    s,
    flags=re.DOTALL,
)
s = re.sub(
    r'\n\s*\{/\* TARGETED_DARK_MODE_WORKFLOW_INTEGRATION_POLISH_V1 \*/\}\s*<style>\{`.*?`\}</style>\s*',
    "\n",
    s,
    flags=re.DOTALL,
)

# Add stable class names.
s = s.replace(
    '''<section
        style={{
          ...cardStyle,
          padding: "14px 18px",
          marginBottom: 18,
        }}
      >''',
    '''<section
        className="client-integrations-strip"
        style={{
          ...cardStyle,
          padding: "14px 18px",
          marginBottom: 18,
        }}
      >''',
    1,
)

s = s.replace(
    '''<section style={responsiveWorkspaceGridStyle}>''',
    '''<section className="client-run-flow-grid" style={responsiveWorkspaceGridStyle}>''',
    1,
)

# Ensure the final Add integration button is clickable and visually active.
s = s.replace(
    '''whiteSpace: "nowrap",
            }}
          >
            + Add integration''',
    '''whiteSpace: "nowrap",
              position: "relative",
              zIndex: 5,
              pointerEvents: "auto",
            }}
          >
            + Add integration''',
    1,
)

# Add exact class-based dark-mode layer.
style_block = r'''
        {/* EXACT_CLIENT_WORKSPACE_DARK_MODE_SECTIONS_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            .client-integrations-strip,
            .client-run-flow-grid > div {
              background: linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 24px 80px rgba(0,0,0,.34) !important;
            }

            .client-integrations-strip button,
            .client-run-flow-grid div[style*="background: #fff"],
            .client-run-flow-grid div[style*="background: #ffffff"],
            .client-run-flow-grid div[style*="background: rgb(255, 255, 255)"],
            .client-run-flow-grid button[style*="background: #fff"],
            .client-run-flow-grid button[style*="background: #ffffff"],
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

            .client-run-flow-grid textarea::placeholder,
            .client-run-flow-grid input::placeholder {
              color: rgba(203,213,225,.72) !important;
            }

            .client-integrations-strip h2,
            .client-integrations-strip span,
            .client-run-flow-grid h3,
            .client-run-flow-grid strong,
            .client-run-flow-grid [style*="color: var(--color-dark)"],
            .client-run-flow-grid [style*="color: #0f172a"] {
              color: #f8fafc !important;
            }

            .client-integrations-strip p,
            .client-run-flow-grid p,
            .client-run-flow-grid [style*="color: var(--color-muted)"],
            .client-run-flow-grid [style*="color: #64748b"],
            .client-run-flow-grid [style*="color: rgb(100, 116, 139)"] {
              color: #94a3b8 !important;
            }

            .client-integrations-strip button {
              cursor: pointer !important;
              pointer-events: auto !important;
              position: relative !important;
              z-index: 5 !important;
            }

            .client-integrations-strip button span {
              color: inherit !important;
            }
          ` : ``}
        `}</style>
'''

marker = '''        <section
        className="client-integrations-strip"'''

if "EXACT_CLIENT_WORKSPACE_DARK_MODE_SECTIONS_V1" not in s:
    if marker not in s:
        raise SystemExit("FAILED: integration strip marker not found")
    s = s.replace(marker, style_block + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("CLIENT_DARK_MODE_EXACT_SECTIONS_FIXED")
print(f"Backup: {backup}")