from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_dark_uniform_last_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Add the missing 7th clickable integration if the static row still ends at SMS / Phone.
old = '''["sms", "S", "SMS / Phone"],
          ].map(([integrationKey, letter, label]) => ('''

new = '''["sms", "S", "SMS / Phone"],
            ["social", "S", "Social Media"],
          ].map(([integrationKey, letter, label]) => ('''

if old in s:
    s = s.replace(old, new, 1)

# Make integration row columns fit all clickable pills cleanly.
s = s.replace(
    '''gridTemplateColumns: "150px repeat(6, minmax(130px, 1fr)) 155px",''',
    '''gridTemplateColumns: "140px repeat(7, minmax(118px, 1fr)) 145px",'''
)

# Install a targeted dark-mode polish layer for blocks 03/04 and integration row only.
insert = r'''
        {/* TARGETED_DARK_MODE_WORKFLOW_INTEGRATION_POLISH_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            main section:nth-of-type(5),
            main section:nth-of-type(6) {
              background: linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 24px 80px rgba(0,0,0,.34) !important;
            }

            main section:nth-of-type(5) div,
            main section:nth-of-type(6) div,
            main section:nth-of-type(5) p,
            main section:nth-of-type(6) p,
            main section:nth-of-type(5) h3,
            main section:nth-of-type(6) h3 {
              color: inherit;
            }

            main section:nth-of-type(5) [style*="background: #fff"],
            main section:nth-of-type(5) [style*="background: rgb(255, 255, 255)"],
            main section:nth-of-type(6) [style*="background: #fff"],
            main section:nth-of-type(6) [style*="background: rgb(255, 255, 255)"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
            }

            main section:nth-of-type(5) [style*="color: var(--color-dark)"],
            main section:nth-of-type(5) [style*="color: #0f172a"],
            main section:nth-of-type(6) [style*="color: var(--color-dark)"],
            main section:nth-of-type(6) [style*="color: #0f172a"] {
              color: #f8fafc !important;
            }

            main section:nth-of-type(5) [style*="color: var(--color-muted)"],
            main section:nth-of-type(5) [style*="color: #64748b"],
            main section:nth-of-type(6) [style*="color: var(--color-muted)"],
            main section:nth-of-type(6) [style*="color: #64748b"] {
              color: #94a3b8 !important;
            }

            main section:nth-of-type(4) button {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              pointer-events: auto !important;
            }

            main section:nth-of-type(4) button span,
            main section:nth-of-type(4) button div {
              color: inherit !important;
            }
          ` : ``}
        `}</style>
'''

marker = '''        <section
        style={{
          ...cardStyle,
          padding: "14px 18px",
          marginBottom: 18,
        }}
      >'''

if "TARGETED_DARK_MODE_WORKFLOW_INTEGRATION_POLISH_V1" not in s:
    if marker not in s:
        raise SystemExit("FAILED: integrations section marker not found")
    s = s.replace(marker, insert + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("DARK_UNIFORM_AND_LAST_INTEGRATION_PILL_FIXED")
print(f"Backup: {backup}")